import {
  formatBeijingDateNow,
  maxBeijingDate,
  parseBeijingDate,
  type BeijingDateParts,
} from '@/utils/datetime'

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate()
}

function toDateString(parts: BeijingDateParts): string {
  return `${parts.year}-${pad(parts.month)}-${pad(parts.day)}`
}

function clampParts(parts: BeijingDateParts, min: BeijingDateParts, max: BeijingDateParts): BeijingDateParts {
  const value = toDateString(parts)
  const minStr = toDateString(min)
  const maxStr = toDateString(max)
  if (value < minStr) {
    return { ...min }
  }
  if (value > maxStr) {
    return { ...max }
  }
  return parts
}

function buildYearLabels(min: BeijingDateParts, max: BeijingDateParts): string[] {
  const labels: string[] = []
  for (let year = min.year; year <= max.year; year += 1) {
    labels.push(`${year}年`)
  }
  return labels
}

function buildMonthLabels(year: number, min: BeijingDateParts, max: BeijingDateParts): string[] {
  const start = year === min.year ? min.month : 1
  const end = year === max.year ? max.month : 12
  const labels: string[] = []
  for (let month = start; month <= end; month += 1) {
    labels.push(`${pad(month)}月`)
  }
  return labels
}

function buildDayLabels(year: number, month: number, min: BeijingDateParts, max: BeijingDateParts): string[] {
  const start = year === min.year && month === min.month ? min.day : 1
  const end = year === max.year && month === max.month
    ? max.day
    : daysInMonth(year, month)
  const labels: string[] = []
  for (let day = start; day <= end; day += 1) {
    labels.push(`${pad(day)}日`)
  }
  return labels
}

function partsFromColumns(
  years: string[],
  months: string[],
  days: string[],
  indexes: number[],
): BeijingDateParts {
  const year = Number.parseInt(years[indexes[0] ?? 0]?.replace('年', '') ?? '0', 10)
  const month = Number.parseInt(months[indexes[1] ?? 0]?.replace('月', '') ?? '0', 10)
  const day = Number.parseInt(days[indexes[2] ?? 0]?.replace('日', '') ?? '0', 10)
  return { year, month, day }
}

export interface BeijingDatePickerState {
  range: string[][]
  indexes: number[]
  displayDate: string
}

export function createBeijingDatePickerState(
  value: string | undefined,
  minDate: string,
  maxDate: string,
): BeijingDatePickerState {
  const min = parseBeijingDate(minDate) ?? parseBeijingDate(formatBeijingDateNow())!
  const max = parseBeijingDate(maxDate) ?? min
  const initial = clampParts(parseBeijingDate(value) ?? min, min, max)

  const years = buildYearLabels(min, max)
  const months = buildMonthLabels(initial.year, min, max)
  const days = buildDayLabels(initial.year, initial.month, min, max)

  const indexes = [
    Math.max(0, years.findIndex((item) => item.startsWith(String(initial.year)))),
    Math.max(0, months.findIndex((item) => item.startsWith(pad(initial.month)))),
    Math.max(0, days.findIndex((item) => item.startsWith(pad(initial.day)))),
  ]

  return {
    range: [years, months, days],
    indexes,
    displayDate: toDateString(initial),
  }
}

export function rebuildBeijingDatePickerColumn(
  state: BeijingDatePickerState,
  minDate: string,
  maxDate: string,
  column: number,
  columnIndex: number,
): BeijingDatePickerState {
  const min = parseBeijingDate(minDate)!
  const max = parseBeijingDate(maxDate)!
  const current = partsFromColumns(state.range[0], state.range[1], state.range[2], state.indexes)
  const nextIndexes = [...state.indexes]
  nextIndexes[column] = columnIndex

  let parts = partsFromColumns(state.range[0], state.range[1], state.range[2], nextIndexes)
  parts = clampParts(parts, min, max)

  const years = buildYearLabels(min, max)
  if (column <= 0) {
    parts.year = Number.parseInt(years[nextIndexes[0] ?? 0]?.replace('年', '') ?? String(min.year), 10)
  }

  const months = buildMonthLabels(parts.year, min, max)
  if (column <= 1) {
    const monthIndex = column === 1 ? columnIndex : Math.max(0, months.findIndex((item) => item.startsWith(pad(parts.month))))
    parts.month = Number.parseInt(months[monthIndex]?.replace('月', '') ?? String(min.month), 10)
  }

  const days = buildDayLabels(parts.year, parts.month, min, max)
  parts = clampParts(parts, min, max)

  const indexes = [
    Math.max(0, years.findIndex((item) => item.startsWith(String(parts.year)))),
    Math.max(0, months.findIndex((item) => item.startsWith(pad(parts.month)))),
    Math.max(0, days.findIndex((item) => item.startsWith(pad(parts.day)))),
  ]

  return {
    range: [years, months, days],
    indexes,
    displayDate: toDateString(parts),
  }
}

export function resolveMinTaskDate(minDate?: string): string {
  return maxBeijingDate(minDate ?? formatBeijingDateNow(), formatBeijingDateNow())
}
