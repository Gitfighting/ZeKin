/**
 * 开发前同步微信小程序 AppID / 基础库版本，避免 touristappid 触发
 * webapi_getwxaasyncsecinfo:fail（41002 appid missing）。
 *
 * 优先级：project.private.config.json > .env.local > .env.development (VITE_WX_APPID)
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const DEFAULT_LIB = '3.8.12'
const TOURIST = 'touristappid'

function readEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {}
  const out = {}
  for (const line of fs.readFileSync(filePath, 'utf8').split(/\r?\n/)) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eq = trimmed.indexOf('=')
    if (eq <= 0) continue
    out[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim()
  }
  return out
}

function resolveWxAppId() {
  const privatePath = path.join(root, 'project.private.config.json')
  if (fs.existsSync(privatePath)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(privatePath, 'utf8'))
      if (cfg.appid && cfg.appid !== TOURIST) return cfg.appid
    } catch {
      console.warn('[weixin-dev] project.private.config.json 解析失败，已跳过')
    }
  }

  for (const name of ['.env.local', '.env.development', '.env']) {
    const env = readEnvFile(path.join(root, name))
    const id = env.VITE_WX_APPID?.replace(/^['"]|['"]$/g, '')
    if (id && id !== TOURIST) return id
  }

  return null
}

function patchJson(filePath, mutator) {
  const raw = fs.readFileSync(filePath, 'utf8')
  const data = JSON.parse(raw)
  mutator(data)
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8')
}

function syncManifest(appid) {
  const manifestPath = path.join(root, 'src/manifest.json')
  let text = fs.readFileSync(manifestPath, 'utf8')
  const re = /("mp-weixin"\s*:\s*\{[\s\S]*?"appid"\s*:\s*")[^"]*(")/m
  if (!re.test(text)) {
    console.warn('[weixin-dev] manifest.json 中未找到 mp-weixin.appid')
    return
  }
  text = text.replace(re, `$1${appid}$2`)
  fs.writeFileSync(manifestPath, text, 'utf8')
}

function ensureProjectConfig(appid, libVersion) {
  const cfgPath = path.join(root, 'project.config.json')
  patchJson(cfgPath, (cfg) => {
    cfg.appid = appid
    cfg.libVersion = libVersion
    cfg.setting = { ...cfg.setting, urlCheck: false }
  })
}

function ensurePrivateExample() {
  const example = path.join(root, 'project.private.config.json.example')
  if (fs.existsSync(example)) return
  fs.writeFileSync(
    example,
    `${JSON.stringify(
      {
        appid: 'wx你的测试号AppID',
        libVersion: DEFAULT_LIB,
        setting: { urlCheck: false, es6: true },
      },
      null,
      2,
    )}\n`,
    'utf8',
  )
}

function main() {
  ensurePrivateExample()

  const privatePath = path.join(root, 'project.private.config.json')
  let libVersion = DEFAULT_LIB
  if (fs.existsSync(privatePath)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(privatePath, 'utf8'))
      if (cfg.libVersion) libVersion = cfg.libVersion
    } catch {
      /* ignore */
    }
  }

  const appid = resolveWxAppId() || TOURIST
  syncManifest(appid)
  ensureProjectConfig(appid, libVersion)

  if (appid === TOURIST) {
    console.warn('')
    console.warn('[weixin-dev] ⚠  当前仍为 touristappid，开发者工具可能反复报：')
    console.warn('         webapi_getwxaasyncsecinfo:fail / err_code 41002 appid missing')
    console.warn('')
    console.warn('  推荐：复制 project.private.config.json.example → project.private.config.json')
    console.warn('        填入微信公众平台「测试号 / 小程序」的真实 AppID，然后重新 npm run dev:mp-weixin')
    console.warn('  或在 .env.development 中设置 VITE_WX_APPID=wx...')
    console.warn('')
    return
  }

  console.info(`[weixin-dev] 已同步 AppID → ${appid}，基础库 → ${libVersion}`)
}

main()
