# Sherlock

| 项目 | 说明 |
|---|---|
| 类型 | 图像线索支持的溯因推理（abductive reasoning）基准 |
| 模态与标签 | 图像区域、可见线索、人工给出的合理推断；不是案件事实真值 |
| 获取状态 | 作者提供标注 ZIP；原图按 VCR/Visual Genome 各自入口取得 |

## 下载与来源

- [官方仓库](https://github.com/allenai/sherlock)。
- [训练标注 v1.1](https://storage.googleapis.com/ai2-mosaic-public/projects/sherlock/data/sherlock_train_v1_1.json.zip)、[验证标注 v1.1](https://storage.googleapis.com/ai2-mosaic-public/projects/sherlock/data/sherlock_val_with_split_idxs_v1_1.json.zip)。
- 原图使用 README 指向的 VCR 和 Visual Genome 官方下载；作者说明不要依赖旧的逐图 URL。

## 可用于什么

用于研究从可见细节产生不同合理解释，比普通图像描述更接近“生成候选假设”。可把它当作通用能力辅助评测，检验假设是否指向图片中的具体线索。

名称不表示它是刑侦数据集。人工合理推断未必是经外部证据证实的事实，也没有持续补充证据后的假设生灭轨迹。因此不能用原标签直接评价最终情报结论的真实性。

## 使用条件与限制

作者仓库提供下载文件地址，README 将数据列为 CC-BY、代码列为 Apache 2.0；原图还需遵循 VCR 或 Visual Genome 的来源条件。该任务研究图像线索与合理推断，不是刑事调查数据。
