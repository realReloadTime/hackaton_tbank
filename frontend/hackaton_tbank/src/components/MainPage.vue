<template>
  <div class="app-container">
    <!-- Заголовок -->
    <div class="header">
      <div class="user-info">
        <img src="@/assets/avatar.png" alt="User Avatar" class="user-icon" />
        <span class="user-name">{{ userName }}</span>
      </div>
      <BurgerMenu />
    </div>

    <!-- Утренняя сводка -->
    <div class="morning-summary">
      <div class="summary-header">
        <h2 class="summary-title">Утренняя сводка</h2>
        <img src="@/assets/summary-icon.png" alt="Summary Icon" class="summary-icon" />
      </div>
      <p class="summary-text">мровырпшоворваоравсис прр бъ втмв в в в втмтлатиаотитилотимлвовольмурус иблоисво морооврмировла витоавмоармоила аньа плинннли</p>
      <a href="#" class="summary-link">Подробнее <span><img src="@/assets/custom-span.png" alt="Custom Span" class="custom-span" /></span></a>
    </div>

    <!-- Новости -->
    <div class="news-section">
      <h3 class="news-title">Новости</h3>
      <NewsSlider :userName="userName" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import NewsSlider from './NewsSlider.vue';
import BurgerMenu from './BurgerMenu.vue';
import { useUserStore } from '../stores/user'
import { ref, onMounted, watch } from 'vue';

// Реактивная переменная для хранения username

const router = useRouter();
const userStore = useUserStore();
const userName = ref(userStore.username); // Инициализируем из хранилища

const initTelegramWebApp = () => {
  // 1. Пробуем получить из Telegram WebApp
  if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
    const tgUsername = window.Telegram.WebApp.initDataUnsafe.user.username;
    if (tgUsername) {
      userStore.setUsername(tgUsername);
      return;
    }
  }

  // 2. Пробуем получить из URL (?start=username)
  const urlParams = new URLSearchParams(window.location.search);
  const urlUsername = urlParams.get('start');
  if (urlUsername) {
    userStore.setUsername(urlUsername);
    return;
  }

  // 3. Если ничего не найдено, оставляем сохраненное значение
  console.warn('Username не обнаружен. Используется сохраненное значение.');
};

// Обновляем реактивную переменную при изменении хранилища
watch(() => userStore.username, (newVal) => {
  userName.value = newVal;
});

// Проверка и обработка первого входа
const handleFirstVisit = () => {
  const hasVisited = localStorage.getItem('hasVisited');
  if (!hasVisited) {
    // Перенаправление на страницу настроек при первом входе
    router.push('/ticker-preferences');
    localStorage.setItem('hasVisited', 'true'); // Устанавливаем флаг после перенаправления
  }
};

// Инициализация при монтировании компонента
onMounted(() => {
  initTelegramWebApp();
  handleFirstVisit();
});
</script>

<style scoped>
.app-container {
  background-color: #000;
  color: #fff;
  min-height: 100vh;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-icon {
  width: 32px;
  height: 32px;
  background-color: #fff;
  object-fit: cover;
  border-radius: 50%;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
}

.morning-summary {
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.summary-title {
  font-size: 18px;
  font-weight: 700;
}

.summary-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.summary-text {
  font-size: 14px;
  color: #a3a3a3;
  margin-bottom: 12px;
}

.summary-link {
  color: #FFDE21;
  text-decoration: none;
  font-size: 14px;
}

.summary-link:hover {
  text-decoration: underline;
}

.news-section {
  flex-grow: 1;
}

.news-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  border-bottom: 1px solid #333;
  padding-bottom: 4px;
}

.custom-span {
  width: 16px;
  height: 16px;
  vertical-align: middle;
}
</style>