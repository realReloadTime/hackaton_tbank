const axios = require('axios');
const cheerio = require('cheerio');
const Parser = require('rss-parser');
const parser = new Parser();

// Хранилище для уже обработанных ссылок
const processedLinks = new Set();

// Интервал проверки RSS-ленты (в миллисекундах, например, 5 минут)
const CHECK_INTERVAL_MS = 60 * 1000;

// URL бэкенда для отправки данных
const BACKEND_URL = 'http://localhost:8000/ai/new'; // http://your-backend.com/api/news Замените на реальный URL

async function fetchNewsFromRSS() {
    try {
        const feed = await parser.parseURL('https://rssexport.rbc.ru/rbcnews/news/30/full.rss');
        const items = feed.items.slice(0, 3); // Первые 3 новости из ленты

        console.log(`=== 🔹 Проверка новых новостей с РБК (RSS) ===\n`);

        // Фильтруем только новые новости
        const newItems = items.filter(item => !processedLinks.has(item.link));

        if (newItems.length === 0) {
            console.log('ℹ️ Новых новостей нет.\n');
            return;
        }

        for (let i = 0; i < newItems.length; i++) {
            const { title, link, pubDate } = newItems[i];
            const text = await fetchFullArticle(link);

            console.log(`📰 ${i + 1}) ${title}`);
            console.log(`📅 Дата: ${pubDate}`);
            console.log(`🔗 Ссылка: ${link}`);
            console.log(`📄 Текст:\n${text}`);
            console.log('---\n');

            // Отправляем данные на бэкенд
            await sendToBackend({ title, link, pubDate, text });

            // Добавляем ссылку в обработанные
            processedLinks.add(link);
        }
    } catch (err) {
        console.error('❌ Ошибка при парсинге RSS:', err.message);
    }
}

async function fetchFullArticle(url) {
    try {
        const res = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0'
            }
        });
        const $ = cheerio.load(res.data);

        const paragraphs = $('div.article__text p').map((_, el) => $(el).text()).get();
        return paragraphs.join('\n').trim() || '⚠️ Не удалось извлечь текст.';
    } catch (err) {
        return `❌ Ошибка при загрузке статьи: ${err.message}`;
    }
}

async function sendToBackend(data) {
    try {
        const response = await axios.post(BACKEND_URL, {
            title: data.title,
            link: data.link,
            pubDate: data.pubDate,
            text: data.text
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log(`✅ Данные отправлены на бэкенд: ${response.status} ${response.statusText}`);
    } catch (err) {
        console.error(`❌ Ошибка при отправке на бэкенд: ${err.message}`);
    }
}

// Запуск периодической проверки
function startPolling() {
    console.log(`🚀 Парсер запущен, проверка каждые ${CHECK_INTERVAL_MS / 1000 / 60} минут.`);
    fetchNewsFromRSS(); // Первая проверка сразу
    setInterval(fetchNewsFromRSS, CHECK_INTERVAL_MS); // Периодическая проверка
}

// Запуск
startPolling();