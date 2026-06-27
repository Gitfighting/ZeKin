/**
 * 生成微信小程序 tabBar PNG 图标（81×81）
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const outDir = path.join(root, 'src/static/tabbar')

const GREY = '#667085'
const BLUE = '#1677FF'

const ICONS = {
  home: (color) => `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="81" height="81">
      <path fill="${color}" d="M24 8L8 20v20a2 2 0 0 0 2 2h10V30h8v12h10a2 2 0 0 0 2-2V20L24 8z"/>
    </svg>`,
  tasks: (color) => `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="81" height="81">
      <rect x="10" y="12" width="28" height="26" rx="3" fill="none" stroke="${color}" stroke-width="2.4"/>
      <path stroke="${color}" stroke-width="2.4" stroke-linecap="round" d="M16 8h16v6H16z"/>
      <path stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" fill="none" d="M18 26l4 4 8-8"/>
    </svg>`,
  messages: (color) => `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="81" height="81">
      <path fill="${color}" d="M10 12a3 3 0 0 1 3-3h22a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H22l-8 7v-7h-1a3 3 0 0 1-3-3V12z"/>
      <circle cx="18" cy="20" r="2" fill="#fff"/>
      <circle cx="24" cy="20" r="2" fill="#fff"/>
      <circle cx="30" cy="20" r="2" fill="#fff"/>
    </svg>`,
  profile: (color) => `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="81" height="81">
      <circle cx="24" cy="18" r="7" fill="${color}"/>
      <path fill="${color}" d="M10 38c0-7.7 6.3-14 14-14s14 6.3 14 14v2H10v-2z"/>
    </svg>`,
}

fs.mkdirSync(outDir, { recursive: true })

async function writeIcon(name, svg) {
  const outPath = path.join(outDir, `${name}.png`)
  await sharp(Buffer.from(svg)).resize(81, 81).png().toFile(outPath)
  console.log('Wrote', outPath)
}

for (const key of Object.keys(ICONS)) {
  await writeIcon(key, ICONS[key](GREY))
  await writeIcon(`${key}-active`, ICONS[key](BLUE))
}
