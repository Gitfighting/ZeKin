/** 登录页图标 SVG（不依赖 iconfont 字体，小程序直接用 image 渲染） */
export type AuthIconName =
  | 'yonghu'
  | 'mima'
  | 'anquan'
  | 'yanzhengma'
  | 'yanjing'
  | 'yanjing-biyan'

const ICON_SVGS: Record<AuthIconName, string> = {
  yonghu: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="{{COLOR}}" stroke-width="1.8"/><path d="M5 20c0-3.5 3.1-5.5 7-5.5s7 2 7 5.5" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  mima: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="{{COLOR}}" stroke-width="1.8"/><path d="M8 11V8a4 4 0 0 1 8 0v3" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="16" r="1.2" fill="{{COLOR}}"/></svg>`,
  anquan: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M12 3l7 3v6c0 4.5-3 8.2-7 9-4-0.8-7-4.5-7-9V6l7-3z" stroke="{{COLOR}}" stroke-width="1.8" stroke-linejoin="round"/><path d="M9 12l2 2 4-4" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  yanzhengma: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><rect x="4" y="6" width="16" height="12" rx="2" stroke="{{COLOR}}" stroke-width="1.8"/><path d="M8 10h3M13 10h3M8 14h8" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  yanjing: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" stroke="{{COLOR}}" stroke-width="1.8"/><circle cx="12" cy="12" r="2.5" stroke="{{COLOR}}" stroke-width="1.8"/></svg>`,
  'yanjing-biyan': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M3 3l18 18" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round"/><path d="M10.6 10.6A2.5 2.5 0 0 0 12 15a2.5 2.5 0 0 0 1.4-4.4M6.7 6.8C4.6 8.2 3 10.1 2 12c0 0 3.5 6 10 6 1.8 0 3.4-.4 4.8-1.1M17.3 17.2C19.4 15.8 21 13.9 22 12c0 0-3.5-6-10-6-1.3 0-2.5.2-3.6.6" stroke="{{COLOR}}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
}

export function buildAuthIconSrc(name: AuthIconName, color: string): string {
  const svg = ICON_SVGS[name].replace(/\{\{COLOR\}\}/g, color)
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}
