function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function parseClock(value: string): { hour: number; minute: number } {
  const [hourText, minuteText] = value.split(':')
  return {
    hour: Number.parseInt(hourText ?? '0', 10),
    minute: Number.parseInt(minuteText ?? '0', 10),
  }
}

function toClockString(hour: number, minute: number): string {
  return `${pad(hour)}:${pad(minute)}`
}

function compareClock(a: string, b: string): number {
  if (a === b) {
    return 0
  }
  return a < b ? -1 : 1
}

function clampClock(value: string, min: string): string {
  return compareClock(value, min) < 0 ? min : value
}

function buildHourLabels(min: { hour: number; minute: number }): string[] {
  const labels: string[] = []
  for (let hour = min.hour; hour <= 23; hour += 1) {
    labels.push(`${pad(hour)}时`)
  }
  return labels
}

function buildMinuteLabels(hour: number, min: { hour: number; minute: number }): string[] {
  const start = hour === min.hour ? min.minute : 0
  const labels: string[] = []
  for (let minute = start; minute <= 59; minute += 1) {
    labels.push(`${pad(minute)}分`)
  }
  return labels
}

function partsFromColumns(hours: string[], minutes: string[], indexes: number[]) {
  const hour = Number.parseInt(hours[indexes[0] ?? 0]?.replace('时', '') ?? '0', 10)
  const minute = Number.parseInt(minutes[indexes[1] ?? 0]?.replace('分', '') ?? '0', 10)
  return { hour, minute }
}

export interface BeijingTimePickerState {
  range: string[][]
  indexes: number[]
  displayTime: string
}

export function createBeijingTimePickerState(value: string | undefined, minTime: string): BeijingTimePickerState {
  const min = parseClock(minTime)
  const initial = parseClock(clampClock(value || minTime, minTime))

  const hours = buildHourLabels(min)
  const minutes = buildMinuteLabels(initial.hour, min)

  const indexes = [
    Math.max(0, hours.findIndex((item) => item.startsWith(pad(initial.hour)))),
    Math.max(0, minutes.findIndex((item) => item.startsWith(pad(initial.minute)))),
  ]

  return {
    range: [hours, minutes],
    indexes,
    displayTime: toClockString(initial.hour, initial.minute),
  }
}

export function rebuildBeijingTimePickerColumn(
  state: BeijingTimePickerState,
  minTime: string,
  column: number,
  columnIndex: number,
): BeijingTimePickerState {
  const min = parseClock(minTime)
  const nextIndexes = [...state.indexes]
  nextIndexes[column] = columnIndex

  let parts = partsFromColumns(state.range[0], state.range[1], nextIndexes)
  if (column === 0) {
    parts.hour = Number.parseInt(state.range[0][columnIndex]?.replace('时', '') ?? String(min.hour), 10)
  }

  const hours = buildHourLabels(min)
  const minutes = buildMinuteLabels(parts.hour, min)
  parts = partsFromColumns(hours, minutes, [
    Math.max(0, hours.findIndex((item) => item.startsWith(pad(parts.hour)))),
    Math.max(0, minutes.findIndex((item) => item.startsWith(pad(parts.minute)))),
  ])

  const clock = toClockString(parts.hour, parts.minute)
  const displayTime = clampClock(clock, minTime)

  const indexes = [
    Math.max(0, hours.findIndex((item) => item.startsWith(displayTime.slice(0, 2)))),
    Math.max(0, minutes.findIndex((item) => item.startsWith(displayTime.slice(3, 5)))),
  ]

  return {
    range: [hours, minutes],
    indexes,
    displayTime,
  }
}
