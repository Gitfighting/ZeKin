<script setup>
// Owner: 胡钊炫 | Sprint 1 实现 FEAT-001/003
</script>

<template>
  <div class="app">
    <el-container>
      <el-header><h2>ZeKin 教师/管理端</h2></el-header>
      <el-main>
        <el-alert title="MVP 脚手架已就绪" type="success" :closable="false" />
        <p>规格见 specs/features/ · API 见 specs/openapi.yaml</p>
        <el-menu mode="horizontal">
          <el-menu-item index="1">审核面板</el-menu-item>
          <el-menu-item index="2">数据统计</el-menu-item>
          <el-menu-item index="3">系统管理</el-menu-item>
        </el-menu>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.app { min-height: 100vh; }
</style>
