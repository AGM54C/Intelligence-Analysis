# Chicago Crimes — 2001 to Present

| 项目 | 说明 |
|---|---|
| 类型 | 城市公开警务事件记录服务 |
| 模态与标签 | 结构化时间、街区位置、案件编号、类型、描述、逮捕标记等 |
| 获取状态 | 官方数据集元数据可访问；支持门户导出与 SODA API |

## 下载与来源

- [Chicago 官方数据门户](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2)。
- [元数据](https://data.cityofchicago.org/api/views/ijzp-q8t2.json)、[SODA JSON 接口](https://data.cityofchicago.org/resource/ijzp-q8t2.json)。正式获取时按时间/地区分页，不以默认返回页当全量。

## 可用于什么

可做公共安全统计、事件时空背景与报告口径核对，也可提供选题线索。官网说明数据为已报告事件，排除最近七天，并会持续修改。

这是行政记录表，不是完整案件证据。`arrest` 不等于有罪判决，记录存在也不等于所有描述都已证实。`updated_on` 是更新字段，不提供更新前的完整版本；不能仅凭该字段构造历史可见证据链。没有原生图像证据。

## 使用条件与限制

官方门户元数据中的许可字段为 `SEE_TERMS_OF_USE`，需按城市条款使用、引用和再分发，不能写为 CC0。行政记录表不等于图文案卷或个人有罪的裁决。
