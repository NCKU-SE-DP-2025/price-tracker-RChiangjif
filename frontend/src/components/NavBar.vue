<template>
  <nav class="navbar">
    <div class="title">
      <RouterLink to="/overview">價格追蹤小幫手</RouterLink>
    </div>

    <!-- hamburger icon -->
    <div class="hamburger" @click="toggleMenu">
      <span></span>
      <span></span>
      <span></span>
    </div>

    <!-- menu list -->
    <ul class="options" :class="{ open: isMenuOpen }">
      <li><RouterLink to="/overview">物價概覽</RouterLink></li>
      <li><RouterLink to="/trending">物價趨勢</RouterLink></li>
      <li><RouterLink to="/news">相關新聞</RouterLink></li>
      <li v-if="!isLoggedIn"><RouterLink to="/login">登入</RouterLink></li>
      <li v-else @click="logout">Hi, {{ getUserName }}! 登出</li>
    </ul>
  </nav>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'NavBar',
  data() {
    return {
      isMenuOpen: false
    };
  },
  computed: {
    isLoggedIn() {
      const userStore = useAuthStore();
      return userStore.isLoggedIn;
    },
    getUserName() {
      const userStore = useAuthStore();
      return userStore.getUserName;
    }
  },
  methods: {
    logout() {
      const userStore = useAuthStore();
      userStore.logout();
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    }
  }
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  background-color: #f3f3f3;
  padding: 1.5em;
  height: 4.5em;
  width: 100%;
  align-items: center;
  box-shadow: 0 0 5px #000000;
}

.navbar ul {
  list-style: none;
  display: flex;
  justify-content: space-around;
}

.title > a {
  font-size: 1.4em;
  font-weight: bold;
  color: #2c3e50 !important;
}

.navbar li {
  color: #575B5D;
  margin: 0 0.5em;
  font-size: 1.2em;
}

.navbar li:hover {
  cursor: pointer;
  font-weight: bold;
}

.navbar a {
  text-decoration: none;
  color: #575B5D;
}

/* hamburger icon */
.hamburger {
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 5px;
}
.hamburger span {
  width: 25px;
  height: 3px;
  background: #333;
  border-radius: 3px;
}

/* mobile styles */
@media (max-width: 768px) {
  .navbar {
    flex-wrap: wrap;
    height: auto;
  }

  .navbar ul {
    display: none;
    flex-direction: column;
    width: 100%;
    text-align: center;
    padding: 0;
  }

  .navbar ul.open {
    display: flex;
  }

  .hamburger {
    display: flex;
  }

  .navbar li {
    padding: 1em 0;
    border-top: 1px solid #ddd;
    width: 100%;
  }
}
</style>
