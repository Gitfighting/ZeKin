import { ElMessage } from 'element-plus'

function readMessage(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) {
    return value
  }

  if (Array.isArray(value)) {
    return value.map(readMessage).find((message): message is string => Boolean(message)) ?? null
  }

  if (typeof value === 'object' && value !== null) {
    const record = value as Record<string, unknown>
    return (
      readMessage(record.detail) ??
      readMessage(record.message) ??
      readMessage(record.error) ??
      readMessage(record.msg) ??
      readMessage(record.data) ??
      readMessage(record.response)
    )
  }

  return null
}

export function errorMessage(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null && 'code' in error) {
    const code = (error as { code?: string }).code
    if (code === 'ECONNABORTED') {
      return '请求超时：人脸特征提取耗时较长，请稍后重试或上传更小、更清晰的照片'
    }
  }

  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: unknown } }).response
    const fromResponse = readMessage(response?.data)
    if (fromResponse) {
      return fromResponse
    }
  }

  return readMessage(error) ?? fallback
}

export function logInfo(message: string, detail?: unknown) {
  if (detail === undefined) {
    console.info(`[AI思政管理端] ${message}`)
    return
  }

  console.info(`[AI思政管理端] ${message}`, detail)
}

export function logError(message: string, error: unknown) {
  console.error(`[AI思政管理端] ${message}`, error)
}

export function showSuccess(message: string) {
  logInfo(message)
  ElMessage.success(message)
}

export function showWarning(message: string) {
  logInfo(message)
  ElMessage.warning(message)
}

export function showError(error: unknown, fallback: string): string {
  const message = errorMessage(error, fallback)
  logError(fallback, error)
  ElMessage.error(message)
  return message
}
