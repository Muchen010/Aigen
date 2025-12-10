<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <div class="avatar">🤖</div>
        <div class="chat-info">
          <h2>Aigen AI</h2>
          <p>智能助手</p>
        </div>
      </div>
      <div class="header-right">
        <div class="user-info">
          <span class="username">{{ authStore.getUser()?.username || '用户' }}</span>
        </div>
        <button class="header-btn">📞</button>
        <button class="header-btn">📎</button>
        <button class="header-btn">⚙️</button>
      </div>
    </div>

    <!-- 聊天内容区域 -->
    <div class="chat-content" ref="chatContent">
      <!-- 欢迎消息 -->
      <div class="welcome-message">
        <div class="welcome-avatar">🤖</div>
        <div class="welcome-text">
          <p>欢迎使用 Aigen AI 智能助手！</p>
          <p>我可以帮助您回答问题、提供建议、生成内容等。</p>
        </div>
      </div>

      <!-- 聊天历史记录 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
        <div v-if="message.isUser" class="user-message">
          <div class="user-avatar">👤</div>
          <div class="message-content user-content">
            <p>{{ message.text }}</p>
            <span class="message-time">{{ message.time }}</span>
          </div>
        </div>
        <div v-else class="ai-message">
          <div class="ai-avatar">🤖</div>
          <div class="message-content ai-content">
            <p>{{ message.text }}</p>
            <span class="message-time">{{ message.time }}</span>
          </div>
        </div>
      </div>

      <!-- AI 正在输入 -->
      <div v-if="isTyping" class="ai-message">
        <div class="ai-avatar">🤖</div>
        <div class="message-content ai-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
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
          <span v-if="!isTyping">发送</span>
          <span v-else>...</span>
        </button>
      </div>
      <p class="input-hint">Aigen AI 提供智能助手服务，请注意保护个人隐私</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { authStore } from '../store/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const chatContent = ref<HTMLElement | null>(null);
const inputText = ref('');
const messages = ref<any[]>([]);
const isTyping = ref(false);

// 模拟 AI 回复
const generateAIResponse = (userMessage: string): Promise<string> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 简单的回复逻辑，实际项目中应该调用 AI API
      const responses = [
        '这是一个很好的问题！',
        '我来帮您解答这个问题。',
        '根据我的理解，您需要的是...',
        '让我为您详细解释一下。',
        '这个问题很有趣，我认为...',
        '感谢您的提问，我会尽力帮助您。'
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      resolve(randomResponse);
    }, 1500);
  });
};

// 发送消息
const sendMessage = async () => {
  if (!inputText.value.trim()) return;

  // 添加用户消息
  const now = new Date();
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  messages.value.push({
    text: inputText.value.trim(),
    time: timeString,
    isUser: true
  });

  inputText.value = '';
  scrollToBottom();
  isTyping.value = true;

  // 生成 AI 回复
  const aiResponse = await generateAIResponse(messages.value[messages.value.length - 1].text);
  isTyping.value = false;

  // 添加 AI 回复
  messages.value.push({
    text: aiResponse,
    time: timeString,
    isUser: false
  });

  scrollToBottom();
};

// 滚动到底部
const scrollToBottom = () => {
  if (chatContent.value) {
    setTimeout(() => {
      chatContent.value!.scrollTop = chatContent.value!.scrollHeight;
    }, 100);
  }
};

// 检查用户是否登录
onMounted(() => {
  if (!authStore.getIsLoggedIn()) {
    router.push('/login');
  }
});

// 监听输入变化
const handleInputChange = (e: Event) => {
  inputText.value = (e.target as HTMLInputElement).value;
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

/* 聊天头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.chat-info h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.chat-info p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-right: 8px;
}

.header-btn {
  width: 36px;
  height: 36px;
  border: none;
  background-color: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.header-btn:hover {
  background-color: #e2e8f0;
}

/* 聊天内容区域 */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 欢迎消息 */
.welcome-message {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.welcome-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.welcome-text p {
  margin: 0 0 8px 0;
  color: #333;
  line-height: 1.5;
}

.welcome-text p:last-child {
  margin-bottom: 0;
  color: #666;
}

/* 消息样式 */
.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.user-message {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.ai-message {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

.user-avatar, .ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 8px;
}

.user-avatar {
  background-color: #4facfe;
}

.ai-avatar {
  background-color: #667eea;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.user-content {
  background-color: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-content {
  background-color: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-content p {
  margin: 0 0 8px 0;
  line-height: 1.5;
  font-size: 15px;
}

.message-time {
  font-size: 12px;
  color: #94a3b8;
  position: absolute;
  bottom: 8px;
  right: 12px;
}

.user-content .message-time {
  color: rgba(255, 255, 255, 0.7);
}

/* 输入区域 */
.input-area {
  padding: 16px 20px;
  background-color: white;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
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
  transition: color 0.3s ease;
}

.input-btn:hover {
  color: #667eea;
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
  transition: background-color 0.3s ease;
}

.send-btn:hover {
  background-color: #5a67d8;
}

.input-hint {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  margin: 0;
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #94a3b8;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 滚动条样式 */
.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background-color: #f1f5f9;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .chat-content {
    padding: 12px 16px;
  }

  .input-area {
    padding: 12px 16px;
  }
}
</style>
