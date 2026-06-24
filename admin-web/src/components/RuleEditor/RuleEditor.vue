<script setup lang="ts">
export interface RuleSection {
  title: string
  description: string
  enabled: boolean
  summary: string
}

const model = defineModel<RuleSection[]>({
  default: () => [],
})
</script>

<template>
  <div class="rule-editor">
    <div v-for="section in model" :key="section.title" class="rule-editor__item sz-card">
      <div class="rule-editor__head">
        <div>
          <h3>{{ section.title }}</h3>
          <p>{{ section.description }}</p>
        </div>
        <el-switch v-model="section.enabled" />
      </div>
      <el-input
        v-model="section.summary"
        type="textarea"
        :rows="3"
        resize="none"
        placeholder="填写规则说明"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.rule-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-editor__item {
  padding: 16px;
}

.rule-editor__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;

  h3 {
    margin: 0;
    font-size: 15px;
  }

  p {
    margin: 4px 0 0;
    color: var(--sz-muted);
    font-size: 13px;
    line-height: 1.5;
  }
}
</style>
