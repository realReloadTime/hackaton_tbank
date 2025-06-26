import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    username: localStorage.getItem('username') || 'User'
  }),
  actions: {
    setUsername(username) {
      this.username = username;
      localStorage.setItem('username', username); // Сохраняем в localStorage
    }
  }
});