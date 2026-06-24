<script setup lang="ts">
import { ref } from 'vue'

import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

interface TypeRow extends Record<string, unknown> {
  id: number
  name: string
  code: string
  enabled: boolean
}

const rows = ref<TypeRow[]>([
  { id: 1, name: '晨读签到', code: 'MORNING_READ', enabled: true },
  { id: 2, name: '晚自习签到', code: 'EVENING_STUDY', enabled: true },
  { id: 3, name: '临时活动签到', code: 'TEMP_EVENT', enabled: false },
])

const columns: DataColumn<TypeRow>[] = [
  { key: 'name', label: '名称', minWidth: 180 },
  { key: 'code', label: '编码', minWidth: 180 },
  { key: 'enabled', label: '启用状态', minWidth: 120 },
]
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>打卡类型</h1>
        <p>统一维护名称与编码，控制可用状态。</p>
      </div>
      <el-button type="primary">新增类型</el-button>
    </div>

    <el-card>
      <DataTable :columns="columns" :rows="rows">
        <template #enabled="{ row }">
          <div class="switch-cell">
            <el-switch v-model="row.enabled" />
            <span>{{ row.enabled ? '启用中' : '已停用' }}</span>
          </div>
        </template>
      </DataTable>
    </el-card>
  </section>
</template>

<style scoped lang="scss">
.switch-cell {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
</style>
