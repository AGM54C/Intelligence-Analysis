# TAT-DQA

| 项目 | 说明 |
|---|---|
| 类型 | 视觉丰富金融文档的数值推理问答 |
| 模态与标签 | 财报文档页面、文字/表格与布局、问题和数值答案 |
| 获取状态 | 官方提供 Google Drive 数据目录 |

## 下载与来源

- [作者仓库](https://github.com/NExTplusplus/TAT-DQA)、[项目主页](https://nextplusplus.github.io/TAT-DQA/)。
- [官方数据下载目录](https://drive.google.com/drive/folders/1SGpZyRWqycMd_dZim1ygvWhl5KdJYDR2)。README 说明测试答案已于 2024 年公布。

## 可用于什么

市场/行业方向优先考察的视觉文档资源，比只提供解析表格的数据更接近“读财报页面并核对结论”。可用于评估页面理解、跨表文证据连接和计算。

它基于 [TAT-QA](10-TAT-QA.md) 扩展，两者具有来源重合。正式拆分应按原报告/公司/时期检查同源性，不能仅按题目 ID 随机切分。文档 QA 仍缺自然错误信息、报告修订史和多假设随证据变化的标签；需要另建任务层。

## 使用条件与限制

作者提供 Google Drive 数据目录，README 声明 CC BY 4.0；页面素材原始权利同时适用。完整页图覆盖和样本对齐需按固定版本检查，与 TAT-QA 的同源关系应纳入数据划分。
