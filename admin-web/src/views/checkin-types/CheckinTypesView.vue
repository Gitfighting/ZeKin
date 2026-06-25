<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getCheckinTypes, type CheckinTypeRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError, showWarning } from '../../utils/feedback'

const rows = ref<CheckinTypeRow[]>([])
const loading = ref(false)

const columns: DataColumn<CheckinTypeRow>[] = [
  { key: 'name', label: '名称', minWidth: 180 },
  { key: 'description', label: '说明', minWidth: 220 },
]

async function loadCheckinTypes() {
  loading.value = true
  try {
    rows.value = (await getCheckinTypes()).items
    logInfo('打卡类型加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '打卡类型加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadCheckinTypes)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>打卡类型</h1>
        <p>统一维护名称与编码，控制可用状态。</p>
      </div>
      <el-button type="primary" @click="showWarning('新增打卡类型接口暂未接入')">新增类型</el-button>
    </div>

    <el-card>
      <DataTable :columns="columns" :rows="rows" :loading="loading" />
    </el-card>
  </section>
</template>
