<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'

import { isValidMapCoord, shouldUseNativeMap } from '@/utils/map-support'

const props = withDefaults(
  defineProps<{
    latitude: number
    longitude: number
    scale?: number
    markers?: Array<Record<string, unknown>>
    circles?: Array<Record<string, unknown>>
    enableTap?: boolean
    fallbackHint?: string
  }>(),
  {
    scale: 15,
    markers: () => [],
    circles: () => [],
    enableTap: false,
    fallbackHint: '地图预览（模拟器不支持原生地图，真机可正常显示）',
  },
)

const emit = defineEmits<{
  (event: 'tap', value: { latitude?: number; longitude?: number }): void
}>()

const useNativeMap = shouldUseNativeMap()
const mapVisible = ref(false)
const mapFailed = ref(false)

const showMap = computed(
  () => useNativeMap && mapVisible.value && !mapFailed.value && isValidMapCoord(props.latitude, props.longitude),
)

const fallbackRadius = computed(() => {
  const circle = props.circles[0]
  if (!circle || typeof circle.radius !== 'number') {
    return null
  }
  return circle.radius
})

function mountMap() {
  if (!useNativeMap || !isValidMapCoord(props.latitude, props.longitude)) {
    mapVisible.value = false
    return
  }
  mapVisible.value = false
  void nextTick(() => {
    setTimeout(() => {
      mapVisible.value = true
    }, 320)
  })
}

function handleMapTap(event: { detail?: { latitude?: number; longitude?: number } }) {
  if (!props.enableTap) {
    return
  }
  emit('tap', event.detail ?? {})
}

function handleMapError() {
  mapFailed.value = true
  mapVisible.value = false
}

onMounted(() => {
  mountMap()
})
</script>

<template>
  <view class="mini-map">
    <map
      v-if="showMap"
      class="mini-map__canvas"
      :latitude="latitude"
      :longitude="longitude"
      :scale="scale"
      :markers="markers"
      :circles="circles"
      enable-scroll
      enable-zoom
      @tap="handleMapTap"
      @error="handleMapError"
      @rendererror="handleMapError"
    />
    <view v-else class="mini-map__fallback">
      <view class="mini-map__fallback-pin" />
      <text class="mini-map__fallback-title">位置预览</text>
      <text class="mini-map__fallback-coords">
        纬度 {{ latitude.toFixed(6) }} · 经度 {{ longitude.toFixed(6) }}
      </text>
      <text v-if="fallbackRadius" class="mini-map__fallback-radius">
        打卡范围 {{ fallbackRadius }} 米
      </text>
      <text class="mini-map__fallback-hint">{{ fallbackHint }}</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.mini-map {
  width: 100%;
  height: 100%;
}

.mini-map__canvas {
  width: 100%;
  height: 100%;
}

.mini-map__fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  width: 100%;
  height: 100%;
  min-height: 360rpx;
  padding: 32rpx;
  box-sizing: border-box;
  background:
    radial-gradient(circle at 50% 42%, rgba(22, 119, 255, 0.18), transparent 58%),
    linear-gradient(180deg, #eef5ff 0%, #f8fbff 100%);
}

.mini-map__fallback-pin {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: #1677ff;
  box-shadow: 0 0 0 12rpx rgba(22, 119, 255, 0.18);
}

.mini-map__fallback-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2937;
}

.mini-map__fallback-coords,
.mini-map__fallback-radius,
.mini-map__fallback-hint {
  font-size: 22rpx;
  color: #667085;
  text-align: center;
  line-height: 1.5;
}

.mini-map__fallback-hint {
  margin-top: 8rpx;
  color: #98a2b3;
}
</style>
