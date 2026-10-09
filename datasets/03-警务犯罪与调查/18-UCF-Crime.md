# UCF-Crime

| 项目 | 说明 |
|---|---|
| 类型 | 监控视频异常检测基准 |
| 模态与标签 | 视频、正常/异常类别；测试视频含异常时间区间标注 |
| 获取状态 | 作者仓库可访问；外部下载地址已记录，未验证全量取得 |

## 下载与来源

- [作者官方仓库](https://github.com/WaqasSultani/AnomalyDetectionCVPR2018)。
- README 提供的[大学下载入口](https://visionlab.uncc.edu/download/summary/60-data/477-ucf-anomaly-detection-dataset)与[Dropbox 入口](https://www.dropbox.com/sh/75v5ehq4cdg5g5g/AABvnJSwZI7zXb8_myBA0CLHa?dl=0)。
- 仓库中的 `Anomaly_Train.txt` 和 `Temporal_Anomaly_Annotation.txt` 等提供划分/标注说明。

## 可用于什么

可作为视觉事件感知的辅助对照。未来若构建图文案例，需要选择有明确可见事实的帧，记录时间区间，配合有依据的文字材料，不能让帧截取破坏事件语境。

视频异常类别不等于犯罪构成、行为动机或人员有罪的事实标签。原数据没有调查笔录、证据可信度与假设演化轨迹；静态抽帧加模型生成描述也不自动成为真实警务情报集。

## 使用条件与限制

作者仓库提供视频下载说明，外链文件完整性未验证。大学旧项目页存在 TLS 访问问题（2026-10-09），可优先参考作者仓库。使用范围按作者声明及原视频权利核对，不能推定统一再分发许可。
