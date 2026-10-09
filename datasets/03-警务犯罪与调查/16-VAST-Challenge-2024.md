# VAST Challenge 2024

| 项目 | 说明 |
|---|---|
| 类型 | 合成调查场景的可视分析竞赛 |
| 模态与标签 | 原始文章、模型抽取及人工修改后的知识图谱、船舶轨迹与业务关系 |
| 获取状态 | 通过官方表单获取；机器评分 gold 的公开范围未确认 |

## 获取入口

- [总览](https://vast-challenge.github.io/2024/)。
- [MC1：知识抽取与来源偏差](https://vast-challenge.github.io/2024/MC1.html)、[MC2：船舶时空行为](https://vast-challenge.github.io/2024/MC2.html)、[MC3：业务关系变化](https://vast-challenge.github.io/2024/MC3.html)。
- [MC1 官方获取表单](https://docs.google.com/forms/d/e/1FAIpQLSe-LEIJ70qNII7e3XuhZ-Vg9s218ZwRxc4e05za8PBf8Qu3Bg/viewform)。各题页面有独立入口；未填写或提交。

## 可用于什么

最值得进一步看的调查资源之一。MC1 要比较新闻来源、两种模型抽取算法以及人工分析员对图的修改，定位偏差来自哪一层；MC2/MC3 涉及时空轨迹和关系变化。它直接提示：即使使用 GNN，也要先解决图中边的来源、抽取错误和修订依据。

这里的 visual analytics 指可视分析，不能因此宣称数据原生具备照片—文本任务。公开题目不等于有逐条边真值、每轮可接受假设和统一自动评分标签，需要取得数据后再判断。

## 使用条件与限制

官方明确数据完全合成，虽与 2023 年有相似元素，但不能假设跨年连续或直接拼成真实演化轨迹。数据通过官方表单获取，机器可评分 gold 的公开范围未确认，许可与版本以下载条款为准。
