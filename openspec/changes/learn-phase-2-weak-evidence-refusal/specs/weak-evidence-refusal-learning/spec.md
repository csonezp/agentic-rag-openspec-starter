## ADDED Requirements

### Requirement: Evidence sufficiency check

项目 MUST 能在生成回答前判断检索证据是否足够。

#### Scenario: 检索结果为空

- **WHEN** top-k 检索结果为空
- **THEN** 系统 MUST 判断证据不足
- **AND** MUST 给出拒答原因

#### Scenario: 最高 score 低于阈值

- **WHEN** 检索结果最高 score 低于 `min_score`
- **THEN** 系统 MUST 判断证据不足
- **AND** MUST 给出拒答原因和最高 score

#### Scenario: 最高 score 达到阈值

- **WHEN** 检索结果最高 score 达到或高于 `min_score`
- **THEN** 系统 MUST 判断证据足够
- **AND** MAY 继续生成回答

### Requirement: Refusal before model generation

项目 MUST 在证据不足时拒答，并避免调用模型生成无依据回答。

#### Scenario: 弱证据拒答

- **WHEN** evidence check 判断证据不足
- **THEN** 系统 MUST 输出拒答文本
- **AND** MUST 输出拒答原因
- **AND** MUST NOT 调用真实模型生成回答

### Requirement: Weak evidence learning record

本小节完成时 MUST 记录拒答策略、阈值取舍、验证结果和学习过程中的关键交互总结。

#### Scenario: 完成弱证据拒答小节

- **WHEN** 弱证据拒答小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 更新勾选状态
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
