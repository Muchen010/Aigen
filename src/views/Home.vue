<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="logo">Aigen</router-link>
        <div class="nav-actions">
          <ul class="nav-links">
            <li><router-link to="#">首页</router-link></li>
            <li><router-link to="#">功能</router-link></li>
            <li><router-link to="#">模板</router-link></li>
            <li><router-link to="#">价格</router-link></li>
            <li><router-link to="#">文档</router-link></li>
          </ul>
          
          <!-- 未登录状态 -->
          <div v-if="!authStore.getIsLoggedIn()" class="auth-buttons">
            <router-link to="/login" class="login-nav-button">登录</router-link>
          </div>
          
          <!-- 已登录状态 -->
          <div v-else class="user-info">
            <span class="username">{{ authStore.getUser()?.username }}</span>
            <button class="logout-button" @click="handleLogout">注销</button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 英雄区域 -->
    <section class="hero">
      <div class="hero-container">
        <div class="hero-content">
          <h1>无需代码，轻松构建专业应用</h1>
          <p>使用我们的可视化开发平台，无需编程知识即可创建网站、应用程序和工作流。</p>
          
        </div>
        
        <!-- 注册按钮（仅未登录时显示） -->
        <router-link v-if="!authStore.getIsLoggedIn()" to="/register" class="login-button">立即注册</router-link>
      </div>
    </section>

    <!-- 功能展示区域 -->
    <section class="features">
      <div class="features-container">
        <h2 class="section-title">强大功能，简单操作</h2>
        
        <!-- 添加智能助手输入框 -->
        <div class="input-area">
          <div class="input-wrapper">
            <button class="input-btn">📎</button>
            <button class="input-btn">🎤</button>
            <input
              v-model="inputText"
              type="text"
              placeholder="输入您的问题或指令..."
              @keyup.enter="sendMessage"
            />
            <button class="send-btn" @click="sendMessage">
              发送
            </button>
          </div>
        </div>
        

        
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>可视化拖拽</h3>
            <p>通过直观的拖拽界面构建应用，所见即所得，无需编写任何代码。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔌</div>
            <h3>丰富的集成</h3>
            <p>与数百个第三方服务集成，轻松扩展应用功能。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>响应式设计</h3>
            <p>自动适配各种设备，确保应用在任何屏幕上都能完美显示。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>快速部署</h3>
            <p>一键部署到全球服务器，享受高性能和可靠性。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>企业级安全</h3>
            <p>多层安全防护，确保您的数据安全可靠。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>数据分析</h3>
            <p>内置数据分析工具，帮助您了解用户行为和应用性能。</p>
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { authStore } from '../store/auth';

// 智能助手输入框功能
const inputText = ref('');

const sendMessage = () => {
  if (!inputText.value.trim()) return;
  // 这里可以添加发送消息的逻辑
  console.log('发送消息:', inputText.value);
  // 跳转到聊天页面
  router.push('/chat');
  inputText.value = '';
};

const router = useRouter();

// 处理注销操作
const handleLogout = () => {
  if (window.confirm('确定要注销吗？')) {
    authStore.logout();
    router.push('/');
  }
};

// 滚动触发动画
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// 导航栏滚动效果
const handleScroll = () => {
  const navbar = document.querySelector('.navbar') as HTMLElement;
  if (window.scrollY > 50) {
    navbar!.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
    navbar!.style.backdropFilter = 'blur(10px)';
  } else {
    navbar!.style.backgroundColor = 'white';
    navbar!.style.backdropFilter = 'none';
  }
};

// 平滑滚动效果
const handleSmoothScroll = () => {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      const href = anchor.getAttribute('href');
      if (href) {
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });
};

// 节流函数 - 进一步降低触发频率
const throttle = (func: Function, delay: number) => {
  let lastCall = 0;
  return function(...args: any[]) {
    const now = new Date().getTime();
    if (now - lastCall < delay) {
      return;
    }
    lastCall = now;
    return func.apply(this, args);
  };
};

// 移除鼠标波纹效果以提高性能
const handleRipple = () => {};
const throttledHandleRipple = () => {};

onMounted(() => {
  // 观察所有功能卡片
  const featureCards = document.querySelectorAll('.feature-card');
  featureCards.forEach(card => {
    observer.observe(card);
  });
  
  // 添加滚动事件监听（使用节流）
  const throttledHandleScroll = throttle(handleScroll, 100);
  window.addEventListener('scroll', throttledHandleScroll);
  
  // 添加平滑滚动
  handleSmoothScroll();
  
  // 存储事件监听器以便移除
  (window as any).throttledHandleScroll = throttledHandleScroll;
});

onUnmounted(() => {
  // 移除事件监听
  window.removeEventListener('scroll', (window as any).throttledHandleScroll);
});
</script>

<style scoped>
/* 首页容器样式 - 鼠标波纹 */
.home-container {
  position: relative;
  overflow: hidden;
  background-color: #ffffff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 确保页面内容填充视口 */
body {
  overflow-x: hidden;
}

/* 确保app容器填充视口 */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 鼠标波纹样式 */
.ripple {
  position: absolute;
  border-radius: 50%;
  background-color: rgba(102, 126, 234, 0.3);
  transform: scale(0);
  pointer-events: none;
  animation: ripple-animation 1.5s ease-out;
  z-index: 0;
  border: 1px solid rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
}

/* 波纹动画 */
@keyframes ripple-animation {
  0% {
    transform: scale(0);
    opacity: 0.7;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}
/* 导航栏样式 */
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  text-decoration: none;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 30px;
}

.nav-links a {
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-links a:hover {
  color: #667eea;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.login-nav-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.login-nav-button {
  position: relative;
  overflow: hidden;
}

.login-nav-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-nav-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-nav-button:hover::after {
  left: 100%;
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: #333;
  font-weight: 600;
  font-size: 16px;
}

.logout-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 英雄区域样式 */
.hero {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 20%, #f093fb 40%, #f5576c 60%, #4facfe 80%, #667eea 100%);
  background-size: 400% 100%;
  color: white;
  padding: 60px 0;
  position: relative;
  overflow: hidden;
  animation: gradientFlow 15s ease infinite;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
  animation: float 10s ease-in-out infinite;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-content {
  text-align: center;
  max-width: 800px;
  animation: slideUp 0.8s ease-out forwards;
  opacity: 0;
}

.hero-content h1 {
  animation: slideUp 0.8s ease-out 0.2s forwards;
  opacity: 0;
}

.hero-content p {
  animation: slideUp 0.8s ease-out 0.4s forwards;
  opacity: 0;
}

.hero-content .cta-button {
  animation: slideUp 0.8s ease-out 0.6s forwards;
  opacity: 0;
}

.login-button {
  animation: slideUp 0.8s ease-out 0.8s forwards;
  opacity: 0;
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-content p {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.cta-button {
  display: inline-block;
  padding: 15px 30px;
  background-color: white;
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.cta-button {
  position: relative;
  overflow: hidden;
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.cta-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.2), transparent);
  transition: left 0.5s;
}

.cta-button:hover::after {
  left: 100%;
}

/* 登录按钮样式 */
.login-button {
  padding: 15px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
  display: inline-block;
}

.login-button {
  position: relative;
  overflow: hidden;
}

.login-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-button:hover::after {
  left: 100%;
}

/* 智能助手输入框样式 */
.input-area {
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
  animation: fadeInOut 1.2s ease-in-out;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-radius: 24px;
  margin-bottom: 8px;
}

.input-btn {
  width: 36px;
  height: 36px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.3s ease-in-out;
  opacity: 0.8;
  transform: scale(1);
}

.input-btn:hover {
  color: #667eea;
  opacity: 1;
  transform: scale(1.1);
  animation: fadeInOut 0.6s ease-in-out;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background-color: transparent;
  padding: 10px 8px;
  font-size: 15px;
  outline: none;
}

.input-wrapper input::placeholder {
  color: #94a3b8;
}

.send-btn {
  padding: 10px 16px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 18px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease-in-out;
  opacity: 0.9;
  transform: scale(1);
}

.send-btn:hover {
  background-color: #5a67d8;
  opacity: 1;
  transform: scale(1.05);
}

/* 保留原始样式，但添加ID选择器确保可见 */
.input-hint {
  font-size: 14px;
  color: #334155;
  text-align: center;
  margin: 16px auto 0;
  opacity: 1;
  transition: all 0.3s ease;
  display: block;
  visibility: visible;
  height: auto;
  overflow: visible;
  position: relative;
  z-index: 100;
  padding: 10px 16px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  width: 90%;
  max-width: 500px;
  border: 1px solid #e2e8f0;
}



/* 页面加载时的渐入渐出动画 */
@keyframes fadeInOut {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  50% {
    opacity: 0.9;
    transform: translateY(-5px) scale(1.02);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 功能展示区域样式 - 带波纹动效的网格纹 */
.features {
  padding: 60px 0;
  background-color: white;
  position: relative;
  flex-grow: 1;
}

.features::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(rgba(102, 126, 234, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(102, 126, 234, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridRipple 3s ease-in-out infinite;
}

/* 网格波纹动画关键帧 */
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

.features-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 40px;
  color: #333;
  transition: transform 0.3s ease;
}

.section-title:hover {
  transform: scale(1.1);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 0;
}

.feature-card {
  background-color: #f8fafc;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease, background-color 0.5s ease;
  opacity: 0;
  transform: translateY(30px);
}

/* 添加滚动触发动画 */
.feature-card.animate {
  animation: slideUp 0.6s ease-out forwards;
}

/* 为每个卡片设置不同的延迟 */
.feature-card:nth-child(1) {
  animation-delay: 0.1s;
}

.feature-card:nth-child(2) {
  animation-delay: 0.2s;
}

.feature-card:nth-child(3) {
  animation-delay: 0.3s;
}

.feature-card:nth-child(4) {
  animation-delay: 0.4s;
}

.feature-card:nth-child(5) {
  animation-delay: 0.5s;
}

.feature-card:nth-child(6) {
  animation-delay: 0.6s;
}

.feature-card:hover {
  transform: translateY(-20px) scale(1.1);
  box-shadow: 0 25px 40px rgba(0, 0, 0, 0.15);
  background-color: #e2e8f0;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
  animation: pulse 0.6s ease-in-out;
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: white;
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* 页脚样式 */


/* 动画效果 */
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

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

/* 全局自适应滚动条样式 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background-color: #f8fafc;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
  border: 2px solid #f8fafc;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* Firefox 滚动条样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f8fafc;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-content h1 {
    font-size: 42px;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .hero-container {
    flex-direction: column;
    gap: 30px;
  }

  .hero-content h1 {
    font-size: 36px;
  }
  
  .hero-content p {
    font-size: 18px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .section-title {
    font-size: 30px;
  }
  
  .hero {
    padding: 60px 0;
  }
}

@media (max-width: 480px) {
  .hero-content h1 {
    font-size: 28px;
  }
  
  .hero-content p {
    font-size: 16px;
  }
  
  .cta-button,
  .login-button {
    padding: 12px 24px;
    font-size: 14px;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .hero {
    padding: 40px 0;
  }
  
  .features {
    padding: 60px 0;
  }
}
</style>
