<template>
  <div class="w-full max-w-md mx-auto">
    <!-- Card de Login Estilo Executive Glassmorphism -->
    <div class="bg-white/95 backdrop-blur-xl rounded-3xl border border-gray-100 shadow-2xl p-8 space-y-6 transition-all duration-300">
      
      <!-- Cabeçalho / Branding -->
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center p-4 bg-emerald-500/10 text-emerald-600 rounded-2xl ring-8 ring-emerald-500/5 mb-2">
          <ChartBarSquareIcon class="h-10 w-10" />
        </div>
        <h1 class="text-3xl font-black tracking-tight text-gray-900">MonitoraUSID</h1>
        <p class="text-xs text-gray-500">Sistema Centralizado de Monitoramento de Aplicações</p>
      </div>

      <!-- Formulário de Autenticação -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5" for="username">
            Login Corporativo / AD
          </label>
          <div class="relative">
            <input 
              v-model="username" 
              id="username" 
              type="text" 
              required
              class="w-full pl-10 pr-4 py-3 bg-gray-50/80 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 focus:bg-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all outline-none" 
              placeholder="ex: EBSERHNET\usuario"
            />
            <UserIcon class="h-5 w-5 text-gray-400 absolute left-3 top-3.5" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5" for="password">
            Senha
          </label>
          <div class="relative">
            <input 
              v-model="password" 
              id="password" 
              :type="passwordFieldType" 
              required
              class="w-full pl-10 pr-10 py-3 bg-gray-50/80 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 focus:bg-white focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all outline-none" 
              placeholder="••••••••••••"
            />
            <LockClosedIcon class="h-5 w-5 text-gray-400 absolute left-3 top-3.5" />
            <button 
              type="button" 
              @click="togglePasswordVisibility" 
              class="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <component :is="passwordFieldType === 'password' ? EyeIcon : EyeSlashIcon" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs">
          <label class="flex items-center space-x-2 cursor-pointer select-none">
            <input type="checkbox" v-model="rememberMe" class="rounded text-emerald-600 focus:ring-emerald-500 h-4 w-4 border-gray-300" />
            <span class="text-gray-600 font-medium">Lembrar de mim</span>
          </label>

          <span class="text-emerald-600 font-semibold text-[11px] bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
            AD / Mock Actived
          </span>
        </div>

        <!-- Botões de Ação -->
        <div class="pt-2">
          <button 
            type="submit" 
            :disabled="loading"
            class="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-sm rounded-xl shadow-lg shadow-emerald-600/20 active:scale-[0.99] transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <ArrowRightOnRectangleIcon v-if="!loading" class="h-5 w-5" />
            <ArrowPathIcon v-else class="h-5 w-5 animate-spin" />
            <span>{{ loading ? 'Autenticando...' : 'Acessar Sistema' }}</span>
          </button>
        </div>
      </form>

      <!-- Feedback de Erro -->
      <div v-if="error" class="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center gap-2 animate-shake">
        <ExclamationCircleIcon class="h-5 w-5 text-rose-500 shrink-0" />
        <span>{{ error }}</span>
      </div>

      <!-- Rodapé do Card -->
      <div class="pt-4 border-t border-gray-100 text-center space-y-1">
        <p class="text-xs font-bold text-gray-700">{{ HOSPITAL_NAME }}</p>
        <p class="text-[11px] text-gray-400">{{ DEPARTMENT_NAME }} | v{{ APP_VERSION }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { 
  ChartBarSquareIcon, 
  UserIcon, 
  LockClosedIcon, 
  EyeIcon, 
  EyeSlashIcon, 
  ArrowRightOnRectangleIcon,
  ArrowPathIcon,
  ExclamationCircleIcon 
} from '@heroicons/vue/24/outline';
import { APP_VERSION, HOSPITAL_NAME, DEPARTMENT_NAME } from '../config/version';

const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const error = ref('');
const loading = ref(false);
const passwordVisible = ref(false);

const router = useRouter();
const authStore = useAuthStore();

const passwordFieldType = computed(() => passwordVisible.value ? 'text' : 'password');

const togglePasswordVisibility = () => {
  passwordVisible.value = !passwordVisible.value;
};

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(username.value, password.value, rememberMe.value);
    await router.push('/');
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Falha na autenticação. Verifique o usuário e senha.';
  } finally {
    loading.value = false;
  }
};
</script>
