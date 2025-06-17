<template>
  <router-view />
</template>

<script setup>
// Удаляем импорт MainPage, так как он теперь управляется маршрутизатором
</script>

<style>
/* Сброс стилей для устранения белой обводки */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html, body {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  background-color: #000;
  font-family: "Nekst", sans-serif;
}
#app {
  width: 100%;
  height: 100%;
  font-family: "Nekst", sans-serif;
}
@import '@/style.css';
</style>