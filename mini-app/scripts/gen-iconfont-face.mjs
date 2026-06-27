import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const ttfPath = path.join(root, 'src/static/fonts/iconfont.ttf')
const outPath = path.join(root, 'src/styles/iconfont-face.scss')

// 字体来源（bsfit 登录图标集 font_1124695）:
// https://at.alicdn.com/t/font_1124695_24zbf5gv2ug.ttf?t=1622778650692

if (!fs.existsSync(ttfPath)) {
  console.error(`Missing font file: ${ttfPath}`)
  process.exit(1)
}

const css = `// 阿里巴巴 iconfont 本地字体（font_1124695 / static/fonts/iconfont.ttf）
@font-face {
  font-family: 'iconfont';
  src: url('/static/fonts/iconfont.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
`

fs.writeFileSync(outPath, css)
console.log(`Wrote ${outPath}`)
