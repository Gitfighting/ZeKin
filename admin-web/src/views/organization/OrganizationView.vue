<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { getOrgTree } from '../../api/admin'
import OrgTree, { type OrgTreeNode } from '../../components/OrgTree/OrgTree.vue'
import { logInfo, showError, showWarning } from '../../utils/feedback'

const tree = ref<OrgTreeNode[]>([])
const loading = ref(false)

const form = reactive({
  name: '',
  type: '',
  principal: '',
  description: '',
})

const handleSelect = (node: OrgTreeNode) => {
  form.name = node.label
  form.type = node.type
}

async function loadOrgTree() {
  loading.value = true
  try {
    tree.value = await getOrgTree()
    logInfo('组织树加载成功', { count: tree.value.length })
  } catch (error) {
    tree.value = []
    showError(error, '组织树加载失败')
  } finally {
    loading.value = false
  }
}

function notifyUnwired() {
  showWarning('组织编辑接口暂未接入')
}

onMounted(loadOrgTree)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>组织管理</h1>
        <p>按学院到班级维护组织层级，并配置管理责任人。</p>
      </div>
      <el-button type="primary" @click="notifyUnwired">新增组织</el-button>
    </div>

    <div class="split-layout">
      <OrgTree v-if="tree.length > 0" :data="tree" @select="handleSelect" />
      <el-card v-else v-loading="loading">
        <el-empty description="暂无组织数据" />
      </el-card>

      <el-card header="组织信息编辑">
        <el-form label-position="top">
          <div class="two-column">
            <el-form-item label="组织名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="组织类型">
              <el-select v-model="form.type">
                <el-option label="学院" value="学院" />
                <el-option label="专业" value="专业" />
                <el-option label="班级" value="班级" />
              </el-select>
            </el-form-item>
          </div>
          <el-form-item label="负责人">
            <el-input v-model="form.principal" />
          </el-form-item>
          <el-form-item label="管理说明">
            <el-input v-model="form.description" type="textarea" :rows="5" resize="none" />
          </el-form-item>
          <el-space>
            <el-button type="primary" @click="notifyUnwired">保存</el-button>
            <el-button @click="notifyUnwired">新增下级</el-button>
          </el-space>
        </el-form>
      </el-card>
    </div>
  </section>
</template>
