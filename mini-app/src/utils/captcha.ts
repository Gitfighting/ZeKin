import type { ComponentInternalInstance } from 'vue'

const CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

const COLORS = ['#0877f2', '#2563eb', '#dc2626', '#059669', '#7c3aed', '#ea580c']

export interface CaptchaCharView {
  char: string
  color: string
  rotate: number
  fontSize: number
  offsetY: number
}

export function createCaptchaCode(length = 4): string {
  let code = ''
  for (let i = 0; i < length; i += 1) {
    code += CHARS[Math.floor(Math.random() * CHARS.length)]
  }
  return code
}

/** 小程序端用 view/text 渲染，避免 canvas 原生组件裁切 */
export function buildCaptchaDisplay(code: string): CaptchaCharView[] {
  return code.split('').map((char, index) => ({
    char,
    color: COLORS[index % COLORS.length],
    rotate: Math.round((Math.random() - 0.5) * 26),
    fontSize: 24 + Math.floor(Math.random() * 4),
    offsetY: Math.round((Math.random() - 0.5) * 6),
  }))
}

export type CanvasScope = ComponentInternalInstance | ComponentInternalInstance['proxy'] | undefined

function resolveScope(componentInstance?: CanvasScope): unknown {
  if (!componentInstance) {
    return undefined
  }
  if (typeof componentInstance === 'object' && componentInstance !== null && 'proxy' in componentInstance) {
    return componentInstance.proxy ?? componentInstance
  }
  return componentInstance
}

export function drawCaptchaImage(
  canvasId: string,
  code: string,
  width: number,
  height: number,
  componentInstance?: CanvasScope,
): Promise<void> {
  const scope = resolveScope(componentInstance)

  return new Promise((resolve, reject) => {
    const ctx = uni.createCanvasContext(canvasId, scope)
    if (!ctx) {
      reject(new Error('createCanvasContext failed'))
      return
    }

    ctx.setFillStyle('#eef6ff')
    ctx.fillRect(0, 0, width, height)

    for (let i = 0; i < 5; i += 1) {
      ctx.setStrokeStyle(`rgba(8, 119, 242, ${0.15 + Math.random() * 0.25})`)
      ctx.setLineWidth(1)
      ctx.beginPath()
      ctx.moveTo(Math.random() * width, Math.random() * height)
      ctx.lineTo(Math.random() * width, Math.random() * height)
      ctx.stroke()
    }

    for (let i = 0; i < 16; i += 1) {
      ctx.setFillStyle(`rgba(100, 116, 139, ${0.2 + Math.random() * 0.35})`)
      ctx.beginPath()
      ctx.arc(Math.random() * width, Math.random() * height, 0.9, 0, Math.PI * 2)
      ctx.fill()
    }

    const padX = 6
    const innerWidth = width - padX * 2
    const cellWidth = innerWidth / code.length
    const baseFont = Math.max(10, Math.min(13, Math.floor(cellWidth * 0.52)))
    for (let i = 0; i < code.length; i += 1) {
      const char = code[i]
      const fontSize = baseFont + Math.floor(Math.random() * 2)
      const angle = (Math.random() - 0.5) * 0.28
      const x = padX + cellWidth * i + cellWidth / 2
      const y = height / 2

      ctx.save()
      ctx.translate(x, y)
      ctx.rotate(angle)
      ctx.setFillStyle(COLORS[i % COLORS.length])
      ctx.setFontSize(fontSize)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText(char, 0, 0)
      ctx.restore()
    }

    ctx.draw(false, () => {
      setTimeout(() => resolve(), 80)
    })
  })
}

export function canvasToImage(
  canvasId: string,
  width: number,
  height: number,
  componentInstance?: CanvasScope,
): Promise<string> {
  const scope = resolveScope(componentInstance)

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      uni.canvasToTempFilePath(
        {
          canvasId,
          x: 0,
          y: 0,
          width,
          height,
          destWidth: width * 2,
          destHeight: height * 2,
          fileType: 'png',
          success: (res) => resolve(res.tempFilePath),
          fail: reject,
        },
        scope,
      )
    }, 120)
  })
}
