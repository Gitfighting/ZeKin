<script setup lang="ts">
import type { DynamicField } from '@/services/student'

const props = withDefaults(
  defineProps<{
    fields?: DynamicField[]
    modelValue?: Record<string, string>
  }>(),
  {
    fields: () => [],
    modelValue: () => ({}),
  },
)

const emit = defineEmits<{
  (event: 'update:modelValue', value: Record<string, string>): void
}>()

function updateField(key: string, value: string) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value,
  })
}

function valueOf(key: string) {
  return props.modelValue[key] ?? ''
}
</script>

<template>
  <view class="dynamic-form">
    <view v-for="field in fields" :key="field.key" class="dynamic-form__field">
      <text class="dynamic-form__label">{{ field.label }}</text>

      <textarea
        v-if="field.type === 'textarea'"
        class="dynamic-form__textarea"
        :maxlength="field.maxLength ?? 140"
        :placeholder="field.placeholder"
        :value="valueOf(field.key)"
        @input="updateField(field.key, $event.detail.value)"
      />

      <input
        v-else
        class="dynamic-form__input"
        :maxlength="field.maxLength ?? 32"
        :type="field.type === 'number' ? 'number' : 'text'"
        :placeholder="field.placeholder"
        :value="valueOf(field.key)"
        @input="updateField(field.key, $event.detail.value)"
      />
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.dynamic-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.dynamic-form__field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.dynamic-form__label {
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
}

.dynamic-form__input,
.dynamic-form__textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 24rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
}

.dynamic-form__textarea {
  min-height: 180rpx;
}
</style>
