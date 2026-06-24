<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'
import { computed, reactive, ref } from 'vue'

import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

interface StudentRow extends Record<string, unknown> {
  id: number
  name: string
  studentNo: string
  className: string
  status: '已启用' | '待激活'
  counselor: string
}

const search = reactive({
  name: '',
  studentNo: '',
  className: '',
})

const importVisible = ref(false)
const drawerVisible = ref(false)
const editingStudent = ref<StudentRow | null>(null)
const importForm = reactive({
  fileName: 'students-2026.xlsx',
  mode: 'merge' as 'merge' | 'overwrite',
  lastSubmittedMode: '',
})

const rows = ref<StudentRow[]>([
  { id: 1, name: '李晨', studentNo: '20240101', className: '软工 1 班', status: '已启用', counselor: '张老师' },
  { id: 2, name: '王宁', studentNo: '20240102', className: '软工 2 班', status: '待激活', counselor: '陈老师' },
  { id: 3, name: '周岚', studentNo: '20240103', className: '思政 1 班', status: '已启用', counselor: '赵老师' },
])

const columns: DataColumn<StudentRow>[] = [
  { key: 'name', label: '姓名', minWidth: 120 },
  { key: 'studentNo', label: '学号', minWidth: 150 },
  { key: 'className', label: '班级', minWidth: 150 },
  { key: 'status', label: '激活状态', minWidth: 120 },
  { key: 'counselor', label: '辅导员', minWidth: 120 },
]

const filteredRows = computed(() =>
  rows.value.filter((row) =>
    [search.name, search.studentNo, search.className].every((keyword, index) => {
      if (!keyword) return true
      const fields = [row.name, row.studentNo, row.className]
      return fields[index].includes(keyword)
    }),
  ),
)

const openEditor = (row: StudentRow) => {
  editingStudent.value = { ...row }
  drawerVisible.value = true
}

const confirmImport = () => {
  importForm.lastSubmittedMode = importForm.mode
  importVisible.value = false
}
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>学生管理</h1>
        <p>支持名单导入、激活状态查看与个人信息维护。</p>
      </div>
      <el-space>
        <el-button @click="importVisible = true">批量导入</el-button>
        <el-button type="primary">新增学生</el-button>
      </el-space>
    </div>

    <el-card>
      <div class="toolbar-grid">
        <el-input v-model="search.name" placeholder="按姓名搜索" :prefix-icon="Search" />
        <el-input v-model="search.studentNo" placeholder="按学号搜索" />
        <el-input v-model="search.className" placeholder="按班级搜索" />
      </div>
    </el-card>

    <el-card>
      <DataTable :columns="columns" :rows="filteredRows">
        <template #status="{ row }">
          <el-tag :type="row.status === '已启用' ? 'success' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
        <template #counselor="{ row }">
          <div class="table-action">
            <span>{{ row.counselor }}</span>
            <el-button text type="primary" @click="openEditor(row)">编辑</el-button>
          </div>
        </template>
      </DataTable>
    </el-card>

    <el-dialog v-model="importVisible" title="导入学生">
      <el-form label-position="top">
        <el-form-item label="导入文件">
          <el-input v-model="importForm.fileName" readonly />
        </el-form-item>
        <el-form-item label="处理方式">
          <el-radio-group v-model="importForm.mode">
            <el-radio value="merge">保留现有并增量导入</el-radio>
            <el-radio value="overwrite">覆盖同学号记录</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-alert
          v-if="importForm.lastSubmittedMode"
          type="success"
          show-icon
          :closable="false"
          :title="`已记录导入方式：${importForm.lastSubmittedMode === 'overwrite' ? '覆盖同学号记录' : '增量导入'}`"
        />
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">开始导入</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="drawerVisible" title="编辑学生档案" size="420px">
      <el-form v-if="editingStudent" label-position="top">
        <el-form-item label="姓名">
          <el-input v-model="editingStudent.name" />
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="editingStudent.className" />
        </el-form-item>
        <el-form-item label="辅导员">
          <el-input v-model="editingStudent.counselor" />
        </el-form-item>
      </el-form>
    </el-drawer>
  </section>
</template>

<style scoped lang="scss">
.table-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
</style>
