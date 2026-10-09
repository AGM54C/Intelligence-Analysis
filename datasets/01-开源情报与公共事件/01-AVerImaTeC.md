# AVerImaTeC

| 项目 | 说明 |
|---|---|
| 类型 | 图文事实核验基准；自然网络断言与证据 |
| 模态与标签 | 图片、断言、问答证据、核验裁决；需逐例确认视觉证据是否充分 |
| 获取状态 | 官方文件目录提供标注与图片 ZIP；原始数据不随本仓库分发 |

## 下载与来源

- [项目官网](https://fever.ai/dataset/averimatec.html)、[作者仓库](https://github.com/abril4416/AVerImaTeC)。
- [Hugging Face 完整目录](https://huggingface.co/datasets/Rui4416/AVerImaTeC/tree/main)。目录列出 `train.json`、`val.json`、`images.zip`、`test_data.zip`。
- [训练标注](https://huggingface.co/datasets/Rui4416/AVerImaTeC/resolve/main/train.json)、[验证标注](https://huggingface.co/datasets/Rui4416/AVerImaTeC/resolve/main/val.json)、[图片包](https://huggingface.co/datasets/Rui4416/AVerImaTeC/resolve/main/images.zip)。

## 可用于什么

优先检查的图文证据资源，可用于核验、证据检索和依据解释，也可作为以后构建证据修订案例的取材入口。论文已有动态提问与更新证据历史的设置，不能将“多轮查证”本身视为我们的创新。

现有标签不自动提供证据撤回、假设淘汰与恢复的逐轮标注。共享任务知识库含标注证据及由标注问答辅助生成的检索材料，不能直接当成未知事件的无泄漏开放搜索环境。公开断言、核查结论和 gold 问答需要分离。

## 使用条件与限制

官方目录列出 `train.json`、`val.json`、`images.zip` 和 `test_data.zip`；数据卡中的图片文件名与测试集说明可能滞后，使用时固定文件版本并单独确认测试答案的公开范围。目录信息不代表样本与图片已逐项验证。共享任务论文声明数据集及基线采用 CC-BY-NC-4.0，原始图片权利另行适用。
