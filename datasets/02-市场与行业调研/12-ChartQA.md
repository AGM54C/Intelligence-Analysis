# ChartQA

| 项目 | 说明 |
|---|---|
| 类型 | 图表视觉问答与逻辑/数值推理基准 |
| 模态与标签 | 图表 PNG、问题与答案、对应 CSV 表格；部分版本含框标注 |
| 获取状态 | 官方 GitHub 子集及 Hugging Face 完整数据入口 |

## 下载与来源

- [官方仓库](https://github.com/vis-nlp/ChartQA)。
- [完整数据集](https://huggingface.co/datasets/ahmed-masry/ChartQA)、[文件目录](https://huggingface.co/datasets/ahmed-masry/ChartQA/tree/main)。
- 原仓库说明 `png/`、`tables/`、`*_human.json` 和 `*_augmented.json` 等文件组织；不要把仓库子集当作全部数据。

## 可用于什么

评估读图表、识别坐标轴与单位、比较趋势和计算差值，可为行业研究中的图表证据设立能力对照。human 与 augmented 问题来源不同，应分开报告。

图表主题不限于财经；正确回答单图问题不证明能识别虚假市场消息。若把原 CSV 一并交给模型，可能绕开视觉需求，适合作为受控对照而非纯图文主设置。作者提示部分框标注含噪声，不能直接作高精度视觉依据 gold。

## 使用条件与限制

官方仓库与 Hugging Face 提供完整数据入口。使用时核对固定版本的数据卡及源图表条款，不能推定统一许可覆盖全部原图。图表不全部来自金融领域。
