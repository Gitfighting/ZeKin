<script setup lang="ts" generic="T extends Record<string, unknown>">
import { computed } from 'vue'

export interface DataColumn<T = Record<string, unknown>> {
  key: keyof T | string
  label: string
  minWidth?: number
  width?: number | string
  align?: 'left' | 'center' | 'right'
  formatter?: (row: T) => string | number
}

const props = withDefaults(
  defineProps<{
    columns: DataColumn<T>[]
    rows: T[]
    stripe?: boolean
    loading?: boolean
    rowKey?: string
  }>(),
  {
    stripe: true,
    loading: false,
    rowKey: 'id',
  },
)

const normalizedColumns = computed(() =>
  props.columns.map((column) => ({
    ...column,
    prop: String(column.key),
  })),
)
</script>

<template>
  <el-table
    :data="rows"
    :stripe="stripe"
    :row-key="rowKey"
    :loading="loading"
    class="data-table"
  >
    <el-table-column
      v-for="column in normalizedColumns"
      :key="column.prop"
      :prop="column.prop"
      :label="column.label"
      :min-width="column.minWidth ?? 120"
      :width="column.width"
      :align="column.align ?? 'left'"
      show-overflow-tooltip
    >
      <template #default="{ row }">
        <slot :name="column.prop" :row="row">
          {{ column.formatter ? column.formatter(row) : row[column.prop] }}
        </slot>
      </template>
    </el-table-column>
    <template #empty>
      <el-empty description="暂无数据" />
    </template>
  </el-table>
</template>

<style scoped lang="scss">
.data-table {
  width: 100%;
}
</style>
