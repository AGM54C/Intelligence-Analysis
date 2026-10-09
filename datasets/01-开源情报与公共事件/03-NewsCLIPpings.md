# NewsCLIPpings

| 项目 | 说明 |
|---|---|
| 类型 | 基于新闻图片与图注构造的图文错配基准 |
| 模态与标签 | 图片、新闻图注、样本与图片 ID、`falsified` 配对标签 |
| 获取状态 | 官方标注下载脚本公开；图片另取 VisualNews |

## 下载与来源

- [作者仓库](https://github.com/g-luo/news_clippings)、[下载脚本](https://raw.githubusercontent.com/g-luo/news_clippings/master/download.sh)。
- [合并平衡训练标注](https://huggingface.co/g-luo/news-clippings/resolve/main/data/merged_balanced/train.json)。完整 train/val/test 及不同错配版本按官方脚本获取。
- [VisualNews 图片与原始元数据](https://github.com/FuxiaoLiu/VisualNews-Repository)、[作者图片下载页](https://www.cs.rice.edu/~vo9/visualnews/)。需要按 ID 对齐，标注文件本身不包含图片字节。

## 可用于什么

适合研究“图片和文字各自真实，但放在一起误导”的情况，作为图文对应能力的基线资源。后续可以检查图像替换、裁剪与来源重复如何影响判断。

负例主要是算法构造的错配，不能全部解释为自然传播的谣言。其时间戳也不组成完整新闻更正史。VisualNews 与 NewsCLIPpings 是同源资源，多个采样版本不能当成独立事件重复计数。

## 使用条件与限制

标注通过官方脚本获取，原图依赖 VisualNews。使用与再分发遵循两个项目及原新闻图片的条款，不能推定所有图片具有统一开放许可；完整图片覆盖率需在固定版本上检查。
