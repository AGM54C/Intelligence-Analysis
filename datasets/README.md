# 公开数据集与下载目录

**整理网上已有的 25 项数据集与开放数据资源，按四类逐项建档。** 每项说明下载/获取入口、模态、标签、可用范围、局限及核查状态。目录用于选材；自建数据的要求另见设计规范。

获取条件的信息日期为 **2026-10-09**。本目录提供官方入口与说明，不包含原始数据包；文件目录、外部网盘、申请要求与访问限制分别标注。下载完整性与样本可用性需独立核验。[CSV 汇总](数据集清单.csv)用于筛选，获取条件见[资源使用说明](资源使用说明.md)。

## 优先看哪些

| 研究需求 | 优先资源 | 仍需补足 |
|---|---|---|
| 图文线索真伪、错配与证据支持 | AVerImaTeC、VERITE、MOCHEG；NewsCLIPpings 作受控错配对照 | 自然更正史、每阶段可见证据、候选恢复标签 |
| 新闻与关系图中的冲突调查 | VAST Challenge 2024/2023、CONFACT | 图边/证据真值与可自动评分答案；VAST 的图不是照片 |
| 财报/图表支持的市场判断 | TAT-DQA、ChartQA；FinQA/TAT-QA 作数值与文本表格对照 | 自然错误陈述、不同版本报告、行业事实判定 |
| 新事件取材和公开记录追踪 | GDELT、SEC EDGAR、UK Police 等 | 网页/图片版本存档、可靠终局依据及图文材料 |
| 视觉猜想与建图模块 | Sherlock、DocRED | 整体情报任务的结论正确性与序贯评测 |

“开源情报”描述信息获取方式，市场和警务描述应用领域，三者可以交叉。分类用于检索，不表示数据来源相互独立；TAT-QA/TAT-DQA 等同源关系已在条目中注明。

## 开源情报与公共事件（8 项）

| 资源 | 模态/主要标签 | 获取入口与状态 |
|---|---|---|
| [01 AVerImaTeC](01-开源情报与公共事件/01-AVerImaTeC.md) | 图文、问答证据、核验裁决 | [HF 文件目录](https://huggingface.co/datasets/Rui4416/AVerImaTeC/tree/main)；官方文件目录 |
| [02 VERITE](01-开源情报与公共事件/02-VERITE.md) | 图文；真实/脱离语境/错误图注 | [CSV](https://github.com/stevejpapad/image-text-verification/tree/master/VERITE) 公开；[图片](https://huggingface.co/datasets/stefpapad/VERITE)需机构邮箱验证 |
| [03 NewsCLIPpings](01-开源情报与公共事件/03-NewsCLIPpings.md) | 图文；受控配对真假 | [官方脚本](https://github.com/g-luo/news_clippings/blob/master/download.sh)；另取 VisualNews 图片 |
| [04 MOCHEG](01-开源情报与公共事件/04-MOCHEG.md) | 图文证据、核验、解释 | [官方仓库](https://github.com/VT-NLP/Mocheg)提供申请表 |
| [05 Fakeddit](01-开源情报与公共事件/05-Fakeddit.md) | 图文、评论；弱监督类别 | [官方网盘入口](https://github.com/entitize/Fakeddit)；未实测下载 |
| [06 CrisisMMD](01-开源情报与公共事件/06-CrisisMMD.md) | 灾害图文；信息性/救援/损毁 | [官方直接下载](https://crisisnlp.qcri.org/crisismmd)；没有真假标签 |
| [07 PHEME](01-开源情报与公共事件/07-PHEME.md) | 文本、回复树；真/假/未核实 | [真实性版归档](https://ndownloader.figshare.com/files/11767817)；归档元数据可查 |
| [08 GDELT](01-开源情报与公共事件/08-GDELT.md) | 新闻事件/提及/知识图谱 | [官方数据服务](https://www.gdeltproject.org/data.html)；非真假评测集 |

## 市场与行业调研（6 项）

| 资源 | 模态/主要标签 | 获取入口与状态 |
|---|---|---|
| [09 FinQA](02-市场与行业调研/09-FinQA.md) | 文本、解析表格；数值答案/程序 | [官方 JSON](https://github.com/czyssrs/FinQA/tree/main/dataset)；非原生页图 |
| [10 TAT-QA](02-市场与行业调研/10-TAT-QA.md) | 文本、解析表格；问答 | [官方 JSON](https://github.com/NExTplusplus/TAT-QA/tree/master/dataset_raw)；非原生页图 |
| [11 TAT-DQA](02-市场与行业调研/11-TAT-DQA.md) | 视觉财报文档；数值问答 | [官方网盘](https://drive.google.com/drive/folders/1SGpZyRWqycMd_dZim1ygvWhl5KdJYDR2)；未实测下载 |
| [12 ChartQA](02-市场与行业调研/12-ChartQA.md) | 图表、问题、答案及表格 | [完整 HF 数据](https://huggingface.co/datasets/ahmed-masry/ChartQA)；并非全是财经图 |
| [13 SEC EDGAR](02-市场与行业调研/13-SEC-EDGAR.md) | 公司披露、XBRL；无真假标签 | [官方 API 说明](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)；访问受限，下载未验证 |
| [14 Amazon Reviews 2023](02-市场与行业调研/14-Amazon-Reviews-2023.md) | 评论、商品元数据、图片字段 | [分类下载](https://amazon-reviews-2023.github.io/)；评分不是真实性标签 |

## 警务犯罪与调查（8 项）

| 资源 | 模态/主要标签 | 获取入口与状态 |
|---|---|---|
| [15 VAST Challenge 2023](03-警务犯罪与调查/15-VAST-Challenge-2023.md) | 调查关系图、贸易记录、竞争叙事 | [官方题目](https://vast-challenge.github.io/2023/overview.html)内有表单；gold 未核实 |
| [16 VAST Challenge 2024](03-警务犯罪与调查/16-VAST-Challenge-2024.md) | 文章、抽取/修改图、轨迹；合成调查 | [官方题目](https://vast-challenge.github.io/2024/)内有表单；gold 未核实 |
| [17 CAIL2018](03-警务犯罪与调查/17-CAIL2018.md) | 中文裁判文本；司法预测标签 | [官方压缩包](https://cail.oss-cn-qingdao.aliyuncs.com/CAIL2018_ALL_DATA.zip)；非原始调查过程 |
| [18 UCF-Crime](03-警务犯罪与调查/18-UCF-Crime.md) | 视频；异常类别/区间 | [作者下载说明](https://github.com/WaqasSultani/AnomalyDetectionCVPR2018)；外链未实测 |
| [19 Chicago Crimes](03-警务犯罪与调查/19-Chicago-Crimes.md) | 警务行政记录表 | [官方元数据](https://data.cityofchicago.org/api/views/ijzp-q8t2.json)可读；无图文案卷 |
| [20 NYPD Complaints](03-警务犯罪与调查/20-NYPD-Complaints.md) | 报案/投诉记录表 | [官方元数据](https://data.cityofnewyork.us/api/views/qgea-i56i.json)可读；日期覆盖待查 |
| [21 UK Police Open Data](03-警务犯罪与调查/21-UK-Police-Open-Data.md) | 月度记录、匿名位置、部分处理结果 | [CSV/API](https://data.police.uk/data/)；无原始图文证据 |
| [22 ICIJ Offshore Leaks](03-警务犯罪与调查/22-ICIJ-Offshore-Leaks.md) | 调查实体与关系图 | [官方 CSV/Neo4j](https://offshoreleaks.icij.org/pages/database)；关系不等于违法 |

## 通用能力与证据处理（3 项）

| 资源 | 模态/主要标签 | 获取入口与状态 |
|---|---|---|
| [23 Sherlock](04-通用能力与证据处理/23-Sherlock.md) | 图像线索与合理推断 | [官方标注及原图说明](https://github.com/allenai/sherlock)；不是刑侦数据 |
| [24 CONFACT](04-通用能力与证据处理/24-CONFACT.md) | 文本冲突证据、裁决、媒体背景 | [官方数据文件](https://github.com/zoeyyes/CONFACT/tree/main/data/dataset)；官方文件目录 |
| [25 DocRED](04-通用能力与证据处理/25-DocRED.md) | 文本、实体关系、证据句 | [官方下载说明](https://github.com/thunlp/DocRED/blob/master/data/README.md)；抽取不等于核实事实 |

## 与自建数据的关系

以上资源各覆盖部分能力，目前未确认有单个资源同时满足“图文必要、真假混合、持续补证、来源依赖、可核验终局结论与无答案泄漏”。后续可以构建多个领域数据集，并共享证据格式与评测协议，详见[多领域数据集构建设想](../docs/多领域数据集设计.md)。

自建正式集另有[硬性准入约束](../docs/自建数据集设计约束.md)：目标事件发生在所选模型知识截止日期之后，真假比例因案例而异，材料逐步公开，并覆盖 hard cases。这里收录的旧资源用于选材参考和辅助对照，不自动满足这些条件。

已有四个受控开发案例保存在 [experiments/data](../experiments/data/README.md)，用于测试代码和协议；不属于本目录收录的网上已有数据集。
