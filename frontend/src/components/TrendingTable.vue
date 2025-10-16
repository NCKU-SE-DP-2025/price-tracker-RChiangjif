<template>
  <div class="trending-table">
    <table>
      <thead>
        <tr>
          <th rowspan="2">年份</th>
          <th v-for="month in months" :key="month">{{ month }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="year in years" :key="year">
          <tr>
            <td>{{ year }}</td>
            <template
              v-for="(value, monthIndex) in getYearData(year)"
              :key="year + '-month-' + monthIndex"
            >
              <td>{{ valueDisplay(value) }}</td>
            </template>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const yearData = ref({});

const months = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const years = computed(() => {
  const startYear = new Date(props.data.時間起點).getFullYear();
  const endYear = new Date(props.data.時間終點).getFullYear();
  const result = [];
  for (let year = startYear; year <= endYear; year++) {
    result.push(year);
  }
  return result;
});

function processInitData() {
  const stats = props.data.統計值.split(',');
  const startDate = new Date(props.data.時間起點);
  const endDate = new Date(props.data.時間終點);
  const startYear = startDate.getFullYear();
  const endYear = endDate.getFullYear();
  const startMonth = startDate.getMonth() + 1;
  const endMonth = endDate.getMonth() + 1;

  const dataMap = {};

  let dataIndex = 0;

  for (let year = startYear; year <= endYear; year++) {
    const yearPrices = [];
    for (let month = 1; month <= 12; month++) {
      if (
        (year === startYear && month < startMonth) ||
        (year === endYear && month > endMonth)
      ) {
        yearPrices.push('0');
      } else {
        yearPrices.push(stats[dataIndex] || '0');
        dataIndex++;
      }
    }
    dataMap[year] = yearPrices;
  }

  yearData.value = dataMap;
}

function getYearData(year) {
  return yearData.value[year] || [];
}

function valueDisplay(value) {
  return value === '0' ? '-' : value;
}

watch(
  () => props.data,
  () => {
    processInitData();
  },
  { immediate: true, deep: true }
);

onMounted(() => {
  processInitData();
});
</script>

<style scoped>
.trending-table {
  margin-top: 2em;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ccc;
  padding: 0.5em;
  text-align: center;
}
</style>
