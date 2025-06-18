<template>
  <div class="ticker-preferences-container">
    <div class="header">
      <button class="back-button" @click="goBack">←</button>
      <BurgerMenu />
    </div>
    <div class="section">
      <h2 class="section-title">Выберите тикеры</h2>
      <input v-model="searchQuery" type="text" placeholder="Поиск" class="search-input" />
      <div class="ticker-list">
        <button
          v-for="ticker in filteredTickers"
          :key="ticker.ticker_id"
          class="ticker-button"
          @click="addTicker(ticker.ticker_id)"
          :disabled="selectedTickers.some(t => t.ticker_id === ticker.ticker_id)"
        >
          {{ ticker.name }}
        </button>
      </div>
    </div>
    <div class="section">
      <h2 class="section-title">Добавьте свой тикер</h2>
      <div class="add-ticker-row">
        <div class="input-group">
          <input v-model="newTickerName" type="text" placeholder="Тикер" class="input-field" @input="toUpperCase" />
          <input v-model="newTickerCompany" type="text" placeholder="Компания" class="input-field" />
          <select v-model="selectedRegionId" class="input-field">
            <option v-for="region in regions" :key="region.region_id" :value="region.region_id">
              {{ region.name }}
            </option>
          </select>
        </div>
        <button class="add-button" @click="addCustomTicker" :disabled="!isValidNewTicker">
          <span class="plus-icon">+</span>
        </button>
      </div>
    </div>
    <div class="section">
      <h2 class="section-title">Ваши тикеры</h2>
      <div class="selected-tickers">
        <div v-for="ticker in selectedTickers" :key="ticker.ticker_id" class="selected-ticker">
          <span>{{ ticker.name }}</span>
          <button class="remove-button" @click="removeTicker(ticker.ticker_id)">×</button>
        </div>
      </div>
    </div>
    <button class="save-button" @click="savePreferences" :disabled="selectedTickers.length === 0">
      Сохранить
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import BurgerMenu from './BurgerMenu.vue';

const router = useRouter();
const searchQuery = ref('');
const availableTickers = ref([]);
const selectedTickers = ref([]);
const newTickerName = ref('');
const newTickerCompany = ref('');
const selectedRegionId = ref(null);
const regions = ref([]);
const skip = ref(0);
const limit = ref(5);
const isLoading = ref(false);
const userName = ref(''); // Реактивная переменная для хранения username

const filteredTickers = computed(() =>
  availableTickers.value.filter(ticker =>
    ticker.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
);

const isValidNewTicker = computed(() => {
  return newTickerName.value.trim() && newTickerCompany.value.trim() && selectedRegionId.value;
});

// Функция для преобразования текста в верхний регистр
const toUpperCase = (event) => {
  newTickerName.value = event.target.value.toUpperCase();
};

// Функция для получения данных из Telegram Web App
const initTelegramWebApp = () => {
  if (window.Telegram && window.Telegram.WebApp) {
    const telegramData = window.Telegram.WebApp.initDataUnsafe;
    if (telegramData && telegramData.user) {
      userName.value = telegramData.user.username || 'User';
    } else {
      userName.value = 'User'; // Значение по умолчанию, если username отсутствует
    }
  } else {
    userName.value = 'User'; // Значение по умолчанию для тестирования вне Telegram
    console.warn('Telegram WebApp не обнаружен. Используется значение по умолчанию.');
  }
};

const loadRegions = async () => {
  try {
    const response = await axios.get('https://api2.academus-pobeda.ru/regions/');
    regions.value = response.data;
    if (regions.value.length > 0) {
      selectedRegionId.value = regions.value[0].region_id;
    }
  } catch (error) {
    console.error('Ошибка при загрузке регионов:', error);
  }
};

const loadTickers = async () => {
  if (isLoading.value) return;
  isLoading.value = true;
  try {
    const response = await axios.get('http://api2.academus-pobeda.ru/tickers/', {
      params: { skip: skip.value, limit: limit.value }
    });
    availableTickers.value = skip.value === 0 ? response.data : [...availableTickers.value, ...response.data];
    skip.value += limit.value;
  } catch (error) {
    console.error('Ошибка при загрузке тикеров:', error);
  } finally {
    isLoading.value = false;
  }
};

const loadSelectedTickers = async () => {
  try {
    const response = await axios.get(`http://api2.academus-pobeda.ru/users/${userName.value}/tickers`);
    selectedTickers.value = response.data.tickers || [];
  } catch (error) {
    console.error('Ошибка при загрузке выбранных тикеров:', error);
  }
};

const addTicker = async (tickerId) => {
  try {
    await axios.post('http://api2.academus-pobeda.ru/users/preferences/add', {
      username: userName.value,
      ticker_id: tickerId
    });
    const ticker = availableTickers.value.find(t => t.ticker_id === tickerId);
    if (ticker && !selectedTickers.value.some(t => t.ticker_id === tickerId)) {
      selectedTickers.value.push(ticker);
    }
  } catch (error) {
    console.error('Ошибка при добавлении тикера:', error);
  }
};

const addCustomTicker = async () => {
  if (!isValidNewTicker.value) return;
  let tickerNameToSend = newTickerName.value;
  // Автоматическое добавление "$" в начало, если его нет
  if (!tickerNameToSend.startsWith('$')) {
    tickerNameToSend = '$' + tickerNameToSend;
  }
  try {
    const response = await axios.post('http://api2.academus-pobeda.ru/tickers', {
      name: tickerNameToSend,
      company: newTickerCompany.value,
      region_ids: [selectedRegionId.value]
    });
    const newTicker = {
      ticker_id: response.data.ticker_id || Date.now(),
      name: tickerNameToSend,
      company: newTickerCompany.value,
      regions: regions.value.filter(r => r.region_id === selectedRegionId.value)
    };
    selectedTickers.value.push(newTicker);
    newTickerName.value = '';
    newTickerCompany.value = '';
    selectedRegionId.value = regions.value[0]?.region_id;
  } catch (error) {
    console.error('Ошибка при добавлении пользовательского тикера:', error);
  }
};

const removeTicker = (tickerId) => {
  selectedTickers.value = selectedTickers.value.filter(t => t.ticker_id !== tickerId);
};

const savePreferences = async () => {
  try {
    await axios.post(`http://localhost:8000/users/${userName.value}/tickers`, {
      tickers: selectedTickers.value.map(t => ({ ticker_id: t.ticker_id }))
    });
    console.log('Предпочтения сохранены');
  } catch (error) {
    console.error('Ошибка при сохранении предпочтений:', error);
  }
};

const goBack = () => {
  router.push('/news-feed');
};

const handleScroll = () => {
  const container = document.querySelector('.ticker-list');
  if (!container) return;
  const { scrollTop, clientHeight, scrollHeight } = container;
  if (scrollTop + clientHeight >= scrollHeight - 10 && !isLoading.value) {
    loadTickers();
  }
};

onMounted(async () => {
  initTelegramWebApp();
  await loadRegions();
  await loadTickers();
  await loadSelectedTickers();
  const container = document.querySelector('.ticker-list');
  if (container) {
    container.addEventListener('scroll', handleScroll);
  }
});
</script>

<style scoped>
.ticker-preferences-container {
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

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.search-input {
  width: 100%;
  padding: 10px;
  background-color: #1a1a1a;
  border: none;
  border-radius: 8px;
  color: #fff;
  margin-bottom: 10px;
}

.ticker-list {
  max-height: 150px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ticker-button {
  background-color: #1a1a1a;
  border: none;
  padding: 8px 16px;
  border-radius: 16px;
  color: #fff;
  cursor: pointer;
}

.ticker-button:disabled {
  background-color: #333;
  cursor: not-allowed;
}

.add-ticker-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.input-group {
  flex: 0 0 60%; /* 60% ширины */
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-field {
  width: 100%;
  padding: 10px;
  background-color: #1a1a1a;
  border: none;
  border-radius: 8px;
  color: #fff;
  margin: 0;
}

.add-button {
  flex: 0 0 auto; /* Фиксированная ширина кнопки */
  background-color: #FFDE21;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: #000;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0;
}

.plus-icon {
  margin: 0;
}

.selected-tickers {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.selected-ticker {
  background-color: #FFDE21;
  padding: 8px 16px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  color: #000;
}

.remove-button {
  background: none;
  border: none;
  color: #000;
  font-size: 18px;
  margin-left: 10px;
  cursor: pointer;
}

.save-button {
  width: 100%;
  padding: 12px;
  background-color: #FFDE21;
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.save-button:disabled {
  background-color: #333;
  cursor: not-allowed;
}
</style>