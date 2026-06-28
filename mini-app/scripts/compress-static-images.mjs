import { readdir, stat, unlink } from 'node:fs/promises'
import path from 'node:path'
import sharp from 'sharp'

const staticDir = path.resolve('src/static')
const targets = ['home.png', 'man-blue-daily.png']
const maxWidth = 750

async function compressImage(filename) {
  const inputPath = path.join(staticDir, filename)
  const tempPath = `${inputPath}.tmp`
  const before = (await stat(inputPath)).size

  await sharp(inputPath)
    .resize({ width: maxWidth, withoutEnlargement: true })
    .png({ quality: 82, compressionLevel: 9, palette: true })
    .toFile(tempPath)

  await unlink(inputPath)
  await sharp(tempPath).toFile(inputPath)
  await unlink(tempPath)

  const after = (await stat(inputPath)).size
  console.log(`${filename}: ${(before / 1024).toFixed(1)} KB -> ${(after / 1024).toFixed(1)} KB`)
}

for (const filename of targets) {
  await compressImage(filename)
}

console.log('Static images compressed.')
