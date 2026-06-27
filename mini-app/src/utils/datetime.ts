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
