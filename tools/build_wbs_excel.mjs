import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(".");
const outputPath = path.join(root, "实训-知勤打卡系统-WBS任务分解表.xlsx");
const previewDir = path.join(root, "build", "excel_preview");

const workbook = Workbook.create();

const palette = {
  navy: "#0F172A",
  blue: "#1D4ED8",
  green: "#16A34A",
  amber: "#D97706",
  red: "#DC2626",
  slate: "#475569",
  lightBlue: "#DBEAFE",
  lightGreen: "#DCFCE7",
  lightAmber: "#FEF3C7",
  lightRed: "#FEE2E2",
  header: "#E8EEF5",
  border: "#CBD5E1",
};

function colLetter(n) {
  let s = "";
  while (n > 0) {
    const m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = Math.floor((n - m) / 26);
  }
  return s;
}

function addSheet(name, title, headers, rows, widths = []) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  const lastCol = colLetter(headers.length);
  sheet.getRange(`A1:${lastCol}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = {
    fill: palette.navy,
    font: { bold: true, color: "#FFFFFF", size: 15 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  sheet.getRange("A1").format.rowHeight = 30;
  sheet.getRangeByIndexes(1, 0, 1, headers.length).values = [headers];
  sheet.getRangeByIndexes(1, 0, 1, headers.length).format = {
    fill: palette.header,
    font: { bold: true, color: palette.navy },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: palette.border },
  };
  if (rows.length) {
    sheet.getRangeByIndexes(2, 0, rows.length, headers.length).values = rows;
    sheet.getRangeByIndexes(2, 0, rows.length, headers.length).format = {
      wrapText: true,
      verticalAlignment: "center",
      borders: { preset: "all", style: "thin", color: "#E2E8F0" },
    };
  }
  const tableRange = `A2:${lastCol}${rows.length + 2}`;
  const table = sheet.tables.add(tableRange, true, `${name.replace(/[^\w]/g, "")}Table`);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  sheet.freezePanes.freezeRows(2);
  widths.forEach((w, i) => {
    sheet.getRange(`${colLetter(i + 1)}:${colLetter(i + 1)}`).format.columnWidth = w;
  });
  return sheet;
}

const modules = [
  ["M1", "认证与角色模块", "赵耀", "王韩韵、胡钊炫、华心仪", "Must", "用户登录、当前用户、角色权限", "backend/app/api/v1/auth.py；前端登录页", "三类角色均可登录并进入对应工作台", "未开始"],
  ["M2", "学生打卡模块", "赵耀、华心仪", "王韩韵", "Must", "今日状态、三类打卡提交、历史记录、重复校验", "backend/checkins；frontend/student", "学生可提交查寝/上课/实习并查看历史", "未开始"],
  ["M3", "教师审核模块", "赵耀、胡钊炫", "王韩韵", "Must", "审核列表、详情、通过/驳回、班级权限", "backend/teacher；frontend/admin", "教师可审核所管班级打卡记录", "未开始"],
  ["M4", "统计概览模块", "赵耀、胡钊炫", "王韩韵", "Must", "今日应打卡、已打卡、打卡率、待审核、异常数", "backend/stats；frontend/admin dashboard", "统计指标正确展示", "未开始"],
  ["M5", "数据库与演示数据", "赵耀", "王韩韵", "Must", "users、classes、courses、checkins、reviews、location_rules", "database/schema.sql；database/seed.sql", "基础表可创建，演示账号可用", "未开始"],
  ["M6", "验收与项目管理", "王韩韵", "全员", "Must", "验收脚本、缺陷模板、四环境检查", "docs/；acceptance/", "10 步验收脚本可执行", "未开始"],
];

const people = [
  ["王韩韵", "产品 / QA / 验收负责人", "docs/；acceptance/", "需求冻结、接口契约、验收脚本、缺陷分级、四环境验收", "backend/、frontend/ 业务代码", "H0-H6；H60-H72", "需求与验收材料齐全"],
  ["赵耀", "后端 / 数据库 / 部署负责人", "backend/；database/；deploy/", "FastAPI、MySQL、认证、打卡、审核、统计、部署", "frontend/student/、frontend/admin/ 页面", "H6-H66", "后端服务和数据库可运行"],
  ["胡钊炫", "教师/管理端负责人", "frontend/admin/", "教师登录、审核列表、详情面板、审核操作、统计概览", "backend/ 数据库和业务规则", "H6-H66", "管理端审核与统计可演示"],
  ["华心仪", "学生端负责人", "frontend/student/", "学生登录、今日状态、提交打卡、历史记录、移动端适配", "backend/ 数据库和业务规则", "H6-H66", "学生端打卡闭环可演示"],
];

const wbs = [
  ["1.1", "项目规格与验收管理", "冻结 72 小时 MVP 范围", "王韩韵", "需求分析报告", "Must/Should/Could 清单", "Must/Should/Could 明确", "H0-H2", "无", "未开始"],
  ["1.2", "项目规格与验收管理", "编写接口契约草案", "王韩韵", "用例规约、顺序图", "docs/api-contract.md", "前后端字段一致", "H0-H4", "1.1", "未开始"],
  ["1.3", "项目规格与验收管理", "编写验收脚本", "王韩韵", "用例规约", "acceptance/uat-script.md", "覆盖登录、打卡、审核、统计", "H2-H6", "1.1", "未开始"],
  ["1.4", "项目规格与验收管理", "建立缺陷分级规则", "王韩韵", "验收目标", "acceptance/bug-template.md", "P0/P1/P2 定义清晰", "H4-H6", "1.3", "未开始"],
  ["1.5", "项目规格与验收管理", "每 12 小时组织集成检查", "王韩韵", "各成员进度", "集成记录", "阻塞问题有负责人", "H12/H24/H36/H48/H60", "2.1/3.1/4.1", "未开始"],
  ["1.6", "项目规格与验收管理", "组织最终验收", "王韩韵", "可运行系统", "验收报告", "四环境结果明确", "H66-H72", "5.5", "未开始"],
  ["2.1", "后端 API 与数据库", "初始化 FastAPI 项目", "赵耀", "技术栈约束", "backend/app/main.py", "/health 可访问", "H6-H8", "1.1", "未开始"],
  ["2.2", "后端 API 与数据库", "建立项目分层目录", "赵耀", "架构约束", "api/schemas/services/repositories", "目录清晰可导入", "H6-H8", "2.1", "未开始"],
  ["2.3", "后端 API 与数据库", "设计 MySQL 最小 DDL", "赵耀", "分析类图", "database/schema.sql", "6 张基础表可创建", "H8-H10", "1.2", "未开始"],
  ["2.4", "后端 API 与数据库", "初始化演示数据", "赵耀", "验收脚本", "database/seed.sql", "1 管理员、1 教师、3 学生", "H10-H12", "2.3", "未开始"],
  ["2.5", "后端 API 与数据库", "实现认证接口", "赵耀", "M1", "/auth/login、/auth/me", "三类角色可登录", "H12-H18", "2.1/2.4", "未开始"],
  ["2.6", "后端 API 与数据库", "实现学生打卡接口", "赵耀", "M2", "/checkins/today、POST /checkins、GET /checkins", "支持三类打卡和重复校验", "H18-H30", "2.5", "未开始"],
  ["2.7", "后端 API 与数据库", "实现教师审核接口", "赵耀", "M3", "/teacher/checkins、POST /teacher/reviews", "支持筛选、通过、驳回", "H30-H42", "2.6", "未开始"],
  ["2.8", "后端 API 与数据库", "实现统计接口", "赵耀", "M4", "/stats/overview", "返回打卡率、待审核、异常数", "H42-H50", "2.6/2.7", "未开始"],
  ["2.9", "后端 API 与数据库", "权限和异常处理", "赵耀", "所有接口", "统一错误响应", "未登录 401、越权 403", "H48-H56", "2.5-2.8", "未开始"],
  ["2.10", "后端 API 与数据库", "部署与环境变量", "赵耀", "四环境要求", ".env.example、启动说明", "本地和服务器可启动", "H56-H66", "2.1-2.9", "未开始"],
  ["3.1", "学生端 H5", "初始化 Vue 学生端", "华心仪", "原型样图", "frontend/student/", "Vite 可启动", "H6-H8", "1.1", "未开始"],
  ["3.2", "学生端 H5", "登录页", "华心仪", "M1 接口", "LoginView.vue", "学生账号可登录", "H8-H14", "3.1", "未开始"],
  ["3.3", "学生端 H5", "路由与登录态", "华心仪", "M1 接口", "router、store", "未登录自动回登录页", "H12-H18", "3.2", "未开始"],
  ["3.4", "学生端 H5", "今日状态页面", "华心仪", "M2 接口或 mock", "HomeView.vue", "三类状态清晰展示", "H18-H26", "3.3", "未开始"],
  ["3.5", "学生端 H5", "打卡表单", "华心仪", "原型、M2 接口", "CheckinView.vue", "可选类型、填内容、定位", "H24-H34", "3.4", "未开始"],
  ["3.6", "学生端 H5", "定位 composable", "华心仪", "浏览器定位 API", "useGeolocation", "定位失败有降级提示", "H26-H34", "3.5", "未开始"],
  ["3.7", "学生端 H5", "历史记录页面", "华心仪", "M2 接口", "HistoryView.vue", "显示审核状态和评语", "H34-H42", "3.5", "未开始"],
  ["3.8", "学生端 H5", "学生端联调", "华心仪", "后端接口", "可演示学生端", "登录、打卡、历史闭环通过", "H42-H58", "2.6/3.7", "未开始"],
  ["3.9", "学生端 H5", "移动端适配", "华心仪", "核心页面", "CSS 修正", "手机宽度不溢出", "H58-H66", "3.8", "未开始"],
  ["4.1", "教师/管理端 Web", "初始化 Vue 管理端", "胡钊炫", "原型样图", "frontend/admin/", "Vite 可启动", "H6-H8", "1.1", "未开始"],
  ["4.2", "教师/管理端 Web", "教师/管理员登录页", "胡钊炫", "M1 接口", "LoginView.vue", "教师、管理员可登录", "H8-H14", "4.1", "未开始"],
  ["4.3", "教师/管理端 Web", "管理端布局", "胡钊炫", "原型样图", "Layout、导航、路由", "审核和统计入口清晰", "H12-H18", "4.2", "未开始"],
  ["4.4", "教师/管理端 Web", "审核筛选栏", "胡钊炫", "M3 接口", "班级、日期、类型、状态筛选", "筛选条件可提交", "H18-H26", "4.3", "未开始"],
  ["4.5", "教师/管理端 Web", "审核列表", "胡钊炫", "M3 接口或 mock", "ReviewList.vue", "待审核记录展示完整", "H24-H34", "4.4", "未开始"],
  ["4.6", "教师/管理端 Web", "打卡详情面板", "胡钊炫", "M3 接口", "ReviewDetail.vue", "内容、定位、状态可见", "H30-H38", "4.5", "未开始"],
  ["4.7", "教师/管理端 Web", "通过/驳回操作", "胡钊炫", "M3 接口", "审核按钮和原因输入", "驳回必须填原因", "H36-H46", "4.6/2.7", "未开始"],
  ["4.8", "教师/管理端 Web", "统计概览页面", "胡钊炫", "M4 接口", "DashboardView.vue", "指标卡片正确展示", "H42-H54", "4.3/2.8", "未开始"],
  ["4.9", "教师/管理端 Web", "管理端联调", "胡钊炫", "后端接口", "可演示管理端", "审核和统计闭环通过", "H54-H66", "4.7/4.8", "未开始"],
  ["5.1", "联调与四环境验收", "第一次集成", "全员", "各模块骨架", "develop 可启动", "登录接口和两个前端启动", "H12", "2.1/3.1/4.1", "未开始"],
  ["5.2", "联调与四环境验收", "第二次集成", "全员", "打卡相关模块", "学生打卡闭环", "学生可提交打卡", "H24", "2.6/3.5", "未开始"],
  ["5.3", "联调与四环境验收", "第三次集成", "全员", "审核相关模块", "教师审核闭环", "教师可审核记录", "H36", "2.7/4.7", "未开始"],
  ["5.4", "联调与四环境验收", "第四次集成", "全员", "统计相关模块", "统计联调", "统计指标可展示", "H48", "2.8/4.8", "未开始"],
  ["5.5", "联调与四环境验收", "回归测试", "王韩韵", "缺陷清单", "缺陷闭环", "P0 缺陷为 0", "H60-H66", "5.4", "未开始"],
  ["5.6", "联调与四环境验收", "本地开发环境验收", "全员", "本地环境", "本地验收记录", "每人机器可启动", "H60-H66", "5.5", "未开始"],
  ["5.7", "联调与四环境验收", "服务器部署环境验收", "赵耀", "服务器环境", "服务器访问地址", "外部浏览器可访问", "H62-H68", "2.10", "未开始"],
  ["5.8", "联调与四环境验收", "用户验收环境演示", "王韩韵", "UAT 环境", "UAT 记录", "10 步验收脚本通过", "H66-H70", "5.6/5.7", "未开始"],
  ["5.9", "联调与四环境验收", "生产环境测试冒烟", "赵耀、王韩韵", "生产测试环境", "冒烟报告", "关键流程无阻塞", "H70-H72", "5.8", "未开始"],
];

const apis = [
  ["Auth", "POST", "/api/v1/auth/login", "学生端、管理端", "赵耀", "登录并返回 token 和用户信息", "Must"],
  ["Auth", "GET", "/api/v1/auth/me", "学生端、管理端", "赵耀", "获取当前用户", "Must"],
  ["Checkin", "GET", "/api/v1/checkins/today", "学生端", "赵耀", "获取今日三类打卡状态", "Must"],
  ["Checkin", "POST", "/api/v1/checkins", "学生端", "赵耀", "提交打卡", "Must"],
  ["Checkin", "GET", "/api/v1/checkins", "学生端", "赵耀", "获取本人历史记录", "Must"],
  ["Teacher", "GET", "/api/v1/teacher/checkins", "管理端", "赵耀", "教师筛选班级打卡列表", "Must"],
  ["Teacher", "POST", "/api/v1/teacher/reviews", "管理端", "赵耀", "提交通过/驳回审核", "Must"],
  ["Stats", "GET", "/api/v1/stats/overview", "管理端", "赵耀", "统计概览", "Must"],
];

const milestones = [
  ["H6", "需求和接口冻结", "王韩韵", "所有人确认 Must 范围", "未开始"],
  ["H12", "项目骨架可启动", "赵耀、胡钊炫、华心仪", "后端和两个前端均可启动", "未开始"],
  ["H24", "学生打卡最小闭环", "赵耀、华心仪", "学生可登录并提交打卡", "未开始"],
  ["H36", "教师审核最小闭环", "赵耀、胡钊炫", "教师可审核一条记录", "未开始"],
  ["H48", "统计概览可用", "赵耀、胡钊炫", "指标卡片返回真实数据", "未开始"],
  ["H60", "全流程联调完成", "全员", "验收脚本主路径通过", "未开始"],
  ["H72", "四环境验收", "王韩韵主导", "本地、服务器、UAT、生产测试完成记录", "未开始"],
];

const risks = [
  ["R1", "登录鉴权耗时过长", "高", "中", "阻塞前后端联调", "使用简单 Token 或固定演示账号", "赵耀", "开放"],
  ["R2", "定位 API 浏览器权限失败", "中", "中", "学生端打卡受阻", "允许手动 mock 经纬度并标记 unknown", "华心仪", "开放"],
  ["R3", "教师审核页面联调延迟", "中", "高", "管理闭环受阻", "使用 mock 列表先完成页面，后切真实接口", "胡钊炫", "开放"],
  ["R4", "统计接口复杂", "中", "中", "演示受阻", "只返回今日核心指标，不做复杂趋势计算", "赵耀", "开放"],
  ["R5", "服务器部署失败", "中", "高", "环境验收受阻", "先用本地局域网演示，同时记录部署缺陷", "王韩韵、赵耀", "开放"],
];

const acceptance = [
  [1, "学生账号登录", "学生端", "华心仪", "进入学生首页", "未开始"],
  [2, "学生查看今日三类打卡状态", "学生端", "华心仪", "查寝/上课/实习状态可见", "未开始"],
  [3, "学生提交查寝打卡", "学生端+后端", "华心仪、赵耀", "提交成功并进入待审核", "未开始"],
  [4, "学生重复提交查寝打卡", "学生端+后端", "华心仪、赵耀", "系统提示不可重复", "未开始"],
  [5, "教师账号登录", "管理端", "胡钊炫", "进入审核工作台", "未开始"],
  [6, "教师筛选今日查寝待审核记录", "管理端+后端", "胡钊炫、赵耀", "列表显示目标记录", "未开始"],
  [7, "教师打开学生打卡详情", "管理端", "胡钊炫", "内容、定位、状态可见", "未开始"],
  [8, "教师审核通过", "管理端+后端", "胡钊炫、赵耀", "审核状态更新", "未开始"],
  [9, "学生刷新历史记录", "学生端", "华心仪", "看到审核通过", "未开始"],
  [10, "管理员或教师进入统计页", "管理端+后端", "胡钊炫、赵耀", "打卡率、待审核数、异常数可见", "未开始"],
];

const dashboard = workbook.worksheets.add("总览仪表盘");
dashboard.showGridLines = false;
dashboard.getRange("A1:H1").merge();
dashboard.getRange("A1").values = [["知勤打卡系统 72 小时 MVP WBS 任务总览"]];
dashboard.getRange("A1").format = { fill: palette.navy, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
dashboard.getRange("A3:B8").values = [
  ["总任务数", wbs.length],
  ["Must 模块数", modules.filter((r) => r[4] === "Must").length],
  ["团队成员数", people.length],
  ["核心接口数", apis.length],
  ["里程碑数", milestones.length],
  ["开放风险数", risks.length],
];
dashboard.getRange("A3:B8").format = { borders: { preset: "all", style: "thin", color: palette.border }, verticalAlignment: "center" };
dashboard.getRange("A3:A8").format = { fill: palette.header, font: { bold: true } };
dashboard.getRange("B3:B8").format = { font: { bold: true, color: palette.blue }, horizontalAlignment: "center" };
dashboard.getRange("D3:H3").values = [["成员", "Owner 模块", "关键交付", "主要目录", "验收口径"]];
dashboard.getRange("D4:H7").values = people.map((p) => [p[0], p[1], p[3], p[2], p[6]]);
dashboard.getRange("D3:H7").format = { borders: { preset: "all", style: "thin", color: palette.border }, wrapText: true, verticalAlignment: "center" };
dashboard.getRange("D3:H3").format = { fill: palette.header, font: { bold: true }, horizontalAlignment: "center" };
dashboard.getRange("A10:H10").merge();
dashboard.getRange("A10").values = [["使用说明：各成员只维护自己的 Owner 目录；跨模块变更必须先更新 API 契约并通过 PR Review。"]];
dashboard.getRange("A10").format = { fill: palette.lightAmber, font: { color: "#92400E" }, wrapText: true };
["A", "B", "D", "E", "F", "G", "H"].forEach((c, i) => {
  const widths = { A: 18, B: 14, D: 12, E: 20, F: 42, G: 28, H: 32 };
  dashboard.getRange(`${c}:${c}`).format.columnWidth = widths[c];
});

addSheet("模块清单", "模块清单", ["模块编号", "模块名称", "负责人", "协作人", "优先级", "核心范围", "Owner 目录/文件", "验收标准", "状态"], modules, [10, 20, 18, 20, 10, 38, 34, 38, 12]);
addSheet("人员分工", "人员分工", ["成员", "角色", "Owner 目录", "负责事项", "禁止直接修改", "关键时间", "验收口径"], people, [12, 24, 24, 42, 32, 20, 30]);
addSheet("WBS明细", "WBS 明细任务表", ["WBS", "工作包", "任务", "负责人", "输入", "输出", "验收标准", "时间", "依赖", "状态"], wbs, [8, 22, 30, 14, 24, 36, 34, 18, 20, 12]);
addSheet("接口清单", "最小 API 接口清单", ["模块", "方法", "路径", "调用方", "负责人", "说明", "优先级"], apis, [12, 10, 34, 22, 12, 38, 10]);
addSheet("里程碑", "72 小时里程碑", ["时间点", "里程碑", "负责人", "判断标准", "状态"], milestones, [10, 28, 24, 44, 12]);
addSheet("风险清单", "风险与降级策略", ["风险编号", "风险", "概率", "影响", "业务影响", "降级策略", "负责人", "状态"], risks, [10, 26, 10, 10, 32, 42, 18, 12]);
addSheet("验收脚本", "10 步验收脚本", ["步骤", "动作", "范围", "负责人", "通过标准", "状态"], acceptance, [8, 32, 20, 20, 40, 12]);

for (const sheet of workbook.worksheets.items) {
  const used = sheet.getUsedRange();
  used.format.font = { name: "Microsoft YaHei", size: 10 };
  used.format.wrapText = true;
  used.format.verticalAlignment = "center";
}

const statusValues = ["未开始", "进行中", "已完成", "阻塞"];
for (const [sheetName, col, rows] of [
  ["模块清单", "I", modules.length],
  ["WBS明细", "J", wbs.length],
  ["里程碑", "E", milestones.length],
  ["验收脚本", "F", acceptance.length],
]) {
  const sheet = workbook.worksheets.getItem(sheetName);
  sheet.getRange(`${col}3:${col}${rows + 2}`).dataValidation = { rule: { type: "list", values: statusValues } };
}
workbook.worksheets.getItem("风险清单").getRange(`H3:H${risks.length + 2}`).dataValidation = { rule: { type: "list", values: ["开放", "处理中", "已关闭"] } };

await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ["总览仪表盘", "WBS明细", "风险清单"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
