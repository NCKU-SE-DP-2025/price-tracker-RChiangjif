<template>
  <div class="wrapper">
    <h1>各類商品物價概覽</h1>
    <h3 v-if="!isLoading" class="subtitle">資料更新時間：{{ updateTime }}</h3>

    <div class="prices">
      <CategoryPrice
        class="category"
        v-for="category in categoryList"
        :key="category"
        :category="category"
        :isLoading="isLoading"
        :errorMessage="errorMessage"
        :priceData="getPriceData(category)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import CategoryPrice from '@/components/CategoryPrice.vue'
import Categories from '@/constants/categories'
import { usePricesStore } from '@/stores/prices'

const priceStore = usePricesStore()

const categoryList = Object.keys(Categories)

const isLoading = computed(() => priceStore.isLoading)
const errorMessage = computed(() => priceStore.errorMessage)
const updateTime = computed(() => priceStore.updatedTime)

function getPriceData(category) {
  return priceStore.getPricesByCategory(category)
}

onMounted(() => {
  priceStore.fetchPrices()
})
</script>

<style scoped>
.wrapper {
  padding: 3em 5em;
  background: #f3f3f3;
  min-height: calc(100vh - 4.5em);
  height: calc(100% - 4.5em);
  box-sizing: border-box;
}

.prices {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
}

.category {
  margin: 1em;
  flex-grow: 1;
}

.subtitle {
  font-weight: normal;
  margin-top: 0.5em;
}
</style>
