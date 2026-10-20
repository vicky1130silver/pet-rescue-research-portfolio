# 答卷字段与编码

| 字段 | 类型 | 可用值 | 用途 |
|---|---|---|---|
| response_id | 文本 | 唯一匿名编号 | 去重，不放姓名或手机号 |
| city | 文本 | 北京／天津／河北城市名／其他 | 地区分组 |
| duration_seconds | 数值 | 非负秒数 | 记录答题时长，不自动凭时长判无效 |
| adoption_intent | 枚举 | yes／no／unsure | 描述统计与交叉表 |
| has_pet_experience | 枚举 | yes／no | 养宠经历分组 |
| consent | 枚举 | yes／no | 是否同意参与 |

多选题如继续增加，应按每个选项单列编码，并记录该题有效作答分母。未回答不能写成“否”。

`responses-template.csv` 只有表头，没有模拟答卷。与公开研究的汇总数据保持分离。
