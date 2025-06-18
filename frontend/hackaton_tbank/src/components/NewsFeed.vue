<template>
  <div class="news-feed-container" ref="feedContainer">
    <div class="header">
      <button class="back-button" @click="goBack">←</button>
      <h1 class="news-title">Новости</h1>
      <BurgerMenu />
    </div>
    <div v-for="(news, index) in newsItems" :key="index" class="news-item" @click="goToDetail(news.new_id)">
      <div class="news-content">
        <h2 class="news-item-title">Новость {{ index + 1 }}</h2>
        <p class="news-item-text">мровырпшоворваоравсис прр бъ втмв в в в втмтлатиаотитилотимлвовольмурус иблоисво</p>
      </div>
      <a href="#" class="news-link" @click.stop="goToDetail(news.new_id)">Подробнее <span>➡️</span></a>
    </div>
    <div v-if="isLoading" class="loading">Загрузка...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import BurgerMenu from './BurgerMenu.vue';

const newsItems = ref([]);
const router = useRouter();
const skip = ref(0);
const limit = ref(10);
const isLoading = ref(false);
const feedContainer = ref(null);

const loadNews = async () => {
  if (isLoading.value) return;

  isLoading.value = true;
  try {
    const response = await axios.get('http://api2.academus-pobeda.ru/news/', {
      params: {
        username: '@ТР ссылка',
        skip: skip.value,
        limit: limit.value
      }
    });
    newsItems.value = skip.value === 0 ? response.data : [...newsItems.value, ...response.data];
    skip.value += limit.value;
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleScroll = () => {
  const container = feedContainer.value;
  if (!container) return;

  const { scrollTop, clientHeight, scrollHeight } = container;
  if (scrollTop + clientHeight >= scrollHeight - 10 && !isLoading.value) {
    loadNews();
  }
};

onMounted(async () => {
  await loadNews();
  const container = feedContainer.value;
  if (container) {
    container.addEventListener('scroll', handleScroll);
  }
});

onUnmounted(() => {
  const container = feedContainer.value;
  if (container) {
    container.removeEventListener('scroll', handleScroll);
  }
});

const goBack = () => {
  router.push('/');
};

const goToDetail = (newId) => {
  router.push(`/news/${newId}`);
};
</script>

<style scoped>
.news-feed-container {
  background-color: #000;
  color: #fff;
  min-height: 100vh;
  padding: 20px;
  font-family: "Nekst", sans-serif;
  overflow-y: auto;
  max-height: 80vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
  margin-bottom: 20px;
}

.back-button {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.news-title {
  font-size: 24px;
  font-weight: 600;
}

.news-item {
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  border: 2px solid #00f;
  cursor: pointer;
}

.news-content {
  margin-bottom: 8px;
}

.news-item-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.news-item-text {
  font-size: 14px;
  color: #a3a3a3;
}

.news-link {
  color: #f59e0b;
  text-decoration: none;
  font-size: 14px;
}

.news-link:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  color: #a3a3a3;
  padding: 10px;
}
</style>