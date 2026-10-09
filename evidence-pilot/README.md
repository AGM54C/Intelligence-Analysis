# 图文证据修订实验代码

固定最终有效图文证据，改变早期信息历史，比较模型是否受到旧解释影响。实现包含四个可重复生成的合成场景、三种基线、四类对照和本地 Transformers 推理入口。

[实验协议](../experiments/01-图文证据修订先导/experiment-protocol.md)定义比较条件；[数据契约](../experiments/data/image-text-pilot/data-contract.md)定义输入与评估信息的边界。合成样例不代表真实事件或正式诊断基准，构造标签未经独立标注者复核。

## 方法与约束

| 方法或组件 | 行为 |
|---|---|
| A：单解释更新 | 继承最多一个解释，依据当前材料重新判断 |
| B：全量重启 | 每个阶段独立请求，可比较最多四个解释，不继承状态 |
| C：普通多假设维护 | 继承最多四个候选，新增最多四个，选择最多四个；淘汰记录不反馈给后续阶段 |
| 图文输入 | 直接传入图片，固定顺序与像素预算 |
| 对照 | 去图、人工视觉事实、后到错误报道、视觉关系变体 |
| 信息隔离 | 公共字段白名单、分阶段证据；gold 仅供评估器读取 |
| 输入检查 | 比较两条历史的最终有效材料、B 的最终请求、种子与处理器张量 |
| 运行记录 | 保存输入哈希、原始输出、用量、格式失败及截断；显式续跑 |

非法输出与截断不自动重试，后续阶段沿用该轨迹最近的有效状态。运行异常会停止；未完成的在途调用不会自动再次执行。引用存在不等于依据充分，合理解释的生成、保留与应用仍需语义核查。

## 安装与运行

Python 3.10+。从仓库根目录进入 `evidence-pilot/`：

```bash
cd evidence-pilot
python -m pip install -e .
python -m unittest discover -s tests -v
python -m evidence_pilot validate --data ../experiments/data/image-text-pilot
python -m evidence_pilot run --data ../experiments/data/image-text-pilot --config configs/development.json --backend dry-run --suite all --output ../experiments/results/example
python -m evidence_pilot evaluate --run ../experiments/results/example --data ../experiments/data/image-text-pilot
```

完整四例运行包含 96 次逻辑请求：72 次核心请求和 4+4+12+4 次对照。`dry-run` 不加载模型，准确率字段为 `null`，仅用于验证运行流程。

输出目录必须是新目录。`--resume` 允许续跑，但配置、数据、代码或后端变化时拒绝续接。`--max-calls 1` 限制调用数，`--runtime-minutes 15` 限制执行会话的时间；配置中的 `budget.max_runtime_hours` 限制累计运行时间。时间预算在调用之间检查，单次生成另受 `max_generation_seconds` 约束，程序不会关闭 GPU 实例。

图片已随样例提供。也可以在空目录中重新生成：

```bash
python -m evidence_pilot build-dev --data ../experiments/results/generated-fixtures
```

## Transformers 图文推理

配置以 `Qwen/Qwen3.5-9B`、BF16、单卡、batch=1 为示例。完整权重在 A100 上的显存、速度与任务成绩没有实测结果，需要根据实际环境验证。先安装与 CUDA 驱动兼容的 PyTorch，再安装固定依赖：

```bash
python -m pip install -e . -r requirements-gpu.txt
```

从[官方模型仓库](https://huggingface.co/Qwen/Qwen3.5-9B)或 [ModelScope](https://modelscope.cn/models/Qwen/Qwen3.5-9B)取得完整模型快照。程序仅读取本地文件，不自动下载权重，并对实际模型文件计算哈希。

```bash
python -m evidence_pilot run --data ../experiments/data/image-text-pilot --config configs/development.json --backend transformers --model-path /data/models/Qwen3.5-9B --suite smoke --cases D001 --output ../experiments/results/model-smoke
```

`smoke` 对指定案例运行 B 的完整证据输入；`core` 执行两条历史的 A/B/C 比较；`all` 增加四类对照。默认配置开启 thinking，总上下文 16K，输入上限 8K（含图像），生成上限 8K，最多四图。超出输入或状态限制会报错，不静默截断证据。生成因长度或时间限制未正常结束时记录为 `truncated`。

正式诊断数据运行要求配置中的 `ready_for_model_execution`、`runtime.frozen`、`data.manifest_frozen` 为真，并满足数据验证规则。该开关不替代数据准入与标注审查。官方完整权重的推理、自动候选恢复、GNN、开放搜索和真实事件题包不包含在现有验证结果中。

## 输出与评估

| 文件 | 内容 |
|---|---|
| `run.json` | 代码、数据、模型身份，环境，任务集合和运行状态 |
| `requests/*.json` | 实际公共输入、候选状态、图片哈希，不含 gold |
| `records.jsonl` | 原始输出、解析结果、错误、token、时间与显存字段 |
| `evaluation/` | 计数、成对输入比较、成对结果及人工审查格式 |

使用实际模型输出，并对证据与候选作人工核查后，可传入独立审查文件：

```bash
python -m evidence_pilot evaluate --run ../experiments/results/model-smoke --data ../experiments/data/image-text-pilot --reviews reviewed.jsonl
```

未核查的依据正确性与候选合理性保持 `null`。GPU 生成用时不等于租赁时长；成本分析还需计入模型加载、图像编码、额外判断和失败调用。
