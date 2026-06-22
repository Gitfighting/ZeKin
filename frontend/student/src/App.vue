<script setup>
// Owner: 华心仪 | Sprint 1 实现 FEAT-001/002
</script>

<template>
  <div class="app">
    <header>
      <h1>ZeKin · AI 思政打卡</h1>
      <p>学生端 MVP 脚手架 — 规格见 specs/features/</p>
    </header>
    <nav>
      <a href="#/home">首页</a>
      <a href="#/checkin">打卡</a>
      <a href="#/profile">我的</a>
    </nav>
  </div>
</template>

<style scoped>
.app { font-family: system-ui, sans-serif; padding: 1rem; max-width: 480px; margin: 0 auto; }
header { text-align: center; margin-bottom: 1.5rem; }
nav { display: flex; justify-content: space-around; }
nav a { color: #1677ff; text-decoration: none; }
</style>
