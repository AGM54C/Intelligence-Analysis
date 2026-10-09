# CONFACT

| 项目 | 说明 |
|---|---|
| 类型 | 冲突文本证据下的自动事实核验数据 |
| 模态与标签 | 断言、问题、裁决、日期、证据 URL/正文、媒体背景；以文本为主 |
| 获取状态 | 官方仓库内数据文件目录已核实 |

## 下载与来源

- [作者仓库](https://github.com/zoeyyes/CONFACT)、[数据目录](https://github.com/zoeyyes/CONFACT/tree/main/data/dataset)。
- [HumC.pkl.gz](https://raw.githubusercontent.com/zoeyyes/CONFACT/main/data/dataset/HumC.pkl.gz)、[ModC.pkl.gz](https://raw.githubusercontent.com/zoeyyes/CONFACT/main/data/dataset/ModC.pkl.gz)。目录另有 `all_media_data.pkl`、`mbfc_media_data.pkl`。
- 对应论文：[Resolving Conflicting Evidence in Automated Fact-Checking](https://doi.org/10.24963/ijcai.2025/1073)。

## 可用于什么

适合研究材料互相矛盾时的来源处理、筛选、重排和结论生成，是必须比较的近邻。人审与模型识别的冲突集合需分开，不能把两者都称为逐例人工确认。

媒体背景分数不等于具体证据真假。字段 `fact_checking_article`、`label` 等可能直接泄漏裁决，不能混入非 oracle 的检索语料。原任务主要是固定文本证据冲突，未自带图片与自然撤回历史，不能直接称为动态图文情报基准。

## 使用条件与限制

官方仓库提供数据文件和下载入口，完整压缩数据可用性未验证。仓库数据、证据正文与媒体背景数据的条款需分别核对，不能推定统一许可。数据立场与来源背景不能直接当作每条材料的绝对真值。
