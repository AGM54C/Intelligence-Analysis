# 提示与候选状态契约

实际提示位于 [prompting.py](../../../evidence-pilot/evidence_pilot/prompting.py)，输出检查位于 [outputs.py](../../../evidence-pilot/evidence_pilot/outputs.py)。相同 ID 的事实表述逐字不可变，新解释使用当前阶段的 ID 前缀并记录父候选；每条 statement 最多 120 字。非法或截断输出保留，后续阶段继承最近一次有效状态，不自动重试。

A/B/C 共用公共说明、当前证据与模型配置，差异限于以下候选维护规则。公共字段与私有标签隔离，提示调整不得利用测试答案。以下文字概括接口，运行内容以代码为准。

**所有方法的公共说明**

```text
根据当前阶段可用的图片、文字和来源记录，判断给定固定时点的问题。
材料可能不完整、相互冲突或来自同一个原始观察。报道数量不等于独立证据数量。
图片本身可真实，但它的图注、时间、地点或事件归属可能错误。

只有 active_evidence 中的材料能作为当前阶段有效证据。
revision_events 指定的撤回/替换是环境给出的材料状态更新，不直接给出目标问题答案。
旧解释是待检验的假设，不是真值；引用已撤回的材料不能继续支持结论。
没有证据时保留未知，不编造来源、观察或图片细节。

结论必须是 supported、refuted、insufficient 之一，并提供简短的可检查依据。
解释要具体到图像归属、时空关系或来源依赖；同一解释换种措辞不算不同假设。
可在当前调用内比较不同解释。最终输出遵循约定 JSON 结构，不需要复述完整推理过程。
```

模型收到的用户载荷仅由 `question`、`target_time`、`active_evidence`、按序的实际图片、`revision_events`、`previous_state` 构成。诊断集分层、参考标签、历史条件名、gold 答案、评估用视觉事实均不进入主实验载荷。

**A：单解释更新**

```text
previous_state 是上轮一个解释及其证据引用，可能已经过时；第一轮为空。
结合当前证据重新检查它，也允许换成另一个解释。
当前阶段最终只保留最多一个解释；无法确定时仍可以输出 insufficient。
说明支持/反对材料及仍未解决的问题，不把旧答案当作约束。
```

**B：全量重启**

```text
只基于当前证据开始判断，当前阶段没有可以继承的旧解释。
可以在当前阶段生成并比较最多四个实质不同的解释，也可以自检。
给出当前最合理的解释集合与最终结论；它们不传给下一轮。
```

B 每轮由程序新建独立请求。不要把空旧状态和聊天服务器内保留的 conversation/thread 混用；对 B 最终配对请求做哈希检查，历史标记只写日志。

**C：普通多假设更新**

```text
previous_state 最多包含四个旧解释，均可能过时；第一轮为空。
用当前有效证据重新评价旧解释，并可生成最多四个新的或修订后的解释。
逐项检查有效材料中的时空、视觉及来源约束，列出主要支持、冲突和未解决项。
从旧解释和新解释的合集里保留最多四个实质不同、当前仍值得考虑的解释。
记录哪些候选被移除及原因；移除记录只写日志，不在下一轮返回给本方法。
沿用原 ID 时 statement 必须逐字不变；改变表述或事实预测则生成新 ID，并记录 parent_ids。
```

模型给出候选的相对排序，程序不能利用隐藏答案替换次序。将提案和评分拆成多次调用时，应独立记录版本与累计计算成本。

**统一最终输出结构**

以下为字段示意，`<...>` 只是说明，不是可运行样本或模拟结果。

```json
{
  "hypotheses": [
    {
      "id": "<immutable neutral ID>",
      "parent_ids": [],
      "statement": "<testable event/image/source interpretation>",
      "support_ids": [],
      "conflict_ids": [],
      "unresolved_points": []
    }
  ],
  "selected_ids": [],
  "discard_records": [
    {
      "hypothesis_id": "<candidate ID>",
      "reason_kind": "constraint_conflict|redundant|capacity|other",
      "reason_evidence_ids": [],
      "brief_reason": "<checkable reason>"
    }
  ],
  "verdict": "supported|refuted|insufficient",
  "support_ids": [],
  "conflict_ids": [],
  "brief_justification": "<evidence-bound explanation>"
}
```

`hypotheses` 是当前阶段已考虑候选，`selected_ids` 指定传入下一阶段的存活者；A 最多 1 个、C 最多 4 个，B 不继承。未选候选仅保留在研究日志里。C 的全部候选数最多为旧 4 + 新 4，第一轮最多 4 个。

引用有效性和 JSON 可解析性由程序检查；引用是否真实支撑结论需要基于题包核查。既不自动修写错误的模型结论，也不把修复失败的调用删除。输出未完成或截断单列，并记录花费。

**对照的输入变化**

去图条件保留相同问题和文字，移除图片与自动视觉观察；仅提示有些视觉材料未提供，不告诉模型正确答案。人工视觉事实条件用预先独立写好的可见事实代替图片，不能包含目标裁决或对候选的评价。视觉关系变体必须人工确认变体标签，后到谣言条件不告知新消息是假。
