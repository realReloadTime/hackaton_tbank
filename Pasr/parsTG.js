import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import input from "input";
import fetch from "node-fetch";
import { NewMessage } from "telegram/events/index.js";



const apiId = ;
const apiHash = "";
const stringSession = new StringSession("");

(async () => {
  console.log("Starting client...");
  const client = new TelegramClient(stringSession, apiId, apiHash, {
    connectionRetries: 5,
  });

  await client.start({
    phoneNumber: async () => await input.text("Введите номер телефона: "),
    password: async () => await input.text("Введите пароль 2FA (если есть): "),
    phoneCode: async () => await input.text("Введите код, присланный в Telegram: "),
    onError: (err) => console.log(err),
  });

  console.log("Client started!");
  console.log("String session:", client.session.save());

  // Получим объект канала по username
  const channel = await client.getEntity("rian_ru");

  // Подписка на новые сообщения канала
  client.addEventHandler(async (event) => {
    const message = event.message;
    if (message && message.peerId.channelId === channel.id) {
      const text = message.message;
      console.log("New message:", text);

      // Отправляем на backend
      await fetch("https://your-backend.example.com/news", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, date: message.date }),
      });
    }
  }, new NewMessage({}));

  console.log("Listening for new messages...");
})();
