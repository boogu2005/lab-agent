<template>
  <div class="login-container auth-page">
    <div class="login-box auth-card">
      <SmartCampusLogo class="auth-logo" />
      <h1 class="auth-heading">财经大学实验室预约系统</h1>
      <div class="auth-subtitle">基于AI-Agent的智能预约系统</div>

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
        <div>
          <el-button
            size="large"
            type="primary"
            class="auth-submit"
            @click="login"
            :loading="loadingValue"
            >登 录</el-button
          >
          <div class="auth-footer">
            还没有账号？请 <a href="/register">注册</a>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { loginApi } from '@/api/auth'
import { useUser } from '@/utils/user'
import SmartCampusLogo from '@/components/SmartCampusLogo.vue'
import '@/assets/css/auth.css'

const { saveLoginData } = useUser()

const form = reactive({
  username: '',
  password: ''
})

const loadingValue = ref(false)

const login = async () => {
  loadingValue.value = true
  const res = await loginApi(form)
  loadingValue.value = false
  if (res.code === 200) {
    saveLoginData(res.data)
    ElMessage.success('登录成功')
    router.push('/manager/home')
  }
}
</script>

