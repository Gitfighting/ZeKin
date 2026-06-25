<script setup lang="ts">
export interface OrgTreeNode {
  id: number
  label: string
  type: string
  children?: OrgTreeNode[]
}

defineProps<{
  data: OrgTreeNode[]
}>()

const emit = defineEmits<{
  select: [node: OrgTreeNode]
}>()

const handleNodeClick = (node: OrgTreeNode) => {
  emit('select', node)
}
</script>

<template>
  <div class="org-tree sz-card">
    <div class="org-tree__header">
      <div>
        <h3>组织结构</h3>
        <p>学院、年级、专业与班级分层管理</p>
      </div>
      <el-tag type="primary" effect="plain">树形视图</el-tag>
    </div>
    <el-tree
      :data="data"
      node-key="id"
      default-expand-all
      highlight-current
      :expand-on-click-node="false"
      @node-click="handleNodeClick"
    >
      <template #default="{ data: node }">
        <div class="org-tree__node">
          <span>{{ node.label }}</span>
          <el-tag size="small" effect="plain">{{ node.type }}</el-tag>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<style scoped lang="scss">
.org-tree {
  padding: 16px;
}

.org-tree__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    font-size: 16px;
  }

  p {
    margin: 4px 0 0;
    color: var(--sz-muted);
    font-size: 13px;
  }
}

.org-tree__node {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 0;
}
</style>
