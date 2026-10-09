# Amazon Reviews 2023

| 项目 | 说明 |
|---|---|
| 类型 | 商品评论与商品元数据语料 |
| 模态与标签 | 评论、评分、时间、商品属性及图片相关字段；图像覆盖需逐项检查 |
| 获取状态 | 官方分类 JSONL 压缩文件与 Hugging Face 入口 |

## 下载与来源

- [作者项目页](https://amazon-reviews-2023.github.io/)、[官方 HF 仓库](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)。
- 示例分类：[All_Beauty 评论](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/All_Beauty.jsonl.gz)、[All_Beauty 商品元数据](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_All_Beauty.jsonl.gz)。其他类别从项目页选择，示例不代表全量数据。

## 可用于什么

可作为消费者市场研究的素材，例如比较产品宣称、用户反馈和商品图片，追踪同一商品随时间出现的不同描述。适合产品层面的调研，不等同于宏观行业情报。

评分是主观评价，不是评论真实性标签；相互矛盾的评价也可能来自不同体验。商品图通常不证明某次用户经历。没有已核实的“虚假评论—纠正—最终事实”链，需要另找可判定事实与独立依据。

## 使用条件与限制

项目提供分类下载及 Hugging Face 入口，图片 URL 存活率和全量覆盖未验证。许可按项目、数据卡和原始素材条件核对；评论评分不能解释为内容真实性，图片也不推定可以自由再分发。
