<template>
  <div class="login-container">
    <h2>用户登录</h2>
    <div class="error-message" v-if="errorMessage" id="errorMessage">{{ errorMessage }}</div>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="userAccount">用户名</label>
        <input 
          type="text" 
          id="userAccount" 
          v-model="formData.userAccount" 
          required 
          placeholder="请输入用户名"
        >
      </div>
      <div class="form-group">
        <label for="userPassword">密码</label>
        <input 
          type="password" 
          id="userPassword" 
          v-model="formData.userPassword" 
          required 
          placeholder="请输入密码"
        >
      </div>
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authStore } from '../store/auth';

const router = useRouter();

// 表单数据
const formData = ref({
  userAccount: '',
  userPassword: ''
});

// 错误信息
const errorMessage = ref('');

// 登录处理函数
const handleLogin = () => {
    // 隐藏之前的错误信息
    errorMessage.value = '';
    
    // 用户名验证：至少4个字符，允许字母、数字或符号
    const accountRegex = /^[a-zA-Z0-9\W_]{4,}$/;
    if (!accountRegex.test(formData.value.userAccount)) {
      errorMessage.value = '用户名至少需要4个字符（字母、数字或符号）';
      return;
    }
    
    // 密码验证：至少8个字符，允许字母或数字
    const passwordRegex = /^[a-zA-Z0-9]{8,}$/;
    if (!passwordRegex.test(formData.value.userPassword)) {
      errorMessage.value = '密码至少需要8个字符（字母或数字）';
      return;
    }
    
    console.log('开始登录流程');
    
    // 直接模拟登录成功，不调用后端API
    authStore.login({
      username: formData.value.userAccount,
      email: `${formData.value.userAccount}@example.com` // 假设邮箱
    });
    
    console.log('状态管理已更新，当前登录状态:', authStore.getIsLoggedIn());
    console.log('当前用户信息:', authStore.getUser());
    
    // 获取重定向路径，如果没有则跳转到聊天页面
    const redirectPath = router.currentRoute.value.query.redirect as string || '/chat';
    console.log('准备跳转到:', redirectPath);
    
    // 使用replace方法进行跳转
    router.replace(redirectPath);
    
    console.log('跳转命令已执行');
  };
</script>

<style>
/* 添加与首页一致的网格纹背景及特效 */
body {
  background-color: white;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

body::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 0;
  animation: gridRipple 3s ease-in-out infinite;
  opacity: 0.5;
  pointer-events: none;
}

/* 网格波纹动画关键帧 - 与首页一致 */
@keyframes gridRipple {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  25%, 75% {
    transform: scale(1.02);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}
</style>

<style scoped>

.login-container {
  background: white;
  border-radius: 15px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.5s ease-out;
  margin: 100px auto;
  position: relative;
  z-index: 1;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-weight: 600;
}

.form-group {
  margin-bottom: 25px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

button:active {
  transform: translateY(0);
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
  text-align: center;
  padding: 10px;
  border-radius: 5px;
  background-color: #fee;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 25px;
    margin: 20px;
  }
  
  h2 {
    font-size: 24px;
  }
  
  input[type="text"],
  input[type="password"] {
    padding: 10px 12px;
    font-size: 14px;
  }
  
  button {
    padding: 12px;
    font-size: 14px;
  }
}


</style>