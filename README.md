# ZeKin · AI 思政打卡系统

高校学生日常管理数字化方案，覆盖**查寝、上课、实习**三大打卡场景，实现「到岗验证 + 内容合规 + 数据追溯 + 异常预警」全流程管理，替代传统人工考勤。

## 项目简介

ZeKin 面向学生、辅导员与管理员三类用户：学生通过手机提交打卡（文字心得 + GPS + 可选照片）；教师在线审核班级考勤；管理员配置系统并查看统计报表。项目采用敏捷开发、规格驱动（OpenAPI 契约先行），支持 Local → Dev → UAT → Prod 四环境验收。

**技术栈：** Python · FastAPI · Vue 3 · MySQL 8.0

**团队：** 王韩韵（产品/QA）· 赵耀（后端/DevOps）· 胡钊炫（管理端）· 华心仪（学生端）

## 快速开始

```bash
# 1. 数据库
docker compose -f deploy/docker-compose.local.yml up -d

# 2. 后端
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# 3. 前端
cd frontend/admin && npm install && npm run dev    # 管理端 :5173
cd frontend/student && npm install && npm run dev  # 学生端 :5174
```

API 文档：http://localhost:8000/docs

## 文档

- [需求分析报告](docs/requirements-analysis-report.md)
- [团队分工](docs/team-module-division.md)
- [OpenAPI 契约](specs/openapi.yaml)

## License

课程实训项目。
