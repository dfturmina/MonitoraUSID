<template>
  <div class="space-y-6">
    <!-- Cabeçalho das Configurações -->
    <Card>
      <template #header>
        <div class="flex items-center space-x-3">
          <Cog6ToothIcon class="h-7 w-7 text-paper-text" />
          <h1 class="text-2xl font-bold text-paper-text">Configurações</h1>
        </div>
      </template>

      <div v-if="authStore.isAdmin" class="space-y-6">
        <p class="text-gray-600 leading-relaxed">
          Gerencie o seu perfil corporativo, o cadastro de usuários autorizados e a atribuição de perfis de acesso (RBAC) do **Framework-SETISD-HC-UFPE**.
        </p>

        <!-- 1. Perfil do Usuário Logado -->
        <div v-if="authStore.user" class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-3">
          <div class="flex items-center space-x-2 text-paper-text font-bold text-lg border-b pb-2">
            <UserCircleIcon class="h-6 w-6 text-gray-500" />
            <span>Seu Perfil Corporativo (Active Directory)</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm pt-1">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Usuário / Login AD</p>
              <p class="font-bold text-gray-800">{{ authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Nome Completo</p>
              <p class="font-medium text-gray-800">{{ authStore.user.displayName?.[0] || authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">E-mail Corporativo</p>
              <p class="font-medium text-gray-800">{{ authStore.user.email?.[0] || 'Não cadastrado' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Setor / Departamento</p>
              <p class="font-medium text-gray-800">{{ authStore.user.department?.[0] || 'SETISD / HC-UFPE' }}</p>
            </div>
          </div>
        </div>

        <!-- 2. Painel de Gestão de Usuários e Perfis (RBAC Local) -->
        <div class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b pb-3 gap-3">
            <div>
              <h2 class="text-lg font-bold text-paper-text flex items-center gap-2">
                <UserGroupIcon class="h-6 w-6 text-gray-600" />
                Usuários do Sistema (RBAC Local)
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Inclua o login do Active Directory (AD) de um colaborador para autorizar o acesso a este sistema.
              </p>
            </div>
            <Button variant="primary" @click="showAddUserModal = true">
              <template #icon>
                <UserPlusIcon class="h-5 w-5" />
              </template>
              Incluir Usuário
            </Button>
          </div>

          <!-- Tabela de Usuários Cadastrados -->
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-600">
              <thead class="bg-gray-50 text-xs uppercase font-semibold text-gray-500 border-b">
                <tr>
                  <th class="py-3 px-4">Login de Rede</th>
                  <th class="py-3 px-4">Nome do Colaborador</th>
                  <th class="py-3 px-4">Perfil de Acesso</th>
                  <th class="py-3 px-4 text-center">Status</th>
                  <th class="py-3 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="user in usersList" :key="user.id" class="hover:bg-gray-50/80 transition-colors">
                  <td class="py-3 px-4 font-bold text-gray-800 flex items-center gap-2">
                    <UserIcon class="h-4 w-4 text-gray-400" />
                    {{ user.username }}
                  </td>
                  <td class="py-3 px-4 font-medium text-gray-700">{{ user.nome }}</td>
                  <td class="py-3 px-4">
                    <span :class="getRoleBadgeClass(user.perfil)" class="px-2.5 py-1 text-xs font-bold rounded-md">
                      {{ user.perfil }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span :class="user.ativo ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'" class="px-2 py-0.5 text-xs font-bold rounded">
                      {{ user.ativo ? 'ATIVO' : 'INATIVO' }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-right space-x-2">
                    <button 
                      @click="openEditModal(user)" 
                      title="Alterar Perfil" 
                      class="px-2.5 py-1 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md transition"
                    >
                      Alterar Perfil
                    </button>
                    <button 
                      @click="toggleUserStatus(user)" 
                      :class="user.ativo ? 'text-red-600 hover:bg-red-50 border-red-200' : 'text-emerald-600 hover:bg-emerald-50 border-emerald-200'"
                      class="px-2.5 py-1 text-xs font-semibold border rounded-md transition"
                    >
                      {{ user.ativo ? 'Inativar' : 'Ativar' }}
                    </button>
                    <button 
                      @click="removeUser(user.id)" 
                      title="Excluir Usuário"
                      class="px-2 py-1 text-xs font-semibold text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md transition"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 3. Integrações de Serviços de Terceiros (Metabase, Grafana, Prometheus) -->
        <div class="space-y-3 pt-4 border-t">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 class="text-md font-bold text-gray-800 flex items-center gap-2">
                <LinkIcon class="h-5 w-5 text-indigo-600" />
                Integrações de Serviços de Terceiros (APIs / Chaves de Acesso)
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Cadastre chaves de API e tokens para integração dinâmica com Metabase, Grafana ou Prometheus.
              </p>
            </div>
            <Button variant="secondary" size="sm" @click="openAddIntegracaoModal">
              <template #icon>
                <PlusIcon class="h-4 w-4" />
              </template>
              Nova Integração
            </Button>
          </div>

          <div v-if="loadingIntegracoes" class="py-4 text-center text-xs text-gray-400">
            Carregando integrações cadastradas...
          </div>
          <div v-else-if="integracoes.length === 0" class="p-4 bg-gray-50 border border-dashed rounded-xl text-center text-xs text-gray-500">
            Nenhuma integração de terceiro cadastrada.
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div 
              v-for="integ in integracoes" 
              :key="integ.id" 
              class="p-4 bg-white border border-gray-200 rounded-xl flex items-center justify-between shadow-sm"
            >
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 text-[10px] font-black uppercase rounded bg-indigo-100 text-indigo-800">
                    {{ integ.provedor }}
                  </span>
                  <h3 class="font-bold text-sm text-gray-900">{{ integ.nome }}</h3>
                </div>
                <p class="text-xs font-mono text-gray-500">{{ integ.url_base }}</p>
                <p class="text-[11px] text-gray-400 font-mono">Chave: {{ integ.api_key_masked }}</p>
              </div>
              <button 
                @click="removeIntegracao(integ.id)" 
                class="p-1.5 text-gray-400 hover:text-red-600 transition"
                title="Excluir Integração"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- 3.1. Alertas Microsoft Teams (Notificações em Tempo Real) -->
        <div class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-3 gap-3">
            <div>
              <h2 class="text-md font-bold text-gray-800 flex items-center gap-2">
                <BellAlertIcon class="h-5 w-5 text-indigo-600" />
                Alertas Microsoft Teams (Notificações em Tempo Real)
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Notifica o seu chat pessoal ou grupo do Teams imediatamente quando qualquer sistema monitorado cair ou se restabelecer.
              </p>
            </div>
            <Button variant="secondary" size="sm" :disabled="testingTeams" @click="testTeamsAlert">
              <template #icon>
                <PaperAirplaneIcon class="h-4 w-4 text-indigo-600" />
              </template>
              {{ testingTeams ? 'Enviando...' : 'Testar Alerta Teams' }}
            </Button>
          </div>
          
          <div class="flex flex-wrap items-center gap-3 text-xs">
            <span class="font-bold text-gray-600">Status dos Alertas:</span>
            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800 flex items-center gap-1.5">
              <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Daemon Ativo no Servidor (Checagem contínua a cada 60s)
            </span>
          </div>

          <p v-if="teamsTestResult" :class="teamsTestSuccess ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-rose-700 bg-rose-50 border-rose-200'" class="p-2.5 rounded-lg border text-xs font-semibold">
            {{ teamsTestResult }}
          </p>
        </div>

        <!-- 4. Guias e Exemplos de Perfis (Informativo) -->
        <div class="p-5 bg-gray-50 border border-gray-200 rounded-xl space-y-3">
          <div class="flex items-center space-x-2 text-paper-text font-bold text-md border-b pb-2">
            <ShieldCheckIcon class="h-5 w-5 text-gray-600" />
            <span>Exemplos de Perfis Disponíveis para Atribuição</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-1">
            <div 
              v-for="roleItem in availableRoles" 
              :key="roleItem.nome"
              class="p-3 bg-white border border-gray-200 rounded-lg space-y-1"
            >
              <span :class="roleItem.badgeClass" class="px-2 py-0.5 text-xs font-bold rounded">
                {{ roleItem.nome }}
              </span>
              <p class="text-xs text-gray-500 pt-1 leading-relaxed">{{ roleItem.descricao }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">
        <h2 class="text-lg font-bold">Acesso Restrito</h2>
        <p class="text-sm mt-1">Você precisa de privilégios de administrador para visualizar as configurações avançadas.</p>
      </div>
    </Card>

    <!-- Modal 1: Incluir Novo Usuário AD -->
    <Modal :show="showAddUserModal" @close="closeAddModal">
      <template #header>Incluir Usuário no Sistema</template>
      <form @submit.prevent="saveUser" class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Login de Rede</label>
          <div class="flex gap-2">
            <input 
              v-model="newUser.username" 
              type="text" 
              required 
              placeholder="Ex: joao.silva"
              @keyup.enter.prevent="searchADUser"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
            />
            <Button 
              variant="secondary" 
              type="button" 
              :disabled="isSearchingAD || !newUser.username.trim()" 
              @click="searchADUser"
            >
              <span v-if="isSearchingAD" class="text-xs font-semibold">Buscando...</span>
              <span v-else class="text-xs font-semibold flex items-center gap-1">
                <MagnifyingGlassIcon class="h-4 w-4" />
                Consultar Login
              </span>
            </Button>
          </div>
          <p class="text-xs text-gray-400 mt-1">Digite o login de rede corporativo (ex: `joao.silva`).</p>
        </div>

        <!-- Banner de Resultado da Consulta AD -->
        <div v-if="adSearchStatus === 'success' && adSearchData" class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs space-y-1">
          <p class="font-bold flex items-center gap-1 text-sm text-emerald-900">
            <CheckCircleIcon class="h-4 w-4 text-emerald-600 shrink-0" />
            Usuário localizado e validado no Active Directory (EBSERHNET)
          </p>
          <p><strong>Nome Completo:</strong> {{ adSearchData.displayName }}</p>
          <p v-if="adSearchData.email"><strong>E-mail:</strong> {{ adSearchData.email }}</p>
          <p><strong>Lotação / Setor:</strong> {{ adSearchData.department }}</p>
        </div>

        <div v-if="adSearchStatus === 'error'" class="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs flex items-center gap-2">
          <ExclamationTriangleIcon class="h-4 w-4 text-red-500 shrink-0" />
          <span>{{ adErrorMessage }}</span>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Nome Completo do Colaborador</label>
          <input 
            v-model="newUser.nome" 
            type="text" 
            required 
            placeholder="Ex: João da Silva"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Perfil de Acesso</label>
          <select 
            v-model="newUser.perfil" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm bg-white"
          >
            <option value="" disabled>Selecione um perfil...</option>
            <option v-for="role in availableRoles" :key="role.nome" :value="role.nome">
              {{ role.nome }}
            </option>
          </select>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="closeAddModal">Cancelar</Button>
          <Button variant="primary" type="submit">Incluir Usuário</Button>
        </div>
      </form>
    </Modal>

    <!-- Modal 2: Alterar Perfil do Usuário -->
    <Modal :show="showEditUserModal" @close="closeEditModal">
      <template #header>Alterar Perfil de Acesso</template>
      <form v-if="editingUser" @submit.prevent="updateUserRole" class="space-y-4">
        <div class="p-3 bg-gray-50 border rounded-lg space-y-1 text-sm">
          <p><strong class="text-gray-700">Login de Rede:</strong> <span class="font-bold text-gray-900">{{ editingUser.username }}</span></p>
          <p><strong class="text-gray-700">Nome:</strong> {{ editingUser.nome }}</p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Selecione o Novo Perfil de Acesso</label>
          <select 
            v-model="editingUser.perfil" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm bg-white"
          >
            <option v-for="role in availableRoles" :key="role.nome" :value="role.nome">
              {{ role.nome }}
            </option>
          </select>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="closeEditModal">Cancelar</Button>
          <Button variant="primary" type="submit">Salvar Perfil</Button>
        </div>
      </form>
    </Modal>

    <!-- Modal 3: Cadastrar Nova Integração de Terceiro -->
    <Modal :show="showAddIntegracaoModal" @close="showAddIntegracaoModal = false">
      <template #header>Cadastrar Nova Integração (API / Chave)</template>
      <form @submit.prevent="handleSaveIntegracao" autocomplete="off" class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Nome da Integração</label>
          <input v-model="newIntegracao.nome" required type="text" autocomplete="off" placeholder="Ex: Metabase HC-UFPE" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Provedor</label>
          <select v-model="newIntegracao.provedor" required class="w-full px-3 py-2 border rounded-lg text-sm bg-white">
            <option value="METABASE">Metabase (API Key / Token)</option>
            <option value="GRAFANA">Grafana (Service Account Token)</option>
            <option value="PROMETHEUS">Prometheus / Outros</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">URL Base do Serviço</label>
          <input v-model="newIntegracao.url_base" required type="url" autocomplete="off" placeholder="http://relatorios.hc-ufpe.ebserh" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Chave de API / Token (X-API-Key / Bearer)</label>
          <input v-model="newIntegracao.api_key" required type="password" autocomplete="new-password" placeholder="Token ou Chave secreta de API" class="w-full px-3 py-2 border rounded-lg text-sm font-mono" />
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="showAddIntegracaoModal = false">Cancelar</Button>
          <Button variant="primary" type="submit" :disabled="submittingIntegracao">Salvar Integração</Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Card from '../components/Card.vue';
import Modal from '../components/Modal.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  Cog6ToothIcon, 
  UserCircleIcon, 
  ShieldCheckIcon, 
  UserGroupIcon, 
  UserPlusIcon, 
  UserIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  LinkIcon,
  PlusIcon,
  TrashIcon,
  BellAlertIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const showAddUserModal = ref(false);
const showEditUserModal = ref(false);

const testingTeams = ref(false);
const teamsTestResult = ref('');
const teamsTestSuccess = ref(false);

const testTeamsAlert = async () => {
  testingTeams.value = true;
  teamsTestResult.value = '';
  try {
    const res = await api.post('/api/monitor/test-teams-alert');
    teamsTestSuccess.value = true;
    teamsTestResult.value = res.data?.detail || "Alerta de teste enviado com sucesso para o Teams!";
  } catch (err: any) {
    teamsTestSuccess.value = false;
    teamsTestResult.value = err?.response?.data?.detail || "Erro ao disparar teste para o Teams.";
  } finally {
    testingTeams.value = false;
  }
};

const integracoes = ref<any[]>([]);
const loadingIntegracoes = ref(false);
const showAddIntegracaoModal = ref(false);
const submittingIntegracao = ref(false);

const newIntegracao = ref({
  nome: '',
  provedor: 'METABASE',
  url_base: '',
  api_key: ''
});

const fetchIntegracoes = async () => {
  loadingIntegracoes.value = true;
  try {
    const res = await api.get('/api/integracoes');
    integracoes.value = res.data || [];
  } catch (err) {
    console.error("Erro ao buscar integrações:", err);
  } finally {
    loadingIntegracoes.value = false;
  }
};

const openAddIntegracaoModal = () => {
  newIntegracao.value = { nome: '', provedor: 'METABASE', url_base: '', api_key: '' };
  showAddIntegracaoModal.value = true;
};

const handleSaveIntegracao = async () => {
  submittingIntegracao.value = true;
  try {
    await api.post('/api/integracoes', newIntegracao.value);
    showAddIntegracaoModal.value = false;
    await fetchIntegracoes();
  } catch (err: any) {
    alert(err?.response?.data?.detail || "Erro ao salvar integração.");
  } finally {
    submittingIntegracao.value = false;
  }
};

const removeIntegracao = async (id: number) => {
  if (!confirm("Tem certeza que deseja excluir esta integração?")) return;
  try {
    await api.delete(`/api/integracoes/${id}`);
    await fetchIntegracoes();
  } catch (err: any) {
    alert("Erro ao excluir integração.");
  }
};

interface UserRBAC {
  id: number;
  username: string;
  nome: string;
  perfil: string;
  ativo: boolean;
}

interface ADUserData {
  exists: boolean;
  username: string;
  displayName: string;
  email: string;
  department: string;
}

const availableRoles = [
  { nome: 'ADMINISTRADOR', descricao: 'Gestão total do sistema, adição de aplicações, Zabbix e controle de usuários.', badgeClass: 'bg-purple-100 text-purple-800' },
  { nome: 'OPERADOR', descricao: 'Gestão operacional de alertas, acompanhamento do poller e checagem de indisponibilidade.', badgeClass: 'bg-emerald-100 text-emerald-800' },
  { nome: 'CONSULTA', descricao: 'Acesso estritamente somente-leitura (Read-Only) aos dashboards e estatísticas.', badgeClass: 'bg-gray-100 text-gray-800' }
];

// Lista Inicial Simulada de Usuários RBAC Autorizados no Banco Local (data/app.db)
const usersList = ref<UserRBAC[]>([
  { id: 1, username: 'admin', nome: 'Administrador do MonitoraUSID', perfil: 'ADMINISTRADOR', ativo: true },
  { id: 2, username: 'operador.setisd', nome: 'Operador de Infraestrutura SETISD', perfil: 'OPERADOR', ativo: true },
  { id: 3, username: 'gestao.hospitalar', nome: 'Consulta de Indicadores SETISD', perfil: 'CONSULTA', ativo: true }
]);

const newUser = ref({
  username: '',
  nome: '',
  perfil: availableRoles[0].nome
});

const isSearchingAD = ref(false);
const adSearchStatus = ref<'idle' | 'success' | 'error'>('idle');
const adErrorMessage = ref('');
const adSearchData = ref<ADUserData | null>(null);

const editingUser = ref<UserRBAC | null>(null);

const getRoleBadgeClass = (perfil: string) => {
  const role = availableRoles.find(r => r.nome === perfil);
  return role ? role.badgeClass : 'bg-gray-100 text-gray-700';
};

const searchADUser = async () => {
  const username = newUser.value.username.trim();
  if (!username) return;

  isSearchingAD.value = true;
  adSearchStatus.value = 'idle';
  adErrorMessage.value = '';
  adSearchData.value = null;

  try {
    const response = await api.get<ADUserData>(`/api/admin/ad-user-search/${encodeURIComponent(username)}`);
    const data = response.data;

    if (data && data.exists) {
      adSearchStatus.value = 'success';
      adSearchData.value = data;
      newUser.value.nome = data.displayName;
    } else {
      adSearchStatus.value = 'error';
      adErrorMessage.value = `Usuário '${username}' não foi localizado no Active Directory. Verifique se o login está correto.`;
    }
  } catch (err: any) {
    adSearchStatus.value = 'error';
    adErrorMessage.value = err.response?.data?.detail || 'Erro ao consultar o Active Directory. Tente novamente.';
  } finally {
    isSearchingAD.value = false;
  }
};

const closeAddModal = () => {
  showAddUserModal.value = false;
  newUser.value = { username: '', nome: '', perfil: availableRoles[0].nome };
  adSearchStatus.value = 'idle';
  adSearchData.value = null;
  adErrorMessage.value = '';
};

const closeEditModal = () => {
  showEditUserModal.value = false;
  editingUser.value = null;
};

const saveUser = () => {
  if (!newUser.value.username || !newUser.value.nome) return;

  usersList.value.push({
    id: Date.now(),
    username: newUser.value.username.trim().toLowerCase(),
    nome: newUser.value.nome.trim(),
    perfil: newUser.value.perfil,
    ativo: true
  });

  closeAddModal();
};

const openEditModal = (user: UserRBAC) => {
  editingUser.value = { ...user };
  showEditUserModal.value = true;
};

const updateUserRole = () => {
  if (!editingUser.value) return;

  const index = usersList.value.findIndex(u => u.id === editingUser.value?.id);
  if (index !== -1) {
    usersList.value[index].perfil = editingUser.value.perfil;
  }

  closeEditModal();
};

const toggleUserStatus = (user: UserRBAC) => {
  user.ativo = !user.ativo;
};

const removeUser = (userId: number) => {
  usersList.value = usersList.value.filter(u => u.id !== userId);
};

onMounted(() => {
  fetchIntegracoes();
});
</script>
