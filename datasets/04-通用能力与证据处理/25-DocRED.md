# DocRED

| 项目 | 说明 |
|---|---|
| 类型 | 文档级实体关系抽取基准 |
| 模态与标签 | 文本、实体提及、关系、证据句；含人工标注及远程监督数据 |
| 获取状态 | 官方 data README 提供 Google Drive 下载目录 |

## 下载与来源

- [作者仓库](https://github.com/thunlp/DocRED)、[数据格式说明](https://github.com/thunlp/DocRED/blob/master/data/README.md)。
- [官方 Google Drive 数据目录](https://drive.google.com/drive/folders/1c5-0YwnoJx8NS6CV2f-NoTHR__BdkNqw?usp=sharing)。测试提交规则以作者说明及竞赛入口为准，不假定公开训练标签覆盖测试集。

## 可用于什么

可作为文本到人物/组织/事件关系图的基础能力资源，检查跨句实体对齐和证据句选择。`vertexSet` 给实体提及，`labels` 中的 h/t/r 与 evidence 连接关系和支撑句。

关系抽取判断“文本说了什么”，不保证文本所说在现实中为真。未标注关系也不能一律当成已证明不存在的边。数据主要来自 Wikipedia/Wikidata，不是警务案卷或自然图文情报，适合评估建图模块而非替代整体任务。

## 使用条件与限制

官方 data README 提供下载目录及格式。使用应结合项目声明与 Wikipedia、Wikidata 原始内容的条件，不推定全部衍生文件具有统一许可；关系抽取标签不等于关系已被独立核实。
