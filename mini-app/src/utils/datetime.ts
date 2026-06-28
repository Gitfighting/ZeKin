const BEIJING_OFFSET_MS = 8 * 60 * 60 * 1000

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function formatBeijingFromTimestamp(timestamp: number): string {
  const beijing = new Date(timestamp + BEIJING_OFFSET_MS)
  return `${beijing.getUTCFullYear()}-${pad(beijing.getUTCMonth() + 1)}-${pad(beijing.getUTCDate())} ${pad(beijing.getUTCHours())}:${pad(beijing.getUTCMinutes())}`
}

export function formatBeijingDateTime(value?: string | null): string {
  if (!value) {
    return ''
  }

  const trimmed = value.trim()
  const beijingMatch = trimmed.match(
    /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::\d{2})?(?:\.\d+)?(?:\+08:00|\+0800)$/,
  )
  if (beijingMatch) {
    return `${beijingMatch[1]}-${beijingMatch[2]}-${beijingMatch[3]} ${beijingMatch[4]}:${beijingMatch[5]}`
  }

  const timestamp = Date.parse(trimmed)
  if (!Number.isNaN(timestamp)) {
    return formatBeijingFromTimestamp(timestamp)
  }

  const match = trimmed.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/)
  if (match) {
    return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}`
  }

  return trimmed
}

export function formatBeijingClock(value?: string | null): string {
  const formatted = formatBeijingDateTime(value)
  const match = formatted.match(/(\d{2}:\d{2})$/)
  return match?.[1] ?? ''
}

export function formatBeijingDateTimeNow(timestamp = Date.now()): string {
  return formatBeijingFromTimestamp(timestamp)
}

export function formatBeijingDateNow(timestamp = Date.now()): string {
  const beijing = new Date(timestamp + BEIJING_OFFSET_MS)
  return `${beijing.getUTCFullYear()}-${pad(beijing.getUTCMonth() + 1)}-${pad(beijing.getUTCDate())}`
}

export function formatBeijingClockNow(timestamp = Date.now()): string {
  const beijing = new Date(timestamp + BEIJING_OFFSET_MS)
  return `${pad(beijing.getUTCHours())}:${pad(beijing.getUTCMinutes())}`
}

export function formatBeijingDateTimeAfterHours(hours: number, timestamp = Date.now()): string {
  return formatBeijingFromTimestamp(timestamp + hours * 60 * 60 * 1000)
}

export function formatBeijingDateTimeAfterMinutes(minutes: number, timestamp = Date.now()): string {
  return formatBeijingFromTimestamp(timestamp + minutes * 60 * 1000)
}

export function parseBeijingDateTime(value?: string | null): number | null {
  const normalized = formatBeijingDateTime(value)
  const match = normalized.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$/)
  if (!match) {
    return null
  }

  const [, year, month, day, hour, minute] = match
  const timestamp = Date.parse(`${year}-${month}-${day}T${hour}:${minute}:00+08:00`)
  return Number.isNaN(timestamp) ? null : timestamp
}

export function isBeijingDateTimeBeforeNow(value: string, now = Date.now()): boolean {
  const timestamp = parseBeijingDateTime(value)
  return timestamp === null || timestamp < now
}

export function isBeijingEndBeforeStart(start: string, end: string): boolean {
  const startMs = parseBeijingDateTime(start)
  const endMs = parseBeijingDateTime(end)
  if (startMs === null || endMs === null) {
    return true
  }
  return endMs <= startMs
}

/** YYYY-MM-DD 字符串取较晚者 */
export function maxBeijingDate(a: string, b: string): string {
  return a >= b ? a : b
}

export interface BeijingDateParts {
  year: number
  month: number
  day: number
}

export function parseBeijingDate(value?: string | null): BeijingDateParts | null {
  if (!value) {
    return null
  }
  const match = value.trim().match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!match) {
    return null
  }
  return {
    year: Number.parseInt(match[1], 10),
    month: Number.parseInt(match[2], 10),
    day: Number.parseInt(match[3], 10),
  }
}

export function clampBeijingDate(value: string, min: string, max: string): string {
  if (value < min) {
    return min
  }
  if (value > max) {
    return max
  }
  return value
}

/** 北京时间下 N 年后的日期 YYYY-MM-DD */
export function formatBeijingDateAfterYears(years: number, timestamp = Date.now()): string {
  const beijing = new Date(timestamp + BEIJING_OFFSET_MS)
  const year = beijing.getUTCFullYear() + years
  const month = pad(beijing.getUTCMonth() + 1)
  const day = pad(beijing.getUTCDate())
  return `${year}-${month}-${day}`
}
