# ZeKin MVP 项目 TODO

本文档用于跟踪 ZeKin 第一阶段之后的团队待办。详细需求、分工和验收标准以 `docs/` 与 `specs/` 目录为准。

## S0：需求与规格冻结

- [x] 创建 GitHub 仓库并完成初始项目文档提交
- [x] 编写 MVP 需求分析报告：`docs/requirements-analysis-report.md`
- [x] 明确团队模块划分：`docs/team-module-division.md`
- [x] 建立规格驱动开发规范：`docs/spec-driven-development.md`
- [x] 建立四环境策略：`docs/environment-strategy.md`
- [x] 建立 OpenAPI 契约初稿：`specs/openapi.yaml`
- [x] 建立数据库 DDL 初稿：`specs/database/schema.sql`
- [ ] 团队共同评审需求分析报告并确认 Must / Should / Could 范围
- [ ] 将需求 ID 拆成 GitHub Issues，并绑定负责人、分支和验收标准
- [ ] 创建 `develop` 分支并配置分支保护规则

## S1：Must 功能开发

- [ ] 赵耀：完成认证、打卡、教师审核核心 API
- [ ] 赵耀：补齐后端单元测试和健康检查
- [ ] 华心仪：完成学生端登录、首页、打卡页面
- [ ] 胡钊炫：完成管理端登录、审核列表、审核详情
- [ ] 王韩韵：输出 S1 测试用例和验收记录模板
- [ ] 全员：完成 Local 环境联调
- [ ] 全员：合并 S1 Must 功能到 `develop`

## S2：Should 功能增强

- [ ] 赵耀：实现 AI 内容审核降级方案
- [ ] 赵耀：实现统计、补签、系统配置 API
- [ ] 胡钊炫：实现统计看板、导出、用户/地点/课程配置
- [ ] 华心仪：实现个人中心、补签申请、历史状态增强
- [ ] 王韩韵：组织 Dev 环境功能走查
- [ ] 全员：完成 Dev 服务器部署验收

## S3：UAT 与质量加固

- [ ] 王韩韵：组织用户验收环境测试
- [ ] 赵耀：完成生产配置、安全项和日志检查
- [ ] 胡钊炫：完成管理端兼容性与异常状态检查
- [ ] 华心仪：完成学生端移动端适配检查
- [ ] 全员：修复 UAT 缺陷并形成缺陷闭环
- [ ] 全员：完成性能、权限、数据一致性回归

## S4：生产环境测试与交付

- [ ] 创建发布 Tag 和版本说明
- [ ] 完成生产环境测试部署
- [ ] 执行核心路径冒烟测试
- [ ] 准备用户手册、部署手册、测试报告、验收报告
- [ ] 完成最终验收签字

## 协作约束

- 不直接向 `main` 推送业务代码，所有功能进入 feature 分支。
- 跨模块变更必须先更新 `specs/openapi.yaml` 或对应 Feature Spec。
- 前端不得口头约定接口字段，必须以 OpenAPI 为准。
- 数据库字段变更必须同步 `specs/database/schema.sql`。
- Agent 生成代码必须由负责人 review，并在 PR 中说明验证结果。
