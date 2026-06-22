# ZeKin · 72 小时极限 MVP 需求建模包

ZeKin 是面向高校学生日常管理的 AI 思政打卡 MVP。当前仓库已按要求删除全部实现代码，仅保留原始需求输入 `需求分析.docx`，并重新设计为专业需求分析与 UML 建模交付物。

## 当前交付

- [需求分析报告](docs/requirements-analysis-report.md)
- [用例规约文档](docs/use-case-specifications.md)
- [72 小时极限开发计划](docs/72h-extreme-programming-plan.md)
- [原型设计说明](docs/prototype-design.md)
- [UML/PlantUML 图源文件](diagrams/)
- [原型样图 SVG](prototypes/)

## 72 小时 MVP 范围

本版以“能完成业务闭环”为唯一目标：

1. 学生完成三类打卡：查寝、上课、实习。
2. 辅导员/教师查看班级打卡并完成审核。
3. 管理员/教师查看统计概览。
4. 系统保存可追溯记录，支撑后续扩展 AI 审核、人脸识别、补签和通知。

AI 审核、人脸识别、复杂推送、积分体系不进入 72 小时核心实现，作为扩展点预留。

## 建模资产

- 用例图：`diagrams/00_system_usecase.puml`
- 活动图：`diagrams/01_submit_checkin_activity.puml`、`diagrams/02_teacher_review_activity.puml`、`diagrams/03_statistics_activity.puml`
- 顺序图：`diagrams/04_submit_checkin_sequence.puml`、`diagrams/05_teacher_review_sequence.puml`
- 时序图：`diagrams/06_checkin_timing.puml`
- 分析类图：`diagrams/07_analysis_class_diagram.puml`

PlantUML 文件可在 VS Code PlantUML 插件、IntelliJ PlantUML 插件或 PlantUML Server 中渲染。
