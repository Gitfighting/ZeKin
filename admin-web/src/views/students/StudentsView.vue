<script setup lang="ts">
import { Camera, Search, UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  batchRegisterStudentFaces,
  clearStudentFace,
  getStudentFaceStatus,
  getStudents,
  registerStudentFace,
  type StudentFaceBatchItem,
  type StudentFaceStatus,
  type StudentRow,
} from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError, showSuccess, showWarning } from '../../utils/feedback'

const search = reactive({
  name: '',
  studentNo: '',
  className: '',
})

const importVisible = ref(false)
const faceDialogVisible = ref(false)
const faceStudent = ref<StudentRow | null>(null)
const faceStatus = ref<StudentFaceStatus | null>(null)
const faceStatusLoading = ref(false)
const faceFile = ref<File | null>(null)
const facePreviewUrl = ref('')
const faceUploading = ref(false)
const faceClearing = ref(false)
const faceBatchVisible = ref(false)
const faceBatchFiles = ref<File[]>([])
const faceBatchUploading = ref(false)
const faceBatchResult = ref<StudentFaceBatchItem[]>([])
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
  { key: 'faceRegistered', label: '人脸状态', minWidth: 130 },
  { key: 'actions', label: '操作', minWidth: 180 },
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

const confirmImport = () => {
  showWarning('批量导入文件解析接口暂未接入')
}

async function loadFaceStatus(studentId: number) {
  faceStatusLoading.value = true
  try {
    faceStatus.value = await getStudentFaceStatus(studentId)
    logInfo('学生人脸状态加载成功', { studentId, status: faceStatus.value })
  } catch (error) {
    faceStatus.value = null
    showError(error, '人脸状态加载失败')
  } finally {
    faceStatusLoading.value = false
  }
}

const openFaceDialog = async (row: StudentRow) => {
  faceStudent.value = row
  faceFile.value = null
  clearFacePreview()
  faceDialogVisible.value = true
  logInfo('打开人脸管理对话框', {
    studentId: row.id,
    studentNo: row.studentNo,
    faceRegistered: row.faceRegistered,
  })
  await loadFaceStatus(row.id)
}

const handleFaceFileChange = (uploadFile: UploadFile) => {
  const rawFile = uploadFile.raw
  if (!rawFile) {
    return
  }
  faceFile.value = rawFile
  facePreviewUrl.value = URL.createObjectURL(rawFile)
  logInfo('已选择人脸照片', {
    name: rawFile.name,
    size: rawFile.size,
    type: rawFile.type,
  })
}

function clearFacePreview() {
  if (facePreviewUrl.value) {
    URL.revokeObjectURL(facePreviewUrl.value)
  }
  facePreviewUrl.value = ''
  faceFile.value = null
}

async function submitFaceUpload() {
  if (!faceStudent.value || !faceFile.value) {
    showWarning('请先选择一张正面人脸照片')
    return
  }

  faceUploading.value = true
  logInfo('开始上传学生人脸', {
    studentId: faceStudent.value.id,
    studentNo: faceStudent.value.studentNo,
    fileName: faceFile.value.name,
    fileSize: faceFile.value.size,
  })
  try {
    const result = await registerStudentFace(faceStudent.value.id, faceFile.value)
    logInfo('学生人脸录入成功', {
      studentId: faceStudent.value.id,
      studentNo: faceStudent.value.studentNo,
      result,
    })
    showSuccess('人脸特征已写入数据库')
    clearFacePreview()
    await Promise.all([loadFaceStatus(faceStudent.value.id), loadStudents()])
  } catch (error) {
    showError(error, '人脸录入失败')
  } finally {
    faceUploading.value = false
  }
}

function openFaceBatchDialog() {
  faceBatchFiles.value = []
  faceBatchResult.value = []
  faceBatchVisible.value = true
}

function handleFaceBatchFileChange(uploadFile: UploadFile, uploadFiles: UploadFile[]) {
  faceBatchFiles.value = uploadFiles
    .map((item) => item.raw)
    .filter((file): file is File => Boolean(file))
  faceBatchResult.value = []
}

async function submitFaceBatchUpload() {
  if (!faceBatchFiles.value.length) {
    showWarning('请先选择至少一张以学号命名的人脸照片')
    return
  }

  faceBatchUploading.value = true
  try {
    const result = await batchRegisterStudentFaces(faceBatchFiles.value)
    faceBatchResult.value = result.items
    logInfo('批量人脸录入完成', result)
    if (result.successCount > 0) {
      showSuccess(`成功录入 ${result.successCount} 名学生，失败 ${result.failedCount} 条`)
      await loadStudents()
    } else {
      showWarning(`全部失败，共 ${result.failedCount} 条，请查看明细`)
    }
  } catch (error) {
    showError(error, '批量人脸录入失败')
  } finally {
    faceBatchUploading.value = false
  }
}

async function handleClearFace() {
  if (!faceStudent.value || !faceStatus.value?.registered) {
    showWarning('当前学生尚未录入人脸')
    return
  }

  try {
    await ElMessageBox.confirm(
      '清除后该学生将无法通过人脸打卡，需重新录入。确定继续吗？',
      '清除人脸信息',
      { type: 'warning', confirmButtonText: '清除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }

  faceClearing.value = true
  try {
    const result = await clearStudentFace(faceStudent.value.id)
    logInfo('学生人脸已清除', {
      studentId: faceStudent.value.id,
      result,
    })
    showSuccess('人脸信息已清除')
    clearFacePreview()
    await Promise.all([loadFaceStatus(faceStudent.value.id), loadStudents()])
  } catch (error) {
    showError(error, '清除人脸失败')
  } finally {
    faceClearing.value = false
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
        <p>支持名单导入、人脸录入与管理。</p>
      </div>
      <el-space>
        <el-button @click="importVisible = true">批量导入学生</el-button>
        <el-button @click="openFaceBatchDialog">批量录入人脸</el-button>
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
        <template #faceRegistered="{ row }">
          <el-tag :type="row.faceRegistered ? 'success' : 'info'">
            {{ row.faceRegistered ? '已录入' : '未录入' }}
          </el-tag>
        </template>
        <template #actions="{ row }">
          <el-button :icon="Camera" text type="primary" @click="openFaceDialog(row)">
            人脸管理
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

    <el-dialog v-model="faceDialogVisible" title="学生人脸管理" width="520px">
      <div v-if="faceStudent" v-loading="faceStatusLoading" class="face-dialog">
        <div>
          <strong>{{ faceStudent.name }}</strong>
          <span>{{ faceStudent.studentNo }} · {{ faceStudent.className }}</span>
        </div>

        <el-upload
          v-if="!facePreviewUrl"
          drag
          accept="image/*"
          :auto-upload="false"
          :limit="1"
          :show-file-list="false"
          :on-change="handleFaceFileChange"
        >
          <el-icon class="face-dialog__icon"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            {{ faceStatus?.registered ? '拖拽或点击选择新照片（重新录入）' : '拖拽或点击选择正面照片' }}
          </div>
          <div class="el-upload__tip">请使用单人正面清晰照片，避免遮挡和强光</div>
        </el-upload>
        <div v-else class="face-dialog__preview-wrap">
          <img class="face-dialog__preview" :src="facePreviewUrl" alt="人脸预览" />
          <el-button text type="primary" @click="clearFacePreview">重新选择</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="faceDialogVisible = false">关闭</el-button>
        <el-button
          v-if="faceStatus?.registered"
          type="danger"
          plain
          :loading="faceClearing"
          @click="handleClearFace"
        >
          清除人脸
        </el-button>
        <el-button
          type="primary"
          :loading="faceUploading"
          :disabled="!faceFile"
          @click="submitFaceUpload"
        >
          {{ faceStatus?.registered ? '重新录入并写入数据库' : '开始录入并写入数据库' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="faceBatchVisible" title="批量录入人脸" width="720px">
      <div class="face-batch">
        <el-alert
          type="info"
          :closable="false"
          title="文件命名规则：照片文件名必须是学号，例如 20260001.jpg。系统会提取人脸特征并写入 face_encodings 表。"
        />
        <el-upload
          drag
          multiple
          accept="image/*"
          :auto-upload="false"
          :show-file-list="true"
          :on-change="handleFaceBatchFileChange"
        >
          <el-icon class="face-dialog__icon"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽或点击选择多张照片</div>
          <div class="el-upload__tip">支持 jpg/png/webp，建议单人正面清晰照片</div>
        </el-upload>

        <el-table v-if="faceBatchResult.length" :data="faceBatchResult" size="small" max-height="280">
          <el-table-column prop="filename" label="文件名" min-width="140" />
          <el-table-column prop="studentNo" label="学号" min-width="110" />
          <el-table-column prop="studentName" label="姓名" min-width="90" />
          <el-table-column label="结果" min-width="90">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'" size="small">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="说明" min-width="180" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="faceBatchVisible = false">关闭</el-button>
        <el-button type="primary" :loading="faceBatchUploading" @click="submitFaceBatchUpload">
          开始批量录入
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped lang="scss">
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

.face-dialog__preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.face-dialog__preview {
  width: 100%;
  max-height: 240px;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
}

.face-batch {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
