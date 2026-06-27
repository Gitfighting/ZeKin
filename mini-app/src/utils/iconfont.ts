/**
 * 微信小程序 iconfont 加载（官方/DCloud 推荐：base64 + uni.loadFontFace）
 * - 勿在 wxss 使用本地 ttf url（会 500 / do-not-use-local-path）
 * - 勿 readFile('/static/...')（permission denied）
 * 生成 base64：npm run gen:iconfont
 */
import { ICONFONT_BASE64, ICONFONT_SUBSET_BYTES } from './iconfont-base64'

export const ICON_FONT_FAMILY = 'iconfont'

let iconFontReady: Promise<boolean> | null = null

function logIconFont(step: string, detail?: unknown) {
  if (detail === undefined) {
    console.info('[iconfont]', step)
    return
  }
  console.info('[iconfont]', step, detail)
}

function loadFontFaceFromSource(source: string): Promise<void> {
  return new Promise((resolve, reject) => {
    uni.loadFontFace({
      global: true,
      family: ICON_FONT_FAMILY,
      source,
      scopes: ['webview', 'native'],
      success: () => resolve(),
      fail: (err) => reject(err),
    })
  })
}

async function loadLocalIconFontMp(): Promise<boolean> {
  logIconFont('boot', {
    strategy: 'base64-loadFontFace',
    subsetBytes: ICONFONT_SUBSET_BYTES,
  })

  const source = `url("data:font/truetype;charset=utf-8;base64,${ICONFONT_BASE64}")`
  logIconFont('loadFontFace.request', { via: 'base64' })

  try {
    await loadFontFaceFromSource(source)
    logIconFont('loadFontFace.ok', { via: 'base64' })
    logIconFont('ready', { strategy: 'base64-loadFontFace', ok: true })
    return true
  } catch (error) {
    logIconFont('loadFontFace.fail', { via: 'base64', error })
    logIconFont('ready.fail', '图标字体加载失败，将显示为方框')
    return false
  }
}

export function loadIconFont(): Promise<boolean> {
  if (iconFontReady) {
    return iconFontReady
  }

  iconFontReady = (async () => {
    // #ifdef MP-WEIXIN
    try {
      return await loadLocalIconFontMp()
    } catch (error) {
      logIconFont('fatal', error)
      return false
    }
    // #endif

    // #ifndef MP-WEIXIN
    logIconFont('ready', { strategy: 'h5-css-file', ok: true })
    return true
    // #endif
  })()

  return iconFontReady
}
