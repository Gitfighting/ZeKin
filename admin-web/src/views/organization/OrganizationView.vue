<script setup lang="ts">
import { reactive, ref } from 'vue'

import OrgTree, { type OrgTreeNode } from '../../components/OrgTree/OrgTree.vue'

const tree = ref<OrgTreeNode[]>([
  {
    id: 1,
    label: '信息工程学院',
    type: '学院',
    children: [
      {
        id: 2,
        label: '2024级软件工程',
        type: '专业',
        children: [
          { id: 3, label: '软工 1 班', type: '班级' },
          { id: 4, label: '软工 2 班', type: '班级' },
        ],
      },
    ],
  },
  {
    id: 5,
    label: '马克思主义学院',
    type: '学院',
    children: [{ id: 6, label: '2024级思政教育', type: '专业' }],
  },
])

const form = reactive({
  name: '软工 1 班',
  type: '班级',
  principal: '张老师',
  description: '默认承担晨读与晚自习打卡任务。',
})

const handleSelect = (node: OrgTreeNode) => {
  form.name = node.label
  form.type = node.type
}
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>组织管理</h1>
        <p>按学院到班级维护组织层级，并配置管理责任人。</p>
      </div>
      <el-button type="primary">新增组织</el-button>
    </div>

    <div class="split-layout">
      <OrgTree :data="tree" @select="handleSelect" />

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
            <el-button type="primary">保存</el-button>
            <el-button>新增下级</el-button>
          </el-space>
        </el-form>
      </el-card>
    </div>
  </section>
</template>
