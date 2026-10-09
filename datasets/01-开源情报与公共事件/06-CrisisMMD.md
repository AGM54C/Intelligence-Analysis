# CrisisMMD

| 项目 | 说明 |
|---|---|
| 类型 | 真实灾害事件的社交媒体图文数据 |
| 模态与标签 | 文本、图片；信息性、人道救援类别、损毁程度等 |
| 获取状态 | 官网提供图片文本包与标注压缩包 |

## 下载与来源

- [官方数据页](https://crisisnlp.qcri.org/crisismmd)。
- [CrisisMMD v2.0 图片文本包，约 1.8 GB](https://crisisnlp.qcri.org/data/crisismmd/CrisisMMD_v2.0.tar.gz)。
- [全部划分标注](https://crisisnlp.qcri.org/data/crisismmd/crisismmd_datasplit_all.zip)、[一致标签子集](https://crisisnlp.qcri.org/data/crisismmd/crisismmd_datasplit_agreed_label.zip)。

## 可用于什么

涵盖 2017 年七起自然灾害，可支持公共事件的图文感知、地点/损毁描述和事件分组，是开源情报取材候选。图片内容可能与文本提供不同的信息，可检查视觉是否带来额外约束。

人道救援或损毁标签不是“真/假”标签，也不自动验证拍摄时间与地点。要构建冲突情报任务，还需核实原图出处、同图转发和更正过程。图片具有真实来源，不等于所有文字报告都是真实事实。

## 使用条件与限制

官方网站提供数据包下载。使用遵循[官方条款](https://crisisnlp.qcri.org/terms-of-use.html)，原始社交媒体素材另有权利约束；灾害类别不能直接替代真假标签。
