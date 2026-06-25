<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getGroups, type GroupRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError, showWarning } from '../../utils/feedback'

type GroupTab = '行政班' | '教学组' | '专项分组'

const activeTab = ref<GroupTab>('行政班')

const groupColumns: DataColumn<GroupRow>[] = [
  { key: 'name', label: '分组名称' },
  { key: 'groupType', label: '类型' },
  { key: 'studentCount', label: '学生数' },
  { key: 'teacherCount', label: '负责教师数' },
]

const rows = ref<GroupRow[]>([])
const loading = ref(false)

const visibleGroups = computed(() => {
  if (activeTab.value === '行政班') return rows.value.filter((row) => row.groupType === 'class')
  return rows.value.filter((row) => row.groupType !== 'class')
})

async function loadGroups() {
  loading.value = true
  try {
    rows.value = (await getGroups()).items
    logInfo('班级与分组列表加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '班级与分组列表加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadGroups)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>班级与分组</h1>
        <p>按组织场景切换分组类型，查看成员与教师配置。</p>
      </div>
      <el-button type="primary" @click="showWarning('新增分组接口暂未接入')">新增分组</el-button>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="行政班" name="行政班" />
        <el-tab-pane label="教学组" name="教学组" />
        <el-tab-pane label="专项分组" name="专项分组" />
      </el-tabs>
    </el-card>

    <el-card :header="`${activeTab}列表`">
      <DataTable :columns="groupColumns" :rows="visibleGroups" :loading="loading" />
    </el-card>
  </section>
</template>
