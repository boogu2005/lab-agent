<template>
  <div class="register-container auth-page">
    <div class="register-box auth-card">
      <SmartCampusLogo class="auth-logo" />
      <h1 class="auth-heading">欢迎注册实验室预约系统</h1>

      <el-form :model="form" label-width="auto" class="auth-form">
        <el-form-item>
          <el-input
            size="large"
            v-model="form.username"
            placeholder="请输入账号"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            type="password"
            size="large"
            v-model="form.password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            type="password"
            size="large"
            v-model="form.confirmPassword"
            placeholder="请确认密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <div>
          <el-button size="large" type="primary" class="auth-submit">注 册</el-button>
          <div class="auth-footer">
            已有账号？请 <a href="/login">登录</a>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import SmartCampusLogo from '@/components/SmartCampusLogo.vue'
import '@/assets/css/auth.css'

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})
</script>

