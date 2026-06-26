<script setup lang="ts">
import { Camera, Search, UploadFilled } from '@element-plus/icons-vue'
import { computed, onMounted, reactive, ref } from 'vue'

import { getStudents, registerStudentFace, type StudentRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError, showWarning } from '../../utils/feedback'

const search = reactive({
  name: '',
  studentNo: '',
  className: '',
})

const importVisible = ref(false)
const drawerVisible = ref(false)
const editingStudent = ref<StudentRow | null>(null)
const faceDialogVisible = ref(false)
const faceStudent = ref<StudentRow | null>(null)
const faceFile = ref<File | null>(null)
const faceUploading = ref(false)
const importForm = reactive({
  fileName: '',
  mode: 'merge' as 'merge' | 'overwrite',
})

const loading = ref(false)
const rows = ref<StudentRow[]>([])

const columns: DataColumn<StudentRow>[] = [
  { key: 'name', label: '姓名', minWidth: 120 },
  { key: 'studentNo', label: '学号', minWidth: 150 },
  { key: 'className', label: '班级', minWidth: 150 },
  { key: 'status', label: '激活状态', minWidth: 120 },
  { key: 'faceRegistered', label: '人脸状态', minWidth: 130 },
  { key: 'counselor', label: '辅导员', minWidth: 120 },
  { key: 'actions', label: '操作', minWidth: 150 },
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
  showWarning('批量导入文件解析接口暂未接入')
}

const openFaceDialog = (row: StudentRow) => {
  faceStudent.value = row
  faceFile.value = null
  faceDialogVisible.value = true
}

const beforeFaceUpload = (file: File) => {
  faceFile.value = file
  return false
}

async function submitFaceUpload() {
  if (!faceStudent.value || !faceFile.value) {
    showWarning('请先选择一张正面人脸照片')
    return
  }

  faceUploading.value = true
  try {
    await registerStudentFace(faceStudent.value.id, faceFile.value)
    logInfo('学生人脸录入成功', {
      studentId: faceStudent.value.id,
      studentNo: faceStudent.value.studentNo,
    })
    faceDialogVisible.value = false
    await loadStudents()
  } catch (error) {
    showError(error, '人脸录入失败')
  } finally {
    faceUploading.value = false
  }
}

async function loadStudents() {
  loading.value = true
  try {
    rows.value = (await getStudents()).items
    logInfo('学生列表加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '学生列表加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadStudents)
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
        <el-button type="primary" @click="showWarning('新增学生接口暂未接入')">新增学生</el-button>
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
      <DataTable :columns="columns" :rows="filteredRows" :loading="loading">
        <template #status="{ row }">
          <el-tag :type="row.status === '已启用' ? 'success' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
        <template #faceRegistered="{ row }">
          <el-tag :type="row.faceRegistered ? 'success' : 'info'">
            {{ row.faceRegistered ? '已录入' : '未录入' }}
          </el-tag>
        </template>
        <template #counselor="{ row }">
          <div class="table-action">
            <span>{{ row.counselor }}</span>
            <el-button text type="primary" @click="openEditor(row)">编辑</el-button>
          </div>
        </template>
        <template #actions="{ row }">
          <el-button :icon="Camera" text type="primary" @click="openFaceDialog(row)">
            录入人脸
          </el-button>
        </template>
      </DataTable>
    </el-card>

    <el-dialog v-model="importVisible" title="导入学生">
      <el-form label-position="top">
        <el-form-item label="导入文件">
          <el-input v-model="importForm.fileName" readonly placeholder="文件选择功能暂未接入" />
        </el-form-item>
        <el-form-item label="处理方式">
          <el-radio-group v-model="importForm.mode">
            <el-radio value="merge">保留现有并增量导入</el-radio>
            <el-radio value="overwrite">覆盖同学号记录</el-radio>
          </el-radio-group>
        </el-form-item>
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

    <el-dialog v-model="faceDialogVisible" title="录入学生人脸" width="460px">
      <div v-if="faceStudent" class="face-dialog">
        <div>
          <strong>{{ faceStudent.name }}</strong>
          <span>{{ faceStudent.studentNo }} · {{ faceStudent.className }}</span>
        </div>
        <el-upload
          drag
          accept="image/*"
          :auto-upload="false"
          :limit="1"
          :before-upload="beforeFaceUpload"
        >
          <el-icon class="face-dialog__icon"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽或点击选择正面照片</div>
        </el-upload>
      </div>
      <template #footer>
        <el-button @click="faceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="faceUploading" @click="submitFaceUpload">
          开始录入
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped lang="scss">
.table-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.face-dialog {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.face-dialog span {
  display: block;
  margin-top: 4px;
  color: var(--el-text-color-secondary);
}

.face-dialog__icon {
  color: var(--el-color-primary);
  font-size: 32px;
}
</style>
