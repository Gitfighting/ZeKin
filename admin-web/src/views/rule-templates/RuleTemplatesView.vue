<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getRuleTemplates, type RuleTemplateRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError, showWarning } from '../../utils/feedback'

const rows = ref<RuleTemplateRow[]>([])
const loading = ref(false)

const columns: DataColumn<RuleTemplateRow>[] = [
  { key: 'name', label: '模板名称', minWidth: 180 },
  { key: 'typeId', label: '打卡类型ID', minWidth: 120 },
  { key: 'ruleCount', label: '规则项数量', minWidth: 120 },
]

async function loadRuleTemplates() {
  loading.value = true
  try {
    rows.value = (await getRuleTemplates()).items
    logInfo('规则模板加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '规则模板加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadRuleTemplates)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>规则模板</h1>
        <p>围绕时间、位置、验证、审核与提醒配置统一模板。</p>
      </div>
      <el-space>
        <el-button @click="showWarning('规则模板另存接口暂未接入')">另存为模板</el-button>
        <el-button type="primary" @click="showWarning('规则模板发布接口暂未接入')">发布模板</el-button>
      </el-space>
    </div>

    <el-card>
      <DataTable :columns="columns" :rows="rows" :loading="loading" />
    </el-card>
  </section>
</template>
