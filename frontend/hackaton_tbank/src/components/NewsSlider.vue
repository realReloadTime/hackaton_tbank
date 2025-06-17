<template>
  <div class="slider-container">
    <swiper
      :slides-per-view="1"
      :pagination="{ el: '.swiper-pagination', clickable: true }"
      class="swiper"
    >
      <swiper-slide v-for="news in newsItems" :key="news.new_id">
        <div class="news-slide">
          <h4 class="news-slide-title">Новость {{ news.new_id }}</h4>
          <p class="news-slide-text">{{ news.text }}</p>
          <p v-if="news.tonality" class="news-slide-tonality">Тональность: {{ news.tonality }}</p>
          <p v-if="news.created_at" class="news-slide-date">Создано: {{ news.created_at }}</p>
          <div v-if="news.regions" class="news-slide-regions">
            <p v-for="region in news.regions" :key="region.region_id" class="news-slide-region">{{ region.name }}</p>
          </div>
        </div>
      </swiper-slide>
    </swiper>

    <div class="slider-controls">
      <button class="read-more-button" @click="goToNewsFeed">Читать больше</button>
    </div>
    <div class="swiper-pagination"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/css';
import 'swiper/css/pagination';

const props = defineProps(['userName']);
const newsItems = ref([]);
const router = useRouter();

onMounted(async () => {
  try {
    console.log('Fetching news data...');
    const response = await axios.get('http://your-backend/api/news', {
      params: {
        username: props.userName, // Используем переданный username в запросе
      }
    });
    newsItems.value = response.data;
    console.log('News data loaded:', newsItems.value);
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error);
  }
});

const goToNewsFeed = () => {
  console.log('Button clicked, navigating to news-feed');
  router.push('/news-feed').catch(err => console.error('Navigation error:', err));
};
</script>

<style scoped>
.slider-container {
  width: 100%;
}

.swiper {
  width: 100%;
  height: auto;
}

.news-slide {
  background-color: #262626;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.news-slide-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.news-slide-text {
  font-size: 14px;
  color: #a3a3a3;
  margin-bottom: 8px;
}

.news-slide-tonality,
.news-slide-date,
.news-slide-region {
  font-size: 12px;
  color: #717171;
  margin-bottom: 4px;
}

.news-slide-regions {
  margin-top: 8px;
}

.slider-controls {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.read-more-button {
  background-color: #FFDE21;
  color: #000;
  padding: 10px 24px;
  border: none;
  border-radius: 9999px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.read-more-button:hover {
  background-color: #FFDE21;
}

.swiper-pagination {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.swiper-pagination-bullet {
  width: 8px;
  height: 8px;
  background-color: #d1d5db;
  opacity: 0.7;
  border-radius: 50%;
  margin: 0 4px;
}

.swiper-pagination-bullet-active {
  background-color: #FFDE21;
  opacity: 1;
}
</style>