<script setup>
import { computed, onMounted, reactive, ref } from "vue";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const activePage = ref("dashboard");
const loading = ref(false);
const message = ref("");
const token = ref(localStorage.getItem("zekin_admin_token") || "");
const currentUser = ref(JSON.parse(localStorage.getItem("zekin_admin_user") || "null"));
const loginForm = reactive({ username: "admin_demo", password: "Passw0rd!" });
const filters = reactive({ keyword: "", status: "", role: "" });
const stats = ref(null);
const checkins = ref([]);
const users = ref([]);

const navItems = [
  { key: "dashboard", label: "数据看板" },
  { key: "checkins", label: "打卡记录" },
  { key: "users", label: "用户管理" },
  { key: "logs", label: "系统日志" },
];

const metrics = computed(() => [
  { label: "今日打卡率", value: `${Math.round((stats.value?.checkin_rate || 0) * 100)}%`, tone: "success" },
  { label: "未打卡人数", value: stats.value?.missing_students ?? 0, tone: "error" },
  { label: "待审核数量", value: stats.value?.pending_checkins ?? 0, tone: "warning" },
  { label: "连续打卡最高", value: `${stats.value?.max_streak_days ?? 0}天`, tone: "primary" },
]);

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Client": "admin-web",
      ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
      ...(options.headers || {}),
    },
  });
  const body = await response.json().catch(() => ({ message: "服务响应异常" }));
  if (!response.ok) {
    throw new Error(body.message || "请求失败");
  }
  return body.data;
}

async function seedDemoData() {
  loading.value = true;
  message.value = "";
  try {
    const accounts = [
      {
        username: "admin_demo",
        password: "Passw0rd!",
        real_name: "管理员",
        role: "admin",
        class_name: "校级",
        phone: "13910000001",
      },
      {
        username: "student_demo",
        password: "Passw0rd!",
        real_name: "王同学",
        role: "student",
        class_name: "软件一班",
        phone: "13910000002",
      },
      {
        username: "teacher_demo",
        password: "Passw0rd!",
        real_name: "华老师",
        role: "teacher",
        class_name: "软件一班",
        phone: "13910000003",
      },
    ];
    for (const account of accounts) {
      await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Client": "admin-web" },
        body: JSON.stringify(account),
      });
    }
    message.value = "演示账号已准备好，可以登录。";
  } catch (error) {
    message.value = error.message;
  } finally {
    loading.value = false;
  }
}

async function login() {
  loading.value = true;
  message.value = "";
  try {
    const data = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(loginForm),
    });
    if (data.user.role !== "admin") {
      throw new Error("当前账号不是管理员");
    }
    token.value = data.access_token;
    currentUser.value = data.user;
    localStorage.setItem("zekin_admin_token", token.value);
    localStorage.setItem("zekin_admin_user", JSON.stringify(data.user));
    await refreshAll();
  } catch (error) {
    message.value = error.message;
  } finally {
    loading.value = false;
  }
}

function logout() {
  token.value = "";
  currentUser.value = null;
  localStorage.removeItem("zekin_admin_token");
  localStorage.removeItem("zekin_admin_user");
}

async function refreshAll() {
  await Promise.all([loadStats(), loadCheckins(), loadUsers()]);
}

async function loadStats() {
  stats.value = await request("/api/stats/overview");
}

async function loadCheckins() {
  const params = new URLSearchParams();
  if (filters.keyword) params.set("keyword", filters.keyword);
  if (filters.status) params.set("status", filters.status);
  const data = await request(`/api/admin/checkins?${params.toString()}`);
  checkins.value = data.items;
}

async function loadUsers() {
  const params = new URLSearchParams();
  if (filters.keyword) params.set("keyword", filters.keyword);
  if (filters.role) params.set("role", filters.role);
  const data = await request(`/api/admin/users?${params.toString()}`);
  users.value = data.items;
}

async function refreshCurrent() {
  loading.value = true;
  message.value = "";
  try {
    if (activePage.value === "dashboard") await refreshAll();
    if (activePage.value === "checkins") await loadCheckins();
    if (activePage.value === "users") await loadUsers();
    message.value = "数据已刷新。";
  } catch (error) {
    message.value = error.message;
  } finally {
    loading.value = false;
  }
}

function statusText(status) {
  return { pending: "待审核", approved: "已通过", rejected: "已拒绝" }[status] || status;
}

function typeText(type) {
  return { dorm: "查寝", class: "上课", internship: "实习" }[type] || type;
}

onMounted(async () => {
  if (token.value) {
    try {
      await refreshAll();
    } catch (error) {
      message.value = error.message;
    }
  }
});
</script>

<template>
  <div v-if="!token" class="login-page">
    <section class="login-panel">
      <h1>知勤打卡 Admin</h1>
      <p>管理端连接同一个后端数据库，可查看学生和教师端产生的数据。</p>
      <label>账号</label>
      <input v-model="loginForm.username" placeholder="admin_demo" />
      <label>密码</label>
      <input v-model="loginForm.password" type="password" placeholder="Passw0rd!" />
      <div class="button-row">
        <button :disabled="loading" @click="login">登录</button>
        <button class="outline" :disabled="loading" @click="seedDemoData">准备演示账号</button>
      </div>
      <p v-if="message" class="notice">{{ message }}</p>
    </section>
  </div>

  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">知勤打卡</div>
      <nav>
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="{ active: activePage === item.key }"
          @click="activePage = item.key"
        >
          {{ item.label }}
        </button>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <input v-model="filters.keyword" placeholder="搜索学生、班级、手机号" @keyup.enter="refreshCurrent" />
        <div class="top-actions">
          <span class="user">{{ currentUser?.real_name }} · local</span>
          <button class="outline" @click="logout">退出</button>
        </div>
      </header>
      <section class="content">
        <div class="page-title">
          <h1>{{ navItems.find((item) => item.key === activePage)?.label }}</h1>
          <div class="button-row">
            <button class="outline" @click="seedDemoData">补演示数据</button>
            <button :disabled="loading" @click="refreshCurrent">刷新</button>
          </div>
        </div>
        <p v-if="message" class="notice">{{ message }}</p>

        <template v-if="activePage === 'dashboard'">
          <div class="metrics">
            <article v-for="item in metrics" :key="item.label" class="metric">
              <span>{{ item.label }}</span>
              <strong :class="item.tone">{{ item.value }}</strong>
            </article>
          </div>
          <div class="panel-grid">
            <section class="panel">
              <h2>打卡趋势</h2>
              <div class="chart-placeholder">当前总打卡 {{ stats?.total_checkins ?? 0 }} 条</div>
            </section>
            <section class="panel">
              <h2>类型分布</h2>
              <div class="chart-placeholder">查寝 / 上课 / 实习来自同一张 checkins 表</div>
            </section>
          </div>
        </template>

        <section v-if="activePage === 'dashboard' || activePage === 'checkins'" class="panel">
          <div class="panel-title">
            <h2>打卡记录</h2>
            <select v-model="filters.status" @change="loadCheckins">
              <option value="">全部状态</option>
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>
          <table>
            <thead>
              <tr>
                <th>学生</th>
                <th>班级</th>
                <th>类型</th>
                <th>内容</th>
                <th>状态</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="checkins.length === 0">
                <td colspan="6" class="empty">暂无打卡记录，先到学生端提交一条。</td>
              </tr>
              <tr v-for="record in checkins" :key="record.id">
                <td>{{ record.student_name }}</td>
                <td>{{ record.class_name }}</td>
                <td>{{ typeText(record.type) }}</td>
                <td>{{ record.content }}</td>
                <td><span class="status">{{ statusText(record.status) }}</span></td>
                <td class="mono">{{ record.created_at?.slice(0, 16).replace('T', ' ') }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section v-if="activePage === 'users'" class="panel">
          <div class="panel-title">
            <h2>用户管理</h2>
            <select v-model="filters.role" @change="loadUsers">
              <option value="">全部角色</option>
              <option value="student">学生</option>
              <option value="teacher">教师</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <table>
            <thead>
              <tr>
                <th>姓名</th>
                <th>账号</th>
                <th>手机号</th>
                <th>角色</th>
                <th>班级</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="users.length === 0">
                <td colspan="5" class="empty">暂无用户。</td>
              </tr>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.real_name }}</td>
                <td class="mono">{{ user.username }}</td>
                <td>{{ user.phone }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.class_name }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section v-if="activePage === 'logs'" class="panel">
          <h2>系统日志</h2>
          <div class="chart-placeholder">MVP 阶段先通过后端结构化日志文件排查，日志查询接口进入 V1.1。</div>
        </section>
      </section>
    </main>
  </div>
</template>
