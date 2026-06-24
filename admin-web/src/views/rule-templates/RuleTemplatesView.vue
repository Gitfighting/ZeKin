<script setup lang="ts">
import { ref } from 'vue'

import RuleEditor, { type RuleSection } from '../../components/RuleEditor/RuleEditor.vue'

const rules = ref<RuleSection[]>([
  { title: '时间', description: '控制签到窗口、迟到判断与补签时限。', enabled: true, summary: '工作日 06:40-07:20 允许签到，07:20 后计为迟到。' },
  { title: '地点', description: '限定允许签到的围栏或教学楼范围。', enabled: true, summary: '要求在宿舍区或教学楼东门 300 米范围内。' },
  { title: '验证', description: '图像、定位与设备可信度校验。', enabled: true, summary: '定位、设备与人脸三项至少满足两项。' },
  { title: '提交', description: '控制材料上传要求与说明字段。', enabled: true, summary: '允许图片与备注一起提交，备注最多 120 字。' },
  { title: '审核', description: '定义自动审核与人工转单策略。', enabled: true, summary: '命中高风险规则时转人工审核。' },
  { title: '提醒', description: '触发站内提醒和班级通知。', enabled: true, summary: '开始前 15 分钟推送，结束前 5 分钟二次提醒。' },
  { title: '人脸', description: '单独控制人脸比对严格度。', enabled: false, summary: '低风险任务暂不启用强制人脸。' },
])
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>规则模板</h1>
        <p>围绕时间、位置、验证、审核与提醒配置统一模板。</p>
      </div>
      <el-space>
        <el-button>另存为模板</el-button>
        <el-button type="primary">发布模板</el-button>
      </el-space>
    </div>

    <RuleEditor v-model="rules" />
  </section>
</template>
