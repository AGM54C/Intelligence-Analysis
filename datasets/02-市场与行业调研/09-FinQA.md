# FinQA

| 项目 | 说明 |
|---|---|
| 类型 | 财报数值推理问答基准 |
| 模态与标签 | 解析后的文本与表格；问题、答案、计算程序、证据 |
| 获取状态 | 官方 JSON 文件目录目录列出 |

## 下载与来源

- [作者仓库](https://github.com/czyssrs/FinQA)、[数据目录](https://github.com/czyssrs/FinQA/tree/main/dataset)。
- [训练集](https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/train.json)、[开发集](https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/dev.json)、[公开测试集](https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/test.json)。另有 `private_test.json`，不应假设它含 gold。

## 可用于什么

财报跨文本/表格计算的能力对照，可检查企业指标比较、单位与口径转换。显式程序和依据便于核查“算对了但引用错了”的输出。

这是给定材料的数值 QA，不是包含假新闻的行业情报。解析表格不等于文档图像；若将表格渲染成图片，应注明受控转换，不能称原生视觉财报。`qa` 中的答案、程序与 gold evidence 不能混入模型输入。作者 README 提及早期预处理泄漏问题，复现时需固定修正后的版本。

## 使用条件与限制

官方仓库提供 JSON 数据。项目声明与原财报内容的许可需分别核对，不能推定全部原始财报具有统一授权。解析表格不等于原生文档页图。
