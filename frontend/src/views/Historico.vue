<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-black text-gray-900 flex items-center gap-3">
          <ClockIcon class="h-8 w-8 text-indigo-600" />
          Histórico de Sondagens & Incidentes
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Registro completo de resposta da rota <code class="text-indigo-600 font-bold">/api/health</code> e estabilidade dos sistemas.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <Button variant="secondary" @click="fetchHistory" :disabled="loading">
          <template #icon>
            <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          </template>
          Atualizar Logs
        </Button>
      </div>
    </div>

    <!-- Tabela de Histórico -->
    <Card>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-base font-bold text-gray-800 flex items-center gap-2">
            <ListBulletIcon class="h-5 w-5 text-gray-600" />
            Últimas Sondagens Registradas
          </h2>
          <span class="text-xs text-gray-400 font-mono">Exibindo os {{ historyLogs.length }} registros mais recentes</span>
        </div>
      </template>

      <div v-if="loading" class="py-12 flex justify-center">
        <LoadingIndicator text="Buscando histórico de logs..." />
      </div>

      <div v-else-if="historyLogs.length === 0" class="text-center py-12 text-gray-500">
        Nenhum registro de histórico encontrado.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm text-gray-600">
          <thead class="bg-gray-50 text-xs uppercase font-bold text-gray-500 border-b">
            <tr>
              <th class="py-3.5 px-4">Aplicação</th>
              <th class="py-3.5 px-4">Data/Hora</th>
              <th class="py-3.5 px-4 text-center">Status HTTP</th>
              <th class="py-3.5 px-4 text-center">Latência (ms)</th>
              <th class="py-3.5 px-4">Status Banco DB</th>
              <th class="py-3.5 px-4 text-right">Versão</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr 
              v-for="log in historyLogs" 
              :key="log.id" 
              class="hover:bg-gray-50/80 transition-colors"
            >
              <td class="py-3.5 px-4 font-bold text-gray-900 flex items-center gap-2">
                <span 
                  class="h-2.5 w-2.5 rounded-full shrink-0" 
                  :class="log.is_online ? 'bg-emerald-500' : 'bg-rose-500'"
                ></span>
                {{ log.aplicacao_nome }}
              </td>
              <td class="py-3.5 px-4 text-xs font-mono text-gray-500">
                {{ formatDate(log.checked_at) }}
              </td>
              <td class="py-3.5 px-4 text-center">
                <span 
                  class="px-2.5 py-1 rounded-full text-xs font-bold font-mono"
                  :class="log.status_http === 200 ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
                >
                  {{ log.status_http || 'OFFLINE' }}
                </span>
              </td>
              <td class="py-3.5 px-4 text-center font-mono font-semibold" :class="getLatencyColor(log.latency_ms)">
                {{ log.latency_ms }} ms
              </td>
              <td class="py-3.5 px-4 text-xs">
                <span class="px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-mono">
                  {{ log.status_db }}
                </span>
              </td>
              <td class="py-3.5 px-4 text-right font-mono text-xs font-bold text-gray-700">
                {{ log.versao_semver || 'v1.0.0' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { ClockIcon, ArrowPathIcon, ListBulletIcon } from '@heroicons/vue/24/outline';

const loading = ref(false);
const historyLogs = ref<any[]>([]);

const fetchHistory = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/monitor/historico?limit=50');
    if (res.data) {
      historyLogs.value = res.data;
    }
  } catch (err) {
    console.error("Erro ao carregar histórico:", err);
  } finally {
    loading.value = false;
  }
};

const formatDate = (isoString: string) => {
  if (!isoString) return '-';
  try {
    const d = new Date(isoString);
    return d.toLocaleString('pt-BR');
  } catch {
    return isoString;
  }
};

const getLatencyColor = (ms: number) => {
  if (ms < 100) return 'text-emerald-600';
  if (ms < 300) return 'text-amber-600';
  return 'text-rose-600';
};

onMounted(() => {
  fetchHistory();
});
</script>
