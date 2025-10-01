<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const chart = ref(null);
const chartCanvas = ref(null);

function generateLabels(startDate, endDate, count) {
  const start = new Date(startDate);
  const labels = [];
  for (let i = 0; i < count; i++) {
    const monthDate = new Date(start.getFullYear(), start.getMonth() + i, 1);
    labels.push(`${monthDate.getFullYear()}.${monthDate.getMonth() + 1}`.padStart(2, '0'));
  }
  return labels;
}

function createChart(data) {
  if (chart.value) {
    chart.value.destroy();
  }

  const ctx = chartCanvas.value.getContext('2d');
  let prices = data.統計值.split(',').map(price => parseInt(price, 10));
  let labels = generateLabels(data.時間起點, data.時間終點, prices.length);

  const firstNonZeroIndex = prices.findIndex(price => price !== 0);
  if (firstNonZeroIndex > 0) {
    prices = prices.slice(firstNonZeroIndex);
    labels = labels.slice(firstNonZeroIndex);
  }

  let lastValidPrice = prices[0];
  const annotations = [];

  prices = prices.map((price, index) => {
    if (price === 0) {
      annotations.push({ index, price: lastValidPrice });
      return lastValidPrice;
    }
    lastValidPrice = price;
    return price;
  });

  chart.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: data.產品名稱,
          data: prices,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
          pointRadius: prices.map((_, index) =>
            annotations.some(a => a.index === index) ? 5 : 3
          ),
          pointStyle: prices.map((_, index) =>
            annotations.some(a => a.index === index) ? 'crossRot' : 'circle'
          )
        }
      ]
    },
    options: {
      scales: {
        y: {
          beginAtZero: false
        }
      },
      animation: {
        duration: 300
      },
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

onMounted(() => {
  createChart(props.data);
});

watch(() => props.data, (newData, oldData) => {
  if (newData !== oldData) {
    createChart(newData);
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
  margin: auto;
  height: 30vh;
  width: 100wh;
}
</style>
