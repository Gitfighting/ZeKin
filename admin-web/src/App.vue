<script setup>
const metrics = [
  { label: "今日打卡率", value: "86%", tone: "success" },
  { label: "未打卡人数", value: "12", tone: "error" },
  { label: "待审核数量", value: "18", tone: "warning" },
  { label: "连续打卡最高", value: "21天", tone: "primary" },
];

const records = [
  { name: "王同学", className: "软件一班", type: "查寝", status: "待审核", time: "09:30" },
  { name: "赵同学", className: "软件二班", type: "上课", status: "已通过", time: "10:12" },
  { name: "胡同学", className: "软件一班", type: "实习", status: "已拒绝", time: "11:05" },
];
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">知勤打卡</div>
      <nav>
        <a class="active">数据看板</a>
        <a>打卡记录</a>
        <a>用户管理</a>
        <a>系统日志</a>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <input placeholder="搜索学生、班级、request_id" />
        <span class="user">Admin · local</span>
      </header>
      <section class="content">
        <div class="page-title">
          <h1>数据看板</h1>
          <button>刷新</button>
        </div>
        <div class="metrics">
          <article v-for="item in metrics" :key="item.label" class="metric">
            <span>{{ item.label }}</span>
            <strong :class="item.tone">{{ item.value }}</strong>
          </article>
        </div>
        <div class="panel-grid">
          <section class="panel">
            <h2>打卡趋势</h2>
            <div class="chart-placeholder">近 7 日趋势图占位</div>
          </section>
          <section class="panel">
            <h2>类型分布</h2>
            <div class="chart-placeholder">查寝 48% · 上课 36% · 实习 16%</div>
          </section>
        </div>
        <section class="panel">
          <h2>最近打卡记录</h2>
          <table>
            <thead>
              <tr>
                <th>学生</th>
                <th>班级</th>
                <th>类型</th>
                <th>状态</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in records" :key="record.name">
                <td>{{ record.name }}</td>
                <td>{{ record.className }}</td>
                <td>{{ record.type }}</td>
                <td><span class="status">{{ record.status }}</span></td>
                <td class="mono">{{ record.time }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </section>
    </main>
  </div>
</template>
