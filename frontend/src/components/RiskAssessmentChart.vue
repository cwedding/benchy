<template>
  <div class="risk-chart">
    <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export default defineComponent({
  name: 'RiskAssessmentChart',
  components: { Bar },
  props: {
    riskData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartData = computed(() => ({
      labels: ['Stability', 'Process', 'Purity', 'Developability'],
      datasets: [{
        label: 'Risk Score',
        data: [
          props.riskData.risk_categories?.stability?.length || 0,
          props.riskData.risk_categories?.process?.length || 0,
          props.riskData.risk_categories?.purity?.length || 0,
          props.riskData.risk_categories?.developability?.length || 0
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }]
    }))

    const chartOptions = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Risk Assessment Categories'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }

    return {
      chartData,
      chartOptions
    }
  }
})
</script>

<style scoped>
.risk-chart {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>
