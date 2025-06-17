<template>
  <div class="burger-menu-container">
    <button class="menu-toggle" @click="toggleMenu" :class="{ 'open': isOpen }">
      <span class="bar"></span>
      <span class="bar"></span>
      <span class="bar"></span>
    </button>
    <div v-if="isOpen" class="menu-overlay" @click="toggleMenu"></div>
    <transition name="slide">
      <div v-if="isOpen" class="menu-content">
        <button @click="goToHome" class="menu-item">Главная</button>
        <button @click="goToNewsFeed" class="menu-item">Лента</button>
        <button @click="goToSettings" class="menu-item">Настройки</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isOpen = ref(false);

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const goToHome = () => {
  router.push('/');
  isOpen.value = false;
};

const goToNewsFeed = () => {
  router.push('/news-feed');
  isOpen.value = false;
};

const goToSettings = () => {
  router.push('/ticker-preferences');
  isOpen.value = false;
};
</script>

<style scoped>
.burger-menu-container {
  position: relative;
}

.menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar {
  width: 24px;
  height: 3px;
  background-color: #fff;
  transition: all 0.3s ease;
}

.menu-toggle.open .bar:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.menu-toggle.open .bar:nth-child(2) {
  opacity: 0;
}

.menu-toggle.open .bar:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.menu-content {
  position: fixed;
  top: 0;
  right: 0;
  width: 250px;
  height: 100%;
  background-color: #1a1a1a;
  z-index: 1002;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.menu-item {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  padding: 10px;
}

.menu-item:hover {
  color: #FFDE21;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>