import { createApp } from 'vue';
import { createPinia } from 'pinia'; // Добавляем импорт Pinia
import App from './App.vue';
import router from './router';

// Создаем экземпляр приложения
const app = createApp(App);

// Создаем и подключаем Pinia ПЕРВОЙ
const pinia = createPinia();
app.use(pinia);

// Затем подключаем router
app.use(router);

// Монтируем приложение
app.mount('#app');