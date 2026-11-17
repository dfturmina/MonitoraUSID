<template>
  <div class="space-y-6">
    <!-- Header / Auto-Refresh Seletor -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-black text-slate-900 flex items-center gap-3">
          <ChartBarIcon class="h-8 w-8 text-emerald-600" />
          Dashboard de Monitoramento
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Acompanhamento em tempo real da saúde das aplicações, usuários conectados, bancos de dados e infraestrutura Zabbix.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Seletor de Auto-Refresh -->
        <div class="flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700">
          <ClockIcon class="h-4 w-4 text-slate-400" />
          <span>Auto-Refresh:</span>
          <select 
            v-model="refreshIntervalSeconds" 
            @change="updateRefreshTimer"
            class="bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option :value="0">Desativado</option>
            <option :value="5">5s</option>
            <option :value="10">10s</option>
            <option :value="30">30s</option>
            <option :value="60">1 min</option>
            <option :value="300">5 min</option>
          </select>
        </div>

        <Button variant="secondary" @click="fetchDashboardData" :disabled="loading">
          <template #icon>
            <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          </template>
          Atualizar Agora
        </Button>
        <Button variant="primary" @click="openAddModal">
          <template #icon>
            <PlusIcon class="h-4 w-4" />
          </template>
          Nova Aplicação
        </Button>
      </div>
    </div>

    <!-- Cards de Métricas Principais -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <!-- Card Total -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Total de Sistemas</p>
          <p class="text-3xl font-black text-slate-900 mt-1">{{ summary.total_apps }}</p>
        </div>
        <div class="p-3 bg-blue-50 text-blue-600 rounded-xl">
          <ServerIcon class="h-7 w-7" />
        </div>
      </div>

      <!-- Card Online -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-emerald-500">Saudáveis / Online</p>
          <p class="text-3xl font-black text-emerald-600 mt-1">{{ summary.online_apps }}</p>
        </div>
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
          <CheckCircleIcon class="h-7 w-7" />
        </div>
      </div>

      <!-- Card Offline -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-rose-400">Indisponíveis</p>
          <p class="text-3xl font-black text-rose-600 mt-1">{{ summary.offline_apps }}</p>
        </div>
        <div class="p-3 bg-rose-50 text-rose-600 rounded-xl">
          <ExclamationTriangleIcon class="h-7 w-7" />
        </div>
      </div>

      <!-- Card Alertas Zabbix -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-amber-500">Alertas Zabbix</p>
          <p class="text-3xl font-black text-amber-600 mt-1">{{ summary.active_problems_count }}</p>
        </div>
        <div class="p-3 bg-amber-50 text-amber-600 rounded-xl">
          <BellAlertIcon class="h-7 w-7" />
        </div>
      </div>
    </div>

    <!-- Grid de Sistemas Monitorados -->
    <Card>
      <template #header>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
            <CpuChipIcon class="h-5 w-5 text-indigo-600" />
            Sistemas do SETISD
          </h2>

          <div class="flex items-center space-x-3">
            <button 
              @click="toggleExpandAll" 
              class="text-xs font-semibold px-2.5 py-1 rounded-lg border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 transition-colors flex items-center gap-1"
            >
              <ChevronUpIcon v-if="allExpanded" class="h-3.5 w-3.5" />
              <ChevronDownIcon v-else class="h-3.5 w-3.5" />
              {{ allExpanded ? 'Recolher Todos' : 'Expandir Todos' }}
            </button>
            <span class="text-xs font-medium text-slate-400">Tempo Médio de Resposta: {{ summary.avg_latency_ms }}ms</span>
          </div>
        </div>
      </template>

      <div v-if="loading && applications.length === 0" class="py-12 flex justify-center">
        <LoadingIndicator text="Carregando métricas dos sistemas..." />
      </div>

      <div v-else-if="applications.length === 0" class="text-center py-12 text-slate-500">
        Nenhuma aplicação cadastrada para monitoramento.
      </div>

      <div 
        v-else 
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <div 
          v-for="app in applications" 
          :key="app.aplicacao_id || app.id"
          class="p-4 rounded-xl border transition-all duration-200 hover:shadow-md flex flex-col justify-between"
          :class="getCardBorderClass(app)"
        >
          <div>
            <!-- Cabeçalho do Card (Compacto com Chevron Expansível que altera TODOS) -->
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center space-x-2 truncate">
                <span 
                  class="h-2.5 w-2.5 rounded-full shrink-0 animate-pulse"
                  :class="app.is_online ? 'bg-emerald-500' : 'bg-rose-500'"
                ></span>
                <h3 class="font-bold text-slate-900 text-sm truncate" :title="app.nome">
                  {{ app.nome }}
                </h3>
              </div>

              <div class="flex items-center space-x-1">
                <span 
                  class="px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider"
                  :class="app.is_online ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
                >
                  {{ app.is_online ? 'Online' : 'Offline' }}
                </span>
                
                <button 
                  @click.stop="toggleExpandAll"
                  class="p-1 text-slate-400 hover:text-slate-700 transition-colors"
                  :title="allExpanded ? 'Recolher todos os cards' : 'Expandir todos os cards'"
                >
                  <ChevronUpIcon v-if="allExpanded" class="h-4 w-4" />
                  <ChevronDownIcon v-else class="h-4 w-4" />
                </button>
              </div>
            </div>

            <!-- Resumo Rápido (Exibido Sempre) -->
            <div class="flex items-center justify-between text-xs text-slate-500 py-1 mb-1 font-mono">
              <span class="truncate text-[11px] text-slate-400" :title="app.full_url">{{ app.full_url }}</span>
              <span class="font-bold shrink-0 ml-2 text-[11px]" :class="app.latency_ms > 500 ? 'text-amber-600' : 'text-slate-700'">
                {{ app.latency_ms }} ms
              </span>
            </div>

            <!-- Mini resumo em Card Recolhido -->
            <div v-if="!allExpanded" class="flex flex-wrap items-center gap-1.5 mt-1 pt-1.5 border-t border-slate-100 text-[10px]">
              <span class="font-mono px-1.5 py-0.5 rounded" :class="getMetricBadgeClass(app.zabbix?.cpu_usage || 0)">
                CPU: {{ app.zabbix?.cpu_usage || 0 }}%
              </span>
              <span class="font-mono px-1.5 py-0.5 rounded" :class="getMetricBadgeClass(app.zabbix?.memory_usage || 0)">
                RAM: {{ app.zabbix?.memory_usage || 0 }}% ({{ app.zabbix?.memory_used_gb || 0 }}/{{ app.zabbix?.memory_total_gb || 0 }}GB)
              </span>
              <span v-if="app.monitora_usuarios_ativos" class="font-mono px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold">
                {{ app.active_users_origin === 'api_users' ? `${app.active_users || 0} Usuário(s)` : (app.possui_rota_health ? `${app.active_users || 0} Usuário(s)` : `${app.active_users || app.zabbix?.active_connections || 0} Conexões TCP`) }}
              </span>
              <span class="font-mono px-1.5 py-0.5 rounded" :class="getMetricBadgeClass(app.zabbix?.disk_usage || 0)">
                Disco: {{ app.zabbix?.disk_usage || 0 }}% ({{ app.zabbix?.disk_used_gb || 0 }}/{{ app.zabbix?.disk_total_gb || 0 }}GB)
              </span>
              <span 
                v-if="app.databases && Object.keys(app.databases).length > 0" 
                class="font-mono px-1.5 py-0.5 rounded flex items-center gap-1"
                :class="getConnectedDbCount(app.databases) === Object.keys(app.databases).length ? 'bg-emerald-50 text-emerald-700 font-bold' : 'bg-rose-100 text-rose-800 font-bold'"
                :title="`${getConnectedDbCount(app.databases)} de ${Object.keys(app.databases).length} banco(s) conectados`"
              >
                <span 
                  class="h-1.5 w-1.5 rounded-full" 
                  :class="getConnectedDbCount(app.databases) === Object.keys(app.databases).length ? 'bg-emerald-500' : 'bg-rose-500'"
                ></span>
                DBs: {{ getConnectedDbCount(app.databases) }}/{{ Object.keys(app.databases).length }}
              </span>
            </div>

            <!-- Conteúdo Detalhado (Recolhível / Expansível) -->
            <div v-if="allExpanded" class="mt-2 pt-2 border-t border-slate-100 space-y-2.5">
              <!-- Métricas Infraestrutura (Zabbix ou SSH) -->
              <div v-if="app.zabbix" class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
                <div class="flex items-center justify-between text-[11px] font-bold text-slate-700">
                  <span class="truncate" :title="app.zabbix?.name || app.zabbix_host_id || app.ssh_host">
                    {{ app.zabbix?.source === 'SSH' ? 'SSH' : 'Zabbix' }}: {{ app.zabbix?.name || app.zabbix_host_id || app.ssh_host }}
                  </span>
                  <span v-if="app.monitora_usuarios_ativos" class="text-[10px] text-indigo-600 font-mono flex items-center gap-1 shrink-0 ml-1">
                    <UsersIcon class="h-3 w-3" />
                    {{ app.active_users_origin === 'api_users' ? `${app.active_users || 0} Usuário(s) Ativo(s)` : (app.possui_rota_health ? `${app.active_users || 0} Usuário(s) Ativo(s)` : `${app.active_users || app.zabbix?.active_connections || 0} Conexões TCP Ativas`) }}
                  </span>
                </div>
                
                <!-- CPU Bar -->
                <div>
                  <div class="flex justify-between text-[10px] font-semibold text-slate-600 mb-0.5">
                    <span>CPU</span>
                    <span class="font-mono" :class="getMetricTextColor(app.zabbix?.cpu_usage || 0)">{{ app.zabbix?.cpu_usage || 0 }}%</span>
                  </div>
                  <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all duration-500" 
                      :class="getMetricBarColor(app.zabbix?.cpu_usage || 0)"
                      :style="{ width: `${app.zabbix?.cpu_usage || 0}%` }"
                    ></div>
                  </div>
                </div>

                <!-- RAM Bar com Porcentagem + GB Absolutos -->
                <div>
                  <div class="flex justify-between text-[10px] font-semibold text-slate-600 mb-0.5">
                    <span>RAM</span>
                    <span class="font-mono" :class="getMetricTextColor(app.zabbix?.memory_usage || 0)">
                      {{ app.zabbix?.memory_usage || 0 }}% ({{ app.zabbix?.memory_used_gb || 0 }}GB / {{ app.zabbix?.memory_total_gb || 0 }}GB)
                    </span>
                  </div>
                  <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all duration-500" 
                      :class="getMetricBarColor(app.zabbix?.memory_usage || 0)"
                      :style="{ width: `${app.zabbix?.memory_usage || 0}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Disco Bar com Porcentagem + GB Absolutos -->
                <div>
                  <div class="flex justify-between text-[10px] font-semibold text-slate-600 mb-0.5">
                    <span>Disco</span>
                    <span class="font-mono" :class="getMetricTextColor(app.zabbix?.disk_usage || 0)">
                      {{ app.zabbix?.disk_usage || 0 }}% ({{ app.zabbix?.disk_used_gb || 0 }}GB / {{ app.zabbix?.disk_total_gb || 0 }}GB)
                    </span>
                  </div>
                  <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all duration-500" 
                      :class="getMetricBarColor(app.zabbix?.disk_usage || 0)"
                      :style="{ width: `${app.zabbix?.disk_usage || 0}%` }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Conexões de Banco de Dados (Resumidas / Expansíveis para a lista de bancos) -->
              <div class="space-y-1.5 text-xs">
                <div class="flex items-center justify-between">
                  <div class="font-bold text-[10px] text-slate-400 uppercase tracking-wider">
                    Conexões DB
                  </div>
                  <!-- Botão de Expandir/Recolher lista individual quando houver mais de 3 bancos -->
                  <button 
                    v-if="Object.keys(app.databases || {}).length > 3" 
                    @click="toggleDbExpand(app.aplicacao_id || app.id)"
                    class="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-0.5"
                  >
                    <span>{{ isDbExpanded(app.aplicacao_id || app.id) ? 'Ocultar Detalhes' : `Ver Lista (${Object.keys(app.databases || {}).length})` }}</span>
                    <ChevronUpIcon v-if="isDbExpanded(app.aplicacao_id || app.id)" class="h-3 w-3" />
                    <ChevronDownIcon v-else class="h-3 w-3" />
                  </button>
                </div>

                <!-- Resumo Sintético quando houver mais de 3 bancos (ex: Metabase) e não estiver expandido -->
                <div 
                  v-if="Object.keys(app.databases || {}).length > 3 && !isDbExpanded(app.aplicacao_id || app.id)"
                  class="p-2 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between"
                >
                  <div class="flex items-center space-x-2">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0"></span>
                    <span class="text-xs font-bold text-emerald-900">
                      {{ getConnectedDbCount(app.databases) }} / {{ Object.keys(app.databases || {}).length }} Bancos Conectados
                    </span>
                  </div>
                </div>

                <!-- Grid Detalhado de Bancos de Dados (Exibido para até 3 bancos ou quando expandido) -->
                <div 
                  v-else 
                  class="grid grid-cols-2 gap-1.5 max-h-48 overflow-y-auto pr-1"
                >
                  <div 
                    v-for="(dbState, dbName) in (app.databases || { 'Banco Aplicação': 'connected' })" 
                    :key="dbName"
                    class="p-1.5 bg-slate-50 rounded-md border border-slate-100 flex flex-col justify-between"
                  >
                    <span class="text-[10px] text-slate-700 font-bold truncate" :title="String(dbName)">{{ formatDbName(String(dbName)) }}</span>
                    <span 
                      class="font-bold text-[10px] capitalize flex items-center gap-1 mt-0.5"
                      :class="String(dbState).includes('connected') || String(dbState).toLowerCase().includes('ok') ? 'text-emerald-600' : (String(dbState).includes('not_in_route') ? 'text-amber-600' : 'text-slate-400')"
                    >
                      <span 
                        class="h-1.5 w-1.5 rounded-full shrink-0"
                        :class="String(dbState).includes('connected') || String(dbState).toLowerCase().includes('ok') ? 'bg-emerald-500' : (String(dbState).includes('not_in_route') ? 'bg-amber-500' : 'bg-slate-300')"
                      ></span>
                      {{ String(dbState).toLowerCase() === 'rede ok' ? 'Rede OK' : (String(dbState).includes('connected') ? 'Conectado' : (String(dbState).includes('not_in_route') ? 'Não informado na Rota' : (String(dbState).includes('disabled') ? 'Desativado' : String(dbState)))) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rodapé de Ações do Card -->
          <div class="flex items-center justify-between pt-2 border-t border-slate-100 mt-2 text-xs">
            <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
              {{ app.criticidade }}
            </span>
            <div class="flex items-center space-x-1">
              <button 
                @click="openEditModal(app)" 
                class="p-1 text-slate-400 hover:text-indigo-600 transition-colors"
                title="Editar Aplicação"
              >
                <PencilSquareIcon class="h-4 w-4" />
              </button>
              <button 
                @click="handleDeleteApp(app.aplicacao_id || app.id)" 
                class="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                title="Excluir Aplicação"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <!-- Incidentes Zabbix -->
    <Card>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
            <ShieldExclamationIcon class="h-5 w-5 text-amber-600" />
            Alertas e Triggers Ativos no Zabbix
          </h2>
          <span class="text-xs text-slate-400">Eventos de Infraestrutura</span>
        </div>
      </template>

      <div v-if="zabbixProblems.length === 0" class="text-center py-8 text-emerald-600 font-medium">
        ✓ Nenhum problema ativo detectado pela infraestrutura do Zabbix.
      </div>

      <div v-else class="space-y-3">
        <div 
          v-for="prob in zabbixProblems" 
          :key="prob.id"
          class="p-4 rounded-xl border flex items-center justify-between gap-4"
          :class="getSeverityClass(prob.severity)"
        >
          <div class="flex items-center gap-3">
            <ExclamationCircleIcon class="h-6 w-6 shrink-0" />
            <div>
              <p class="font-bold text-sm text-slate-900">{{ prob.name }}</p>
              <p class="text-xs text-slate-500">ID Evento Zabbix: #{{ prob.id }}</p>
            </div>
          </div>

          <span class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wide">
            {{ prob.severity }}
          </span>
        </div>
      </div>
    </Card>

    <!-- Modal Adicionar / Editar Aplicação -->
    <Modal :show="showModal" @close="showModal = false">
      <template #header>{{ editingAppId ? 'Editar Aplicação' : 'Cadastrar Nova Aplicação' }}</template>
      <form @submit.prevent="handleSaveApp" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700">Nome do Sistema</label>
          <input v-model="appForm.nome" required type="text" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border" placeholder="Ex: Sistema de Faturamento SUS" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700">Tipo de Checagem</label>
            <select v-model="appForm.tipo_checagem" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border bg-white">
              <option value="HTTP">HTTP / HTTPS</option>
              <option value="TCP">TCP Direto (Sem HTTP)</option>
              <option value="ZABBIX">Somente Zabbix</option>
            </select>
          </div>
          <div v-if="appForm.tipo_checagem === 'TCP'">
            <label class="block text-sm font-medium text-slate-700">Porta TCP</label>
            <input v-model.number="appForm.porta_tcp" type="number" min="1" max="65535" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border" placeholder="Ex: 10050" />
          </div>
          <div v-else>
            <label class="block text-sm font-medium text-slate-700">Host SSH (Opcional)</label>
            <input v-model="appForm.ssh_host" type="text" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border" placeholder="Ex: wokibi ou root@10.34.0.219" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700">{{ appForm.tipo_checagem === 'TCP' ? 'IP / Host' : 'URL Base' }}</label>
          <input v-model="appForm.url_base" required :type="appForm.tipo_checagem === 'TCP' ? 'text' : 'url'" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border" :placeholder="appForm.tipo_checagem === 'TCP' ? '10.34.0.70' : 'http://10.34.0.X:8000'" />
        </div>

        <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-200 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <label class="text-xs font-bold text-emerald-900 block">Sistema baseado no Framework Padrão SETISD?</label>
              <span class="text-[11px] text-emerald-700">Utiliza rota padronizada /api/health e métricas corporativas</span>
            </div>
            <input v-model="appForm.usar_framework_setisd" @change="onFrameworkToggle" type="checkbox" class="h-4 w-4 text-emerald-600 focus:ring-emerald-500 rounded border-emerald-300" />
          </div>

          <!-- Pergunta de conexão ao AGHU para sistemas do Framework -->
          <div v-if="appForm.usar_framework_setisd" class="pt-2 border-t border-emerald-200 flex items-center justify-between">
            <label class="text-xs font-bold text-emerald-900">Conecta ao Banco de Dados do AGHU?</label>
            <input v-model="appForm.possui_banco_aghu" type="checkbox" class="h-4 w-4 text-emerald-600 focus:ring-emerald-500 rounded border-emerald-300" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700">Host ID no Zabbix (Servidor Zabbix 10.34.0.127)</label>
          <input v-model="appForm.zabbix_host_id" type="text" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border" placeholder="Ex: 11309 ou 11361" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700">Criticidade</label>
          <select v-model="appForm.criticidade" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border">
            <option value="ALTA">Alta</option>
            <option value="MEDIA">Média</option>
            <option value="BAIXA">Baixa</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700">Provedor / Integração Externa (Opcional)</label>
          <select v-model="appForm.integracao_id" class="mt-1 block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-2.5 border bg-white">
            <option :value="null">Nenhuma (Poller Padrão / Framework)</option>
            <option v-for="integ in integracoesDisponiveis" :key="integ.id" :value="integ.id">
              {{ integ.nome }} ({{ integ.provedor }})
            </option>
          </select>
          <span class="text-[11px] text-slate-400 mt-1 block">Permite consultar métricas e bancos de dados automaticamente via API REST (ex: Metabase).</span>
        </div>

        <!-- Seção de Bancos de Dados Adicionais Dinâmicos (Ocultada conforme solicitação) -->
        <!-- 
        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <label class="text-xs font-bold text-slate-800 block">Conexões com Bancos de Dados Adicionais (TCP)</label>
              <span class="text-[11px] text-slate-500">Sonda diretamente a conectividade via IP e Porta</span>
            </div>
            <button type="button" @click="addBanco" class="text-xs font-bold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 bg-emerald-50 px-2 py-1 rounded border border-emerald-200">
              <PlusIcon class="h-3.5 w-3.5" /> Adicionar Banco
            </button>
          </div>

          <div v-if="appForm.bancos_adicionais.length === 0" class="text-[11px] text-slate-400 italic">
            Nenhum banco de dados adicional configurado.
          </div>

          <div v-for="(db, idx) in appForm.bancos_adicionais" :key="idx" class="flex items-center gap-2 bg-white p-2 rounded-lg border border-slate-200 shadow-sm">
            <input v-model="db.nome" type="text" placeholder="Nome (Ex: AGHU BI)" class="text-xs p-1.5 border border-slate-300 rounded w-1/3 focus:ring-emerald-500" />
            <input v-model="db.host" type="text" placeholder="IP/Host (Ex: 10.34.3.182)" class="text-xs p-1.5 border border-slate-300 rounded w-1/3 focus:ring-emerald-500" />
            <input v-model.number="db.porta" type="number" placeholder="Porta" class="text-xs p-1.5 border border-slate-300 rounded w-1/5 focus:ring-emerald-500" />
            <button type="button" @click="removeBanco(idx)" class="text-slate-400 hover:text-rose-600 p-1" title="Remover Banco">
              <TrashIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
        -->

        <div class="flex justify-end gap-3 pt-4">
          <Button variant="secondary" type="button" @click="showModal = false">Cancelar</Button>
          <Button variant="primary" type="submit" :disabled="submitting">
            {{ editingAppId ? 'Salvar Alterações' : 'Cadastrar' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import {
  ChartBarIcon,
  ArrowPathIcon,
  PlusIcon,
  ServerIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  BellAlertIcon,
  CpuChipIcon,
  ShieldExclamationIcon,
  ExclamationCircleIcon,
  ClockIcon,
  UsersIcon,
  PencilSquareIcon,
  TrashIcon,
  ChevronUpIcon,
  ChevronDownIcon
} from '@heroicons/vue/24/outline';

const loading = ref(false);
const submitting = ref(false);
const showModal = ref(false);
const editingAppId = ref<number | null>(null);
const refreshIntervalSeconds = ref(10);
let refreshTimer: any = null;

const allExpanded = ref(true);

const toggleExpandAll = () => {
  allExpanded.value = !allExpanded.value;
};

const summary = ref({
  total_apps: 0,
  online_apps: 0,
  offline_apps: 0,
  avg_latency_ms: 0,
  active_problems_count: 0
});

const applications = ref<any[]>([]);
const zabbixProblems = ref<any[]>([]);

const integracoesDisponiveis = ref<any[]>([]);

const fetchIntegracoes = async () => {
  try {
    const res = await api.get('/api/integracoes');
    integracoesDisponiveis.value = res.data || [];
  } catch (err) {
    console.error("Erro ao carregar integrações:", err);
  }
};

const appForm = ref<{
  nome: string;
  url_base: string;
  usar_framework_setisd: boolean;
  possui_rota_health: boolean;
  url_health: string;
  possui_banco_aghu: boolean;
  monitora_usuarios_ativos: boolean;
  zabbix_host_id: string;
  criticidade: string;
  integracao_id: number | null;
  bancos_adicionais: Array<{ nome: string; host: string; porta: number }>;
  tipo_checagem: string;
  porta_tcp: number | null;
  ssh_host: string;
  http_headers: any;
  servicos_monitorados: any;
}>({
  nome: '',
  url_base: '',
  usar_framework_setisd: false,
  possui_rota_health: false,
  url_health: '',
  possui_banco_aghu: false,
  monitora_usuarios_ativos: false,
  zabbix_host_id: '',
  criticidade: 'MEDIA',
  integracao_id: null,
  bancos_adicionais: [],
  tipo_checagem: 'HTTP',
  porta_tcp: null,
  ssh_host: '',
  http_headers: null,
  servicos_monitorados: null
});

const onFrameworkToggle = () => {
  if (appForm.value.usar_framework_setisd) {
    appForm.value.possui_rota_health = true;
    appForm.value.url_health = '/api/health';
    appForm.value.monitora_usuarios_ativos = true;
    appForm.value.possui_banco_aghu = false; // Não pré-marcado
  } else {
    appForm.value.possui_rota_health = false;
    appForm.value.url_health = '';
    appForm.value.monitora_usuarios_ativos = false;
    appForm.value.possui_banco_aghu = false;
  }
};

const openAddModal = () => {
  fetchIntegracoes();
  editingAppId.value = null;
  appForm.value = {
    nome: '',
    url_base: '',
    usar_framework_setisd: false,
    possui_rota_health: false,
    url_health: '',
    possui_banco_aghu: false,
    monitora_usuarios_ativos: false,
    zabbix_host_id: '',
    criticidade: 'MEDIA',
    integracao_id: null,
    bancos_adicionais: [],
    tipo_checagem: 'HTTP',
    porta_tcp: null,
    ssh_host: '',
    http_headers: null,
    servicos_monitorados: null
  };
  showModal.value = true;
};

const openEditModal = (app: any) => {
  fetchIntegracoes();
  editingAppId.value = app.aplicacao_id || app.id;
  let parsedBancos: any[] = [];
  if (app.bancos_adicionais) {
    if (typeof app.bancos_adicionais === 'string') {
      try {
        parsedBancos = JSON.parse(app.bancos_adicionais);
      } catch (e) {
        parsedBancos = [];
      }
    } else if (Array.isArray(app.bancos_adicionais)) {
      parsedBancos = app.bancos_adicionais;
    }
  }

  const pHealth = app.possui_rota_health !== false;
  const pAghu = app.possui_banco_aghu !== false;
  const pUsers = app.monitora_usuarios_ativos !== false;
  const isFw = pHealth && (app.url_health === '/api/health' || !app.url_health) && pAghu && pUsers;

  appForm.value = {
    nome: app.nome || '',
    url_base: app.url_base || '',
    usar_framework_setisd: isFw,
    possui_rota_health: pHealth,
    url_health: app.url_health || '/api/health',
    possui_banco_aghu: pAghu,
    monitora_usuarios_ativos: pUsers,
    zabbix_host_id: app.zabbix_host_id || '',
    criticidade: app.criticidade || 'MEDIA',
    integracao_id: app.integracao_id || null,
    bancos_adicionais: parsedBancos,
    tipo_checagem: app.tipo_checagem || 'HTTP',
    porta_tcp: app.porta_tcp ?? null,
    ssh_host: app.ssh_host || '',
    http_headers: app.http_headers ?? null,
    servicos_monitorados: app.servicos_monitorados ?? null
  };
  showModal.value = true;
};

const fetchDashboardData = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/monitor/dashboard');
    if (res.data) {
      summary.value = res.data.summary || summary.value;
      applications.value = res.data.applications || [];
      zabbixProblems.value = res.data.zabbix_problems || [];
    }
  } catch (err) {
    console.error("Erro ao carregar dados do dashboard:", err);
  } finally {
    loading.value = false;
  }
};

const updateRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
  if (refreshIntervalSeconds.value > 0) {
    refreshTimer = setInterval(() => {
      fetchDashboardData();
    }, refreshIntervalSeconds.value * 1000);
  }
};

const handleSaveApp = async () => {
  submitting.value = true;
  try {
    if (editingAppId.value) {
      await api.put(`/api/monitor/aplicacoes/${editingAppId.value}`, appForm.value);
    } else {
      await api.post('/api/monitor/aplicacoes', appForm.value);
    }
    showModal.value = false;
    await fetchDashboardData();
  } catch (err: any) {
    console.error("Erro ao salvar aplicação:", err);
    alert(err?.response?.data?.detail || "Erro ao salvar a aplicação. Verifique as informações.");
  } finally {
    submitting.value = false;
  }
};

const handleDeleteApp = async (id: number) => {
  if (!id) {
    alert("Erro: ID da aplicação inválido para exclusão.");
    return;
  }
  if (!confirm("Tem certeza que deseja excluir esta aplicação do monitoramento?")) {
    return;
  }
  try {
    await api.delete(`/api/monitor/aplicacoes/${id}`);
    await fetchDashboardData();
  } catch (err: any) {
    console.error("Erro ao excluir aplicação:", err);
    alert(err?.response?.data?.detail || "Erro ao excluir aplicação do monitoramento.");
  }
};

const getMetricBarColor = (pct: number) => {
  if (pct >= 80) return 'bg-rose-500';
  if (pct >= 60) return 'bg-amber-500';
  return 'bg-emerald-500';
};

const getMetricTextColor = (pct: number) => {
  if (pct >= 80) return 'text-rose-600 font-bold';
  if (pct >= 60) return 'text-amber-600 font-bold';
  return 'text-emerald-600 font-bold';
};

const getMetricBadgeClass = (pct: number) => {
  if (pct >= 80) return 'bg-rose-100 text-rose-800 font-bold';
  if (pct >= 60) return 'bg-amber-100 text-amber-800 font-bold';
  return 'bg-emerald-50 text-emerald-700 font-medium';
};

const getCardBorderClass = (app: any) => {
  if (!app.is_online) {
    return 'border-rose-300 bg-rose-50/20';
  }
  const z = app.zabbix;
  if (z) {
    const maxUsage = Math.max(z.cpu_usage || 0, z.memory_usage || 0, z.disk_usage || 0);
    if (maxUsage >= 80) {
      return 'border-rose-300 bg-white ring-1 ring-rose-200';
    }
    if (maxUsage >= 60) {
      return 'border-amber-300 bg-white ring-1 ring-amber-200';
    }
  }
  return 'border-emerald-200 bg-white';
};

const getSeverityClass = (severity: string) => {
  switch (severity) {
    case 'HIGH':
    case 'DISASTER':
      return 'bg-rose-50 border-rose-200 text-rose-800';
    case 'AVERAGE':
      return 'bg-amber-50 border-amber-200 text-amber-800';
    default:
      return 'bg-blue-50 border-blue-200 text-blue-800';
  }
};

const formatDbName = (name: string) => {
  const map: Record<string, string> = {
    'app_db': 'Banco Aplicação',
    'aghu_postgres': 'Banco AGHU',
    'aghu_db': 'Banco AGHU',
    'postgres': 'Banco PostgreSQL'
  };
  if (map[name]) return map[name];
  if (name.length > 22) return name.substring(0, 20) + '...';
  return name;
};

const expandedDbsMap = ref<Record<number, boolean>>({});

const toggleDbExpand = (appId: number) => {
  expandedDbsMap.value[appId] = !expandedDbsMap.value[appId];
};

const isDbExpanded = (appId: number) => {
  return !!expandedDbsMap.value[appId];
};

const getConnectedDbCount = (databases: Record<string, string> | undefined) => {
  if (!databases) return 0;
  return Object.values(databases).filter(st => {
    const str = String(st).toLowerCase();
    return str.includes('connected') || str.includes('ok');
  }).length;
};

onMounted(() => {
  fetchDashboardData();
  updateRefreshTimer();
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
</script>
