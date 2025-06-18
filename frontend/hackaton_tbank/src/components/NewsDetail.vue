<template>
  <div class="news-detail-container">
    <div class="header">
      <button class="back-button" @click="goBack">←</button>
      <button class="menu-button">☰</button>
    </div>
    <div class="news-detail-content" v-if="news">
      <h1 class="news-detail-title">Новость {{ news.new_id }}</h1>
      <p class="news-detail-text">{{ news.text }}</p>
      <p class="news-detail-meta" v-if="news.tonality">Тональность: {{ news.tonality }}</p>
      <div class="news-detail-footer">
        <p class="news-detail-meta">Создано: {{ formatDate(news.created_at) }}</p>
        <p class="news-detail-meta" v-if="news.regions && news.regions.length">Регион: {{ news.regions[0].name }}</p>
      </div>
    </div>
    <div v-else class="loading">Загрузка...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const news = ref(null);

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(async () => {
  try {
    const response = await axios.get(`http://api2.academus-pobeda.ru/news/${route.params.id}`);
    news.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке новости:', error);
  }
});

const goBack = () => {
  router.push('/news-feed');
};
</script>

<style scoped>
.news-detail-container {
  background-color: #000;
  color: #fff;
  min-height: 100vh;
  padding: 20px;
  font-family: "Nekst", sans-serif;
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

.menu-button {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.news-detail-content {
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.news-detail-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
}

.news-detail-text {
  font-size: 16px;
  color: #a3a3a3;
  margin-bottom: 16px;
}

.news-detail-meta {
  font-size: 14px;
  color: #717171;
  margin-bottom: 8px;
}

.news-detail-footer {
  margin-top: 16px;
  border-top: 1px solid #333;
  padding-top: 8px;
}

.loading {
  text-align: center;
  color: #a3a3a3;
  padding: 10px;
}
</style>