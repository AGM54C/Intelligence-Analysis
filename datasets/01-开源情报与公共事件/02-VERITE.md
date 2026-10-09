# VERITE

| 项目 | 说明 |
|---|---|
| 类型 | 注重单模态偏差控制的图文失实信息评测集 |
| 模态与标签 | 1,000 组图文配对；真实、脱离语境、错误图注 |
| 获取状态 | CSV 公开；原始图片需机构邮箱验证 |

## 下载与来源

- [作者仓库](https://github.com/stevejpapad/image-text-verification)。
- [VERITE.csv](https://raw.githubusercontent.com/stevejpapad/image-text-verification/master/VERITE/VERITE.csv)、[VERITE_articles.csv](https://raw.githubusercontent.com/stevejpapad/image-text-verification/master/VERITE/VERITE_articles.csv)。
- [官方图片申请入口](https://huggingface.co/datasets/stefpapad/VERITE)。作者于 2026 年 7 月更新：许多旧图片 URL 已失效，现提供图片，但须使用正式学术或研究机构邮箱验证。

## 可用于什么

适合检查模型是否真正结合图片与文字判断。其模态平衡设计尤其值得借鉴：同一图像或图注可以出现在真实及误导配对中，避免只看一个模态就完成任务。

它是静态配对核验，尚无逐轮证据撤回或候选恢复标签。使用真实/错误图注构造顺序实验时须标为受控改造，并按原始图片与事件分组，防止相同材料跨训练测试集。CLIP 特征不能替代给视觉语言模型输入原始图片。

## 使用条件与限制

标注 CSV 公开，图片通过官方 Hugging Face 入口按要求验证学术机构邮箱。代码许可为 Apache 2.0，作者说明将数据用途限定为研究；代码许可不能替代新闻图片的使用条件。
