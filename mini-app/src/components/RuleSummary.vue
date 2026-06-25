<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    timeWindow: string
    locationName: string
    locationHint?: string
    requirements?: string[]
  }>(),
  {
    title: '打卡规则',
    locationHint: '',
    requirements: () => [],
  },
)
</script>

<template>
  <view class="rule-card">
    <text class="rule-card__title">{{ title }}</text>
    <view class="rule-card__row">
      <text class="rule-card__label">时间窗口</text>
      <text class="rule-card__value">{{ timeWindow }}</text>
    </view>
    <view class="rule-card__row">
      <text class="rule-card__label">签到地点</text>
      <view class="rule-card__value-group">
        <text class="rule-card__value">{{ locationName }}</text>
        <text v-if="locationHint" class="rule-card__hint">{{ locationHint }}</text>
      </view>
    </view>
    <view class="rule-card__requirements">
      <text class="rule-card__label">提交要求</text>
      <view class="rule-card__list">
        <text v-for="item in requirements" :key="item" class="rule-card__item">
          {{ item }}
        </text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.rule-card {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: rgba($primary, 0.04);
  border: 2rpx solid rgba($primary, 0.08);
}

.rule-card__title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.rule-card__row,
.rule-card__requirements {
  display: flex;
  gap: 20rpx;
}

.rule-card__label {
  width: 140rpx;
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 26rpx;
}

.rule-card__value-group,
.rule-card__list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10rpx;
}

.rule-card__value,
.rule-card__item {
  color: $text-primary;
  font-size: 26rpx;
  line-height: 1.5;
}

.rule-card__hint {
  color: $text-muted;
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
