// 简单的状态管理，用于管理用户登录状态
import { reactive } from 'vue';

interface UserState {
  isLoggedIn: boolean;
  user: {
    username: string;
    email: string;
  } | null;
}

class AuthStore {
  private state: UserState;

  constructor() {
    this.state = reactive({
      isLoggedIn: localStorage.getItem('isLoggedIn') === 'true',
      user: JSON.parse(localStorage.getItem('user') || 'null')
    });
  }

  // 登录
  login(userData: { username: string; email: string }) {
    this.state.isLoggedIn = true;
    this.state.user = userData;
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('user', JSON.stringify(userData));
  }

  // 注册
  register(userData: { username: string; email: string }) {
    // 注册后自动登录
    this.login(userData);
  }

  // 登出
  logout() {
    this.state.isLoggedIn = false;
    this.state.user = null;
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('user');
  }

  // 获取登录状态
  getIsLoggedIn(): boolean {
    return this.state.isLoggedIn;
  }

  // 获取用户信息
  getUser() {
    return this.state.user;
  }
}

export const authStore = new AuthStore();
