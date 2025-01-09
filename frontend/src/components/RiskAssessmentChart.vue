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
          (props.riskData.risk_categories?.stability || []).reduce((sum, risk) => sum + parseFloat(risk.match(/\+(\d+\.\d+)/)?.[1] || '0'), 0),
          (props.riskData.risk_categories?.process || []).reduce((sum, risk) => sum + parseFloat(risk.match(/\+(\d+\.\d+)/)?.[1] || '0'), 0),
          (props.riskData.risk_categories?.purity || []).reduce((sum, risk) => sum + parseFloat(risk.match(/\+(\d+\.\d+)/)?.[1] || '0'), 0),
          (props.riskData.risk_categories?.developability || []).reduce((sum, risk) => sum + parseFloat(risk.match(/\+(\d+\.\d+)/)?.[1] || '0'), 0)
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
        },
        tooltip: {
          callbacks: {
            afterLabel: function(context: any) {
              const category = ['stability', 'process', 'purity', 'developability'][context.dataIndex];
              const risks = props.riskData.risk_categories?.[category] || [];
              return risks.map((risk: string) => '• ' + risk.split(':')[0]);
            }
          }
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
