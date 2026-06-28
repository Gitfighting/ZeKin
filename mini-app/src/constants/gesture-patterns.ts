export interface GesturePreset {
  id: string
  label: string
  sequence: number[]
}

/** 九宫格编号：1 2 3 / 4 5 6 / 7 8 9 */
export const GESTURE_PRESETS: GesturePreset[] = [
  { id: 'Z', label: 'Z 形', sequence: [1, 2, 3, 6, 9] },
  { id: 'N', label: 'N 形', sequence: [1, 4, 7, 5, 3, 9] },
  { id: 'L', label: 'L 形', sequence: [1, 4, 7, 8, 9] },
]

export function sequenceToPatternId(sequence: number[]): string {
  return sequence.filter((item) => item >= 1 && item <= 9).join('')
}

export function patternIdToSequence(pattern?: string | null): number[] {
  const raw = (pattern ?? '').trim()
  if (!raw) {
    return []
  }
  if (/^\d+$/.test(raw)) {
    return raw.split('').map(Number).filter((item) => item >= 1 && item <= 9)
  }
  const preset = GESTURE_PRESETS.find((item) => item.id.toUpperCase() === raw.toUpperCase())
  return preset ? [...preset.sequence] : []
}

export function patternDisplayLabel(pattern?: string | null): string {
  const raw = (pattern ?? '').trim()
  if (!raw) {
    return '未设置手势'
  }
  const sequence = patternIdToSequence(raw)
  const preset = GESTURE_PRESETS.find(
    (item) =>
      item.id.toUpperCase() === raw.toUpperCase()
      || sequenceToPatternId(item.sequence) === raw,
  )
  if (preset) {
    return preset.label
  }
  if (sequence.length) {
    return sequence.join(' → ')
  }
  return raw
}

export function normalizePatternId(pattern?: string | null): string {
  const sequence = patternIdToSequence(pattern)
  if (sequence.length) {
    return sequenceToPatternId(sequence)
  }
  return (pattern ?? '').trim()
}
