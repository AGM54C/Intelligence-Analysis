# Intelligence Analysis：不可靠图文证据下的动态事件推理

研究真假混合、来源相关且会被修订的图文材料：模型如何判断当前证据支持什么，如何保留替代解释，以及早期错误依据被纠正后，如何重新评价曾被放弃的候选。

[研究概述](情报分析.md)介绍背景、相关工作、研究问题与方法设想。本仓库提供文献分析、25 项公开数据资源目录、数据设计规范，以及可运行的受控图文实验代码。

## 内容

| 路径 | 内容 |
|---|---|
| [情报分析.md](情报分析.md) | 研究背景、四类相关工作、研究问题和适用边界 |
| [related work](<related work/README.md>) | 十一篇代表论文、论文笔记及方法比较 |
| [datasets](datasets/README.md) | 公开数据集与开放资源的入口、模态、标签、用途和使用条件 |
| [docs](docs/README.md) | 自建数据集约束、多领域设计、案例与失败分析规范 |
| [候选 IDEA 集合](候选IDEA集合/README.md) | 来源调查、动态多假设进化、证据修订与候选恢复 |
| [experiments](experiments/README.md) | 受控实验协议、输入契约和四个合成图文样例 |
| [evidence-pilot](evidence-pilot/README.md) | Python 实现、配置、测试及 Transformers 推理入口 |

## 运行示例

Python 3.10+，基础依赖为 Pillow。在仓库根目录执行：

```bash
python -m pip install -e ./evidence-pilot
python -m evidence_pilot validate --data experiments/data/image-text-pilot
python -m evidence_pilot run --data experiments/data/image-text-pilot --config evidence-pilot/configs/development.json --backend dry-run --suite all --output experiments/results/example
python -m evidence_pilot evaluate --run experiments/results/example --data experiments/data/image-text-pilot
```

完整示例包含 96 次逻辑请求。`dry-run` 只验证输入、状态更新和评估流程，不加载模型，不产生方法准确率。输出目录需要是新目录；续跑、模型安装和真实推理参数见[代码说明](evidence-pilot/README.md)。

## 研究范围

四个图文样例是可重复生成的合成场景，用于检验代码与受控协议，不是真实事件基准。实验实现包含单解释更新、全量重启、普通多假设维护及视觉/后到错误材料对照；候选恢复、GNN 和主动检索属于研究设计，不包含在现有基线实现中。仓库不提供官方完整模型权重的性能结果。

正式自建数据要求事件严格晚于所选模型**有依据的知识截止日期**，每例真假混合、比例跨案例变化、材料逐步公开，并具有真实的图文互补性。旧公开资源与合成样例不自动满足这些条件。完整要求见[数据集设计约束](docs/自建数据集设计约束.md)。

## 使用许可

项目代码及原创文本遵循 [MIT License](LICENSE)。引用的论文、外部数据和原始图像遵循各自的权利与使用条件；数据资源目录列出官方获取入口，不包含第三方原始数据包。
