/**
 * 从 bsfit 登录 iconfont 生成小程序用 base64（仅保留登录页 6 个图标）
 * 字体来源: https://at.alicdn.com/t/font_1124695_24zbf5gv2ug.ttf
 */
import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const ttfPath = path.join(root, 'src/static/fonts/iconfont.ttf')
const subsetPath = path.join(root, 'src/static/fonts/iconfont-subset.ttf')
const outPath = path.join(root, 'src/utils/iconfont-base64.ts')

const GLYPHS = 'e68e,e687,e713,e68d,e68b,e68a'

if (!fs.existsSync(ttfPath)) {
  console.error(`Missing: ${ttfPath}`)
  process.exit(1)
}

execSync(
  `python -c "from fontTools import subset; subset.main(['${ttfPath.replace(/\\/g, '/')}', '--output-file=${subsetPath.replace(/\\/g, '/')}', '--unicodes=${GLYPHS}', '--layout-features=*', '--glyph-names', '--symbol-cmap', '--legacy-cmap', '--notdef-glyph', '--notdef-outline', '--recommended-glyphs'])"`,
  { stdio: 'inherit' },
)

const base64 = fs.readFileSync(subsetPath).toString('base64')
const ts = `/** 自动生成：scripts/gen-iconfont-base64.mjs — 勿手改 */
export const ICONFONT_BASE64 = '${base64}'
export const ICONFONT_SUBSET_BYTES = ${fs.statSync(subsetPath).size}
`

fs.writeFileSync(outPath, ts)
console.log(`Wrote ${outPath} (subset ${fs.statSync(subsetPath).size} bytes, base64 ${base64.length} chars)`)
