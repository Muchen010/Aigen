<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<template>
  <div class="app-container">
    <RouterView />
    <!-- 全局底部声明 -->
    <div class="global-declaration">
      <div class="declaration-content">
        <span class="declaration-icon">©</span>
        <span class="declaration-text">版权所有 2023 Aigen平台. 保留所有权利.</span>
      </div>
    </div>
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 全局底部声明样式 */
.global-declaration {
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 16px 20px;
  margin-top: auto;
  width: 100%;
  box-sizing: border-box;
}

.declaration-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.declaration-icon {
  font-weight: bold;
  color: #475569;
}

.declaration-text {
  line-height: 1.5;
}
</style>
