const axios = require('axios');
const Parser = require('rss-parser');

const parser = new Parser({
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
  }
});

const processedLinks = new Set();
const CHECK_INTERVAL_MS = 60 * 1000; // 10 минут, можно менять
const BACKEND_URL = 'http://your-backend.com/api/news'; // Заменить на реальный URL

async function fetchNewsFromRSS() {
  try {
    const response = await axios.get('https://www.vedomosti.ru/rss/news', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
      }
    });

    const feed = await parser.parseString(response.data);
    const items = feed.items.slice(0, 3);

    console.log(`=== Проверка новостей: ${new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Berlin' })} ===`);

    const newItems = items.filter(item => !processedLinks.has(item.link));

    if (newItems.length === 0) {
      console.log('Нет новых новостей.\n');
      return;
    }

    for (const item of newItems) {
      const { title, link, pubDate } = item;

      // Берём текст из description или content или content:encoded
      const text = item.description || item.content || item['content:encoded'] || 'Текст отсутствует';

      console.log(`📰 ${title}`);
      console.log(`📅 Дата: ${pubDate}`);
      console.log(`🔗 Ссылка: ${link}`);
      console.log(`📄 Текст:\n${text}`);
      console.log('---\n');

      await sendToBackend({ title, link, pubDate, text });

      processedLinks.add(link);
    }
  } catch (err) {
    console.error('Ошибка при парсинге RSS:', err.message);
  }
}

async function sendToBackend(data) {
  try {
    const res = await axios.post(BACKEND_URL, data, {
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    console.log(`✅ Отправлено на бэкенд: ${res.status} ${res.statusText}`);
  } catch (err) {
    console.error('Ошибка отправки на бэкенд:', err.message);
  }
}

function startPolling() {
  console.log(`🚀 Запущено, проверка каждые ${CHECK_INTERVAL_MS / 1000 / 60} минут.`);
  fetchNewsFromRSS();
  setInterval(fetchNewsFromRSS, CHECK_INTERVAL_MS);
}

startPolling();
