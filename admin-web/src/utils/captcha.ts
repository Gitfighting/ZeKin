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

export function buildCaptchaDisplay(code: string): CaptchaCharView[] {
  return code.split('').map((char, index) => ({
    char,
    color: COLORS[index % COLORS.length],
    rotate: Math.round((Math.random() - 0.5) * 26),
    fontSize: 22 + Math.floor(Math.random() * 4),
    offsetY: Math.round((Math.random() - 0.5) * 4),
  }))
}
