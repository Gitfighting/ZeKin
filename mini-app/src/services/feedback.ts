type ErrorLike = {
  message?: unknown
  data?: unknown
  response?: unknown
}

function readMessage(value: unknown): string {
  if (typeof value === 'string' && value.trim()) {
    return value.trim()
  }

  if (Array.isArray(value)) {
    return value.map(readMessage).filter(Boolean).join('；')
  }

  if (typeof value === 'object' && value !== null) {
    const payload = value as Record<string, unknown>
    return (
      readMessage(payload.detail) ||
      readMessage(payload.message) ||
      readMessage(payload.error) ||
      readMessage(payload.msg)
    )
  }

  return ''
}

export function errorMessage(error: unknown, fallback: string): string {
  const direct = readMessage(error)
  if (direct) {
    return direct
  }

  const errorLike = error as ErrorLike
  return (
    readMessage(errorLike?.data) ||
    readMessage(errorLike?.response) ||
    readMessage(errorLike?.message) ||
    fallback
  )
}

export function logInfo(message: string, detail?: unknown) {
  if (detail === undefined) {
    console.info(`[AI思政] ${message}`)
    return
  }

  console.info(`[AI思政] ${message}`, detail)
}

export function logError(message: string, error: unknown) {
  console.error(`[AI思政] ${message}`, error)
}

export function showSuccess(message: string) {
  if (typeof uni === 'undefined') {
    return
  }

  uni.showToast({ title: message, icon: 'success' })
}

export function showCheckinErrorModal(message: string) {
  logError('签到失败', message)

  if (typeof uni === 'undefined') {
    return
  }

  if (typeof uni.showModal === 'function') {
    uni.showModal({
      title: '签到失败',
      content: message,
      showCancel: false,
      confirmText: '我知道了',
    })
    return
  }

  uni.showToast({ title: message, icon: 'none' })
}

export function showError(error: unknown, fallback: string): string {
  const message = errorMessage(error, fallback)
  if (typeof error === 'object' && error !== null && (error as { silent?: unknown }).silent === true) {
    return message
  }

  logError(fallback, error)

  if (typeof uni === 'undefined') {
    return message
  }

  if (message.length > 18 && typeof uni.showModal === 'function') {
    uni.showModal({
      title: '操作失败',
      content: message,
      showCancel: false,
    })
    return message
  }

  uni.showToast({ title: message, icon: 'none' })
  return message
}
