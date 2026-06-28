export interface TeacherQuickEntry {
  key: 'create' | 'tasks' | 'groups' | 'review'
  label: string
  sub: string
  path: string
  iconSrc: string
}

export const TEACHER_QUICK_ENTRIES: TeacherQuickEntry[] = [
  {
    key: 'create',
    label: '发起签到',
    sub: '课堂/活动签到',
    path: '/pages/teacher/task-create',
    iconSrc: '/static/home-icons/task-calendar.svg',
  },
  {
    key: 'tasks',
    label: '考勤管理',
    sub: '查看考勤记录',
    path: '/pages/teacher/tasks',
    iconSrc: '/static/home-icons/task-records.svg',
  },
  {
    key: 'groups',
    label: '班级管理',
    sub: '学生与班级',
    path: '/pages/teacher/groups',
    iconSrc: '/static/home-icons/my-classes.svg',
  },
  {
    key: 'review',
    label: '审核管理',
    sub: '缺勤/异常审核',
    path: '/pages/teacher/exceptions',
    iconSrc: '/static/home-icons/join-class.svg',
  },
]

export function openTeacherQuickEntry(path: string) {
  if (typeof uni === 'undefined') {
    return
  }
  const pages = getCurrentPages()
  const currentRoute = pages.length ? `/${pages[pages.length - 1].route}` : ''
  if (currentRoute === path) {
    return
  }
  if (path === '/pages/teacher/tasks' || path === '/pages/teacher/groups' || path === '/pages/teacher/home') {
    uni.reLaunch({ url: path })
    return
  }
  uni.navigateTo({ url: path })
}
