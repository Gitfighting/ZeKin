<script setup lang="ts">
const stats = [
  { label: '任务总数', value: '28', suffix: '项' },
  { label: '今日完成率', value: '92', suffix: '%' },
  { label: '异常数量', value: '11', suffix: '条' },
  { label: '待处理申诉', value: '4', suffix: '条' },
]
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>工作台</h1>
        <p>集中查看今日任务完成情况与例外波动。</p>
      </div>
      <el-button type="primary">刷新概览</el-button>
    </div>

    <div class="stat-grid">
      <el-card v-for="item in stats" :key="item.label">
        <template #header>{{ item.label }}</template>
        <div class="stat-card">
          <strong>{{ item.value }}</strong>
          <span>{{ item.suffix }}</span>
        </div>
      </el-card>
    </div>

    <div class="two-column">
      <el-card header="今日提醒">
        <el-timeline>
          <el-timeline-item timestamp="08:30" type="primary">早签到任务已下发</el-timeline-item>
          <el-timeline-item timestamp="11:20" type="warning">出现 5 条定位例外记录</el-timeline-item>
          <el-timeline-item timestamp="14:00" type="success">晨读模板完成率保持稳定</el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card header="系统状态">
        <div class="dashboard-note sz-card">
          <strong>导航、布局与登录基线已就绪</strong>
          <p>后续页面将在此基础上接入组织、人员、规则与任务监管内容。</p>
        </div>
      </el-card>
    </div>
  </section>
</template>

<style scoped lang="scss">
.stat-card {
  display: flex;
  align-items: flex-end;
  gap: 6px;

  strong {
    font-size: 32px;
    line-height: 1;
    color: var(--sz-primary);
  }

  span {
    color: var(--sz-muted);
    padding-bottom: 4px;
  }
}

.dashboard-note {
  padding: 16px;

  strong {
    display: block;
    margin-bottom: 8px;
  }

  p {
    margin: 0;
    color: var(--sz-muted);
    line-height: 1.6;
  }
}
</style>
