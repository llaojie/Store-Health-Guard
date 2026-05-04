<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>🏥 门店健康卫士</h2>
        <p class="subtitle">Store Health Guard</p>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#1a1a2e"
        text-color="#e0e0e0"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>门店总览</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <span>预警中心</span>
        </el-menu-item>
        <el-menu-item index="/diagnosis">
          <el-icon><Stethoscope /></el-icon>
          <span>诊断工具</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <p>v1.0.0 · 开源</p>
      </div>
    </el-aside>

    <!-- 主内容 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { Monitor, Bell } from '@element-plus/icons-vue'
</script>

<style scoped>
/* Stethoscope icon doesn't exist in element-plus, using a workaround */
.app-layout {
  height: 100vh;
}
.sidebar {
  background: #1a1a2e;
  overflow: hidden;
}
.logo {
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid #2a2a4a;
}
.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}
.logo .subtitle {
  color: #888;
  font-size: 11px;
  margin: 4px 0 0;
}
.sidebar-footer {
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 220px;
  text-align: center;
}
.sidebar-footer p {
  color: #555;
  font-size: 11px;
}
.main-content {
  background: #f0f2f5;
  overflow-y: auto;
}
</style>

<style>
body { margin: 0; padding: 0; }
#app { height: 100vh; }
</style>
