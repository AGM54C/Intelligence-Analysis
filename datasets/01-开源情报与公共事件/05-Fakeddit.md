# Fakeddit

| 项目 | 说明 |
|---|---|
| 类型 | Reddit 多模态失实信息分类语料 |
| 模态与标签 | 帖子标题、图片链接/图片包、元数据；多粒度弱标签；评论单独提供 |
| 获取状态 | 作者提供 Google Drive 标注、图片和评论下载入口 |

## 下载与来源

- [作者仓库](https://github.com/entitize/Fakeddit)。
- [文本与元数据 v2](https://drive.google.com/drive/folders/1jU7qgDqU1je9Y0PMKJ_f31yXRo5uWGFm?usp=sharing)。
- [图片包](https://drive.google.com/file/d/1cjY6HsHaSZuLVHywIxD5xQqng33J5S2b/view?usp=sharing)、[评论](https://drive.google.com/drive/folders/150sL4SNi5zFK8nmllv5prWbn0LyvLzvo?usp=sharing)。

## 可用于什么

可用于大规模图文噪声测试、标题与配图对应、传播内容分析。原实验的多模态子集应按 `multimodal_only_samples` 等说明筛选，评论通过 submission ID 对齐。

标签带有社区来源和类别弱监督特征，不等于每条主张经独立事实调查。不能把类别标签直接当作真实事件结论，或把帖子评论数量当作独立证据数量。没有现成的阶段证据充分性或修订史 gold。

## 使用条件与限制

作者提供 Google Drive 标注、图片和评论入口，外部文件可用性与完整图片覆盖率未验证。帖子、图片、评论的使用范围受项目及原平台条款约束，不推定统一开放许可。
