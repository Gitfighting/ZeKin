import { ref } from 'vue'

import { getStudentMessages } from '@/services/student'

export const studentUnreadMessageCount = ref(0)

export async function refreshStudentUnreadMessageCount() {
  try {
    const { messages, unreadCount } = await getStudentMessages()
    studentUnreadMessageCount.value = unreadCount ?? messages.filter((item) => !item.read).length
  } catch {
    studentUnreadMessageCount.value = 0
  }
  return studentUnreadMessageCount.value
}

export function formatUnreadBadge(count: number): string {
  if (count <= 0) {
    return ''
  }
  return count > 99 ? '99+' : String(count)
}
