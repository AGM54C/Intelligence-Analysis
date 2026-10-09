# TAT-QA

| 项目 | 说明 |
|---|---|
| 类型 | 金融表格与文本联合问答 |
| 模态与标签 | 结构化表格、段落、问题、答案及推理相关标注 |
| 获取状态 | 官方数据文件公开；测试 gold 已在 2024 年公布 |

## 下载与来源

- [官方仓库](https://github.com/NExTplusplus/TAT-QA)、[dataset_raw 目录](https://github.com/NExTplusplus/TAT-QA/tree/master/dataset_raw)。
- [训练集](https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_train.json)、[开发集](https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_dev.json)。
- [测试问题](https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_test.json)、[测试 gold](https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_test_gold.json)。

## 可用于什么

检验企业分析中的表文对齐、指标选择和数值推导，适合行业研究的基础能力对照。原任务提供答案与推理依据，而非让研究者事后猜测正确指标。

表格与文字均主要是解析形式，不自带原始页面视觉任务；也没有“某条证据为假、随后被撤回”的自然更新链。[TAT-DQA](11-TAT-DQA.md)由它扩展而来，不能将两个数据集随机划分后视为独立训练和测试来源。

## 使用条件与限制

作者 README 声明 CC BY 4.0；原始财报页面的再分发范围另行核对。官方目录包含 train/dev/test/test_gold，评估标签应与模型输入隔离。
