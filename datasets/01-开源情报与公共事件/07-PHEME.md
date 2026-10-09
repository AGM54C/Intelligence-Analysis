# PHEME：谣言检测与真实性判定版

| 项目 | 说明 |
|---|---|
| 类型 | 多事件社交媒体讨论线程与真实性标注 |
| 模态与标签 | 文本、回复树、时间；rumour/non-rumour 与 true/false/unverified 分开 |
| 获取状态 | Figshare 官方条目及归档文件元数据目录列出 |

## 下载与来源

- [带真实性标签的正式条目](https://figshare.com/articles/dataset/PHEME_dataset_for_Rumour_Detection_and_Veracity_Classification/6392078)。
- [PHEME_veracity.tar.bz2，约 46.5 MB](https://ndownloader.figshare.com/files/11767817)。
- [条目元数据 API](https://api.figshare.com/v2/articles/6392078)。不要误用只有 rumours/non-rumours 的旧版来声称拥有真假标签。

## 可用于什么

九个事件的源帖、回应及树结构，可研究新信息到达、来源/传播依赖以及未核实状态下的判断。是文字与传播图对照的合适候选。

“谣言”在此不等于“错误”。线程最终真实性标签也不表示每条回复可靠，不能直接监督逐证据真假。图片字节及图文证据覆盖未获保证，不满足原生图文要求；回复时间线不等于经过裁定的证据修订过程。

## 使用条件与限制

Figshare 条目提供真实性版本的归档及文件元数据，条目标注为 CC BY 4.0；推文原文仍受原始内容权利及平台条件约束。不同 PHEME 版本的任务与标签需区分。
