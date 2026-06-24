<script setup lang="ts">
import { computed, ref } from 'vue'

import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

type GroupTab = '行政班' | '教学组' | '专项分组'

interface MemberRow extends Record<string, unknown> {
  id: number
  name: string
  role: string
  attendance: string
}

interface TeacherRow extends Record<string, unknown> {
  id: number
  name: string
  responsibility: string
}

const activeTab = ref<GroupTab>('行政班')

const memberColumns: DataColumn<MemberRow>[] = [
  { key: 'name', label: '成员姓名' },
  { key: 'role', label: '角色' },
  { key: 'attendance', label: '最近出勤' },
]

const teacherColumns: DataColumn<TeacherRow>[] = [
  { key: 'name', label: '教师姓名' },
  { key: 'responsibility', label: '负责范围' },
]

const groupData: Record<GroupTab, { members: MemberRow[]; teachers: TeacherRow[] }> = {
  行政班: {
    members: [
      { id: 1, name: '李晨', role: '班长', attendance: '96%' },
      { id: 2, name: '王宁', role: '学生', attendance: '89%' },
    ],
    teachers: [
      { id: 1, name: '张明', responsibility: '晨读与晚签' },
      { id: 2, name: '陈雪', responsibility: '定位异常复核' },
    ],
  },
  教学组: {
    members: [
      { id: 3, name: '周岚', role: '学习委员', attendance: '94%' },
      { id: 4, name: '赵航', role: '学生', attendance: '91%' },
    ],
    teachers: [
      { id: 3, name: '刘倩', responsibility: '课程实践签到' },
    ],
  },
  专项分组: {
    members: [
      { id: 5, name: '陈一', role: '组长', attendance: '98%' },
      { id: 6, name: '林悦', role: '学生', attendance: '93%' },
    ],
    teachers: [
      { id: 4, name: '黄敏', responsibility: '活动现场复核' },
    ],
  },
}

const visibleMembers = computed(() => groupData[activeTab.value].members)
const visibleTeachers = computed(() => groupData[activeTab.value].teachers)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>班级与分组</h1>
        <p>按组织场景切换分组类型，查看成员与教师配置。</p>
      </div>
      <el-button type="primary">新增分组</el-button>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="行政班" name="行政班" />
        <el-tab-pane label="教学组" name="教学组" />
        <el-tab-pane label="专项分组" name="专项分组" />
      </el-tabs>
    </el-card>

    <div class="two-column">
      <el-card :header="`${activeTab}成员`">
        <DataTable :columns="memberColumns" :rows="visibleMembers" />
      </el-card>
      <el-card :header="`${activeTab}负责教师`">
        <DataTable :columns="teacherColumns" :rows="visibleTeachers" />
      </el-card>
    </div>
  </section>
</template>
