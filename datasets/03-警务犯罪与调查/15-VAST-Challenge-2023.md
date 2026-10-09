# VAST Challenge 2023

| 项目 | 说明 |
|---|---|
| 类型 | 可视分析竞赛；非法捕捞调查的虚构场景 |
| 模态与标签 | 新闻抽取关系图、贸易/业务关系、时序数据；以调查问题和分析报告为主 |
| 获取状态 | 通过官方表单获取；机器评分 gold 的公开范围未确认 |

## 获取入口

- [挑战总览](https://vast-challenge.github.io/2023/overview.html)。
- [MC1：实体与关系上下文](https://vast-challenge.github.io/2023/MC1.html)、[MC2：贸易模式与候选链接](https://vast-challenge.github.io/2023/MC2.html)、[MC3：公司结构异常](https://vast-challenge.github.io/2023/MC3.html)、[Grand Challenge：竞争叙事](https://vast-challenge.github.io/2023/GC.html)。
- MC1 的[官方数据获取表单](https://docs.google.com/forms/d/e/1FAIpQLSe7wv93AtKVnZaJOw_1tBzM63FrU6GjT6VH5GsXP2a-kTi8uw/viewform)嵌于任务页面，MC2 等有各自表单。未提交信息或申请下载。

## 可用于什么

与情报研究关系很近：MC1 要在有噪声、重复关系的图中理解线索；MC2 要评估模型提出的链接补全是否可靠；总挑战要求解释不同数据源产生的竞争叙事。可借鉴其调查问题，并研究“直接 GNN 核查”究竟解决哪些环节。

节点连线是结构化图，不等于照片与文本两种感知模态。图异常或连接到可疑实体也不是定罪标签。竞赛提交以分析报告为主，公开标准答案、评分方式及数据许可尚需核实，不能直接宣布它是可自动评分的推理基准。

## 使用条件与限制

官方页面提供数据获取表单，机器可评分 gold 的公开范围未确认。场景人物、地点等为虚构，部分任务说明还涉及由新闻整理的图噪声，应按下载包定义解释；该资源不是真实警方案卷。使用许可以官方获取条款为准。
