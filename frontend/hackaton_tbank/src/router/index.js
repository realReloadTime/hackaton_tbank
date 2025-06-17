import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../components/MainPage.vue';
import NewsFeed from '../components/NewsFeed.vue';
import NewsDetail from '../components/NewsDetail.vue';
import TickerPreferences from '../components/TickerPreferences.vue'; // Импортируем новый компонент

const routes = [
  { path: '/', component: MainPage },
  { path: '/news-feed', component: NewsFeed },
  { path: '/news/:id', component: NewsDetail },
  { path: '/ticker-preferences', component: TickerPreferences }, // Новый маршрут
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;