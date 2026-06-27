import { onShow } from '@dcloudio/uni-app'

const TAB_INDEX: Record<string, number> = {
  'pages/student/home': 0,
  'pages/student/tasks': 1,
  'pages/student/messages': 2,
  'pages/student/profile': 3,
}

type TabBarPage = keyof typeof TAB_INDEX

type TabBarInstance = {
  setData?: (data: { selected: number }) => void
}

type TabBarPageInstance = UniApp.PageInstance & {
  getTabBar?: () => TabBarInstance
  $scope?: {
    getTabBar?: () => TabBarInstance
  }
}

function resolveTabBar(page: TabBarPageInstance): TabBarInstance | undefined {
  if (typeof page.getTabBar === 'function') {
    return page.getTabBar()
  }

  if (typeof page.$scope?.getTabBar === 'function') {
    return page.$scope.getTabBar()
  }

  return undefined
}

export function useStudentTabBar(pagePath: TabBarPage) {
  onShow(() => {
    const pages = getCurrentPages()
    const page = pages[pages.length - 1] as TabBarPageInstance
    resolveTabBar(page)?.setData?.({ selected: TAB_INDEX[pagePath] })
  })
}
