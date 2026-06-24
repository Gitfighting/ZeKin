<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getTeachers, type TeacherRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

const createVisible = ref(false)
const groupDrawerVisible = ref(false)
const currentTeacher = ref<TeacherRow | null>(null)
const loading = ref(false)

const rows = ref<TeacherRow[]>([])

const columns: DataColumn<TeacherRow>[] = [
  { key: 'name', label: '姓名', minWidth: 120 },
  { key: 'department', label: '所属部门', minWidth: 160 },
  { key: 'phone', label: '联系电话', minWidth: 140 },
  {
    key: 'groups',
    label: '关联分组',
    minWidth: 220,
    formatter: (row) => row.groups.join(' / '),
  },
]

const openGroups = (row: TeacherRow) => {
  currentTeacher.value = { ...row }
  groupDrawerVisible.value = true
}

onMounted(async () => {
  loading.value = true
  try {
    rows.value = (await getTeachers()).items
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>教师管理</h1>
        <p>维护教师主体信息，并绑定其负责班级与分组。</p>
      </div>
      <el-button type="primary" @click="createVisible = true">新增教师</el-button>
    </div>

    <el-card>
      <DataTable :columns="columns" :rows="rows" :loading="loading">
        <template #groups="{ row }">
          <div class="teacher-groups">
            <span>{{ row.groups.join(' / ') }}</span>
            <el-button text type="primary" @click="openGroups(row)">关联分组</el-button>
          </div>
        </template>
      </DataTable>
    </el-card>

    <el-dialog v-model="createVisible" title="新增教师" width="520px">
      <el-form label-position="top">
        <div class="two-column">
          <el-form-item label="姓名">
            <el-input />
          </el-form-item>
          <el-form-item label="部门">
            <el-select>
              <el-option label="信息工程学院" value="信息工程学院" />
              <el-option label="马克思主义学院" value="马克思主义学院" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="联系电话">
          <el-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="createVisible = false">创建</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="groupDrawerVisible" title="关联分组" size="420px">
      <template v-if="currentTeacher">
        <p class="drawer-note">{{ currentTeacher.name }} 当前负责 {{ currentTeacher.groups.length }} 个分组</p>
        <el-checkbox-group>
          <el-checkbox label="软工 1 班">软工 1 班</el-checkbox>
          <el-checkbox label="软工 2 班">软工 2 班</el-checkbox>
          <el-checkbox label="思政 1 班">思政 1 班</el-checkbox>
          <el-checkbox label="晚自习专项组">晚自习专项组</el-checkbox>
        </el-checkbox-group>
      </template>
    </el-drawer>
  </section>
</template>

<style scoped lang="scss">
.teacher-groups {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.drawer-note {
  margin: 0 0 16px;
  color: var(--sz-muted);
}
</style>
