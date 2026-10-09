from __future__ import annotations

import importlib.metadata
import importlib.util
import time
from dataclasses import dataclass, field
from pathlib import Path

from .common import ProtocolError, canonical, digest, file_hash
from .prompting import Request


@dataclass
class Completion:
    raw_output: str
    finish_reason: str
    usage: dict = field(default_factory=dict)
    processed_input_hash: str | None = None


def configure_processor(processor, config: dict) -> dict:
    image_config = config["runtime"].get("image_processor_configuration")
    if not image_config or not {"min_pixels", "max_pixels"} <= image_config.keys():
        raise ProtocolError("Set explicit min_pixels/max_pixels before running the model")
    image_processor = processor.image_processor
    if not hasattr(image_processor, "size"):
        raise ProtocolError("Processor has no inspectable pixel budget; check the installed Transformers version")
    image_processor.size = {"shortest_edge": image_config["min_pixels"], "longest_edge": image_config["max_pixels"]}
    return image_processor.to_dict()


def prepare_inputs(processor, request: Request, config: dict):
    """One path for the real backend and the no-weights processor integration probe."""
    from PIL import Image
    content = [{"type": "text", "text": canonical(request.payload)}]
    images = []
    for asset in request.assets:
        content.append({"type": "text", "text": f"图片 {asset['image_id']}："})
        content.append({"type": "image"})
        with Image.open(asset["path"]) as opened:
            images.append(opened.convert("RGB"))
    messages = [{"role": "system", "content": request.system}, {"role": "user", "content": content}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                          enable_thinking=config["generation"]["enable_thinking"])
    inputs = processor(text=[text], images=images or None, return_tensors="pt", padding=True)
    input_tokens = int(inputs["input_ids"].shape[-1])
    state_tokens = len(processor.tokenizer.encode(canonical(request.payload["previous_state"]), add_special_tokens=False))
    runtime = config["runtime"]
    if state_tokens > config["state"]["maximum_visible_state_tokens"]:
        raise ProtocolError("Inherited state exceeds token cap; no silent state truncation")
    if len(images) > runtime["max_images_per_request"] or input_tokens > runtime["max_input_tokens_including_vision"]:
        raise ProtocolError("Input exceeds frozen image/token limit; no silent input truncation")
    if input_tokens + runtime["max_new_tokens_including_thinking"] > runtime["context_tokens"]:
        raise ProtocolError("Input plus output budget exceeds context cap")
    return inputs, {"input_tokens": input_tokens, "state_tokens": state_tokens, "image_count": len(images)}


class DryRunBackend:
    name = "dry-run"
    execution_kind = "DRY_RUN"

    def identity(self) -> dict:
        return {"backend": self.name, "execution_kind": self.execution_kind, "model_loaded": False}

    def generate(self, request: Request) -> Completion:
        # Explicit empty fixture; no prediction, oracle, image captioning, or hidden gold.
        discarded = [{"hypothesis_id": h["id"], "reason_kind": "other", "reason_evidence_ids": [],
                      "brief_reason": "仅检查接口，未执行模型推理。"} for h in request.payload["previous_state"]]
        output = {"hypotheses": [], "selected_ids": [], "discard_records": discarded,
                  "verdict": "insufficient", "support_ids": [], "conflict_ids": [],
                  "brief_justification": "DRY_RUN：仅校验请求和日志，不是模型答案。"}
        return Completion(canonical(output), "dry_run", {"input_tokens": None, "output_tokens": None,
                          "visual_tokens": None, "gpu_seconds": None, "peak_allocated_bytes": None})


def snapshot_identity(path: Path) -> dict:
    """Hash the actual local snapshot, including weight shards; no network access."""
    files = sorted(p for p in path.rglob("*") if p.is_file() and p.suffix in {".json", ".safetensors", ".bin", ".model", ".tiktoken", ".jinja", ".txt"})
    if not (path / "config.json").is_file() or not any(p.suffix in {".safetensors", ".bin"} for p in files):
        raise ProtocolError("Local model snapshot needs config.json and weight files")
    entries = {p.relative_to(path).as_posix(): {"bytes": p.stat().st_size, "sha256": file_hash(p)} for p in files}
    return {"snapshot_sha256": digest(entries), "files": entries}


class TransformersBackend:
    name = "transformers"
    execution_kind = "MODEL_INFERENCE"

    def __init__(self, config: dict, model_path: Path):
        # Imports remain optional for local data preparation and tests.
        import torch
        import transformers
        from transformers import AutoConfig, AutoModelForImageTextToText, AutoProcessor
        if not torch.cuda.is_available():
            raise ProtocolError("CUDA GPU is required for this backend; CPU fallback is disabled")
        if not torch.cuda.is_bf16_supported():
            raise ProtocolError("The frozen BF16 setting requires BF16-capable CUDA hardware")
        if not model_path.is_dir():
            raise ProtocolError("--model-path must point to an existing local snapshot")
        if config["generation"].get("presence_penalty", 0) != 0:
            raise ProtocolError("This HF backend does not implement presence_penalty; cannot silently ignore it")
        self.config, self.torch, self.transformers = config, torch, transformers
        print("Hashing local model snapshot (including weight shards)...", flush=True)
        self.snapshot = snapshot_identity(model_path)
        model_config = AutoConfig.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=False)
        if model_config.model_type not in {"qwen3_5", "qwen3_vl"}:
            raise ProtocolError(f"Unsupported model type: {model_config.model_type}; no automatic model substitution")
        self.processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=False)
        self.processor_config = configure_processor(self.processor, config)
        self.model = AutoModelForImageTextToText.from_pretrained(
            str(model_path), dtype=torch.bfloat16, device_map={"": 0},
            attn_implementation="sdpa", local_files_only=True, trust_remote_code=False,
        ).eval()
        self.model_config = model_config
        self.processor_hash = digest(self.processor_config)
        torch.backends.cudnn.benchmark = False

    def identity(self) -> dict:
        versions = {}
        for package in ("torch", "torchvision", "transformers", "accelerate", "Pillow", "numpy"):
            try:
                versions[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                versions[package] = None
        return {
            "backend": self.name, "execution_kind": self.execution_kind, "versions": versions,
            "snapshot": self.snapshot, "model_type": self.model_config.model_type,
            "processor_hash": self.processor_hash, "image_processor": self.processor_config,
            "gpu": self.torch.cuda.get_device_name(0), "cuda_version": self.torch.version.cuda,
            "attention": "sdpa", "bitwise_determinism_guaranteed": False,
            "optional_linear_attention_kernels": {name: importlib.util.find_spec(name) is not None for name in ("causal_conv1d", "fla")},
        }

    def generate(self, request: Request) -> Completion:
        import hashlib
        torch, runtime, generation = self.torch, self.config["runtime"], self.config["generation"]
        self.transformers.set_seed(request.seed)
        started = time.perf_counter()
        inputs, token_info = prepare_inputs(self.processor, request, self.config)
        input_tokens, state_tokens = token_info["input_tokens"], token_info["state_tokens"]
        tensor_hash = hashlib.sha256()
        tensor_hash.update(canonical({"processor": self.processor_hash, "seed": request.seed, "generation": generation}).encode())
        for name, tensor in sorted(inputs.items()):
            tensor_hash.update(canonical({"name": name, "shape": list(tensor.shape), "dtype": str(tensor.dtype)}).encode())
            tensor_hash.update(tensor.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
        visual_token_id = getattr(self.model_config, "image_token_id", None)
        visual_tokens = int((inputs["input_ids"] == visual_token_id).sum()) if visual_token_id is not None else None
        inputs = inputs.to(self.model.device)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        gpu_start = time.perf_counter()
        with torch.inference_mode():
            generated = self.model.generate(
                **inputs, do_sample=True, temperature=generation["temperature"], top_p=generation["top_p"],
                top_k=generation["top_k"], min_p=generation.get("min_p", 0.0),
                repetition_penalty=generation.get("repetition_penalty", 1.0),
                max_new_tokens=runtime["max_new_tokens_including_thinking"],
                max_time=runtime.get("max_generation_seconds", 300),
            )
        torch.cuda.synchronize()
        gpu_seconds = time.perf_counter() - gpu_start
        ids = generated[0, input_tokens:]
        eos_ids = self.model.generation_config.eos_token_id
        eos_ids = eos_ids if isinstance(eos_ids, list) else [eos_ids]
        finished = bool(ids.numel()) and int(ids[-1]) in eos_ids
        raw = self.processor.tokenizer.decode(ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        return Completion(raw, "eos" if finished else "length_or_time_limit", {
            "input_tokens": input_tokens, "output_tokens": int(ids.numel()), "visual_tokens": visual_tokens,
            "state_tokens": state_tokens, "gpu_seconds": gpu_seconds, "processing_and_generation_seconds": time.perf_counter() - started,
            "peak_allocated_bytes": int(torch.cuda.max_memory_allocated()),
            "peak_reserved_bytes": int(torch.cuda.max_memory_reserved()),
            "generation_limit_seconds": runtime.get("max_generation_seconds", 300),
        }, tensor_hash.hexdigest())
