<template>
  <div class="relative h-screen overflow-hidden md:flex bg-slate-100">
    <!-- Mobile Menu Header -->
    <div class="bg-slate-900 text-slate-100 flex justify-between md:hidden shrink-0 border-b border-slate-800">
      <router-link to="/" class="block p-4 text-emerald-400 font-black text-lg flex items-center gap-2">
        <ChartBarSquareIcon class="h-6 w-6 text-emerald-500" />
        {{ SYSTEM_TITLE }}
      </router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-4 focus:outline-none focus:bg-slate-800">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar (Paleta Esmeralda & Slate Dark) -->
    <aside 
      :class="[
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        isCollapsed ? 'md:w-20' : 'md:w-64'
      ]" 
      class="bg-slate-900 border-r border-slate-800 text-slate-200 pt-6 pb-4 px-3 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition-all duration-300 ease-in-out z-20 h-full shrink-0 flex flex-col justify-between shadow-xl"
    >
      <div>
        <!-- Logo e Branding do MonitoraUSID -->
        <div 
          @click="toggleSidebar" 
          title="Clique para recolher / expandir o menu"
          class="cursor-pointer text-white flex items-center space-x-3 px-2 mb-6 hover:opacity-90 transition duration-150 group select-none"
        >
          <div class="p-2.5 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl shadow-lg shadow-emerald-500/20 text-white shrink-0 group-hover:scale-105 transition-transform">
            <ChartBarSquareIcon class="h-7 w-7" />
          </div>
          <span v-if="!isCollapsed" class="text-xl font-black tracking-tight text-white leading-snug break-words">
            Monitora<span class="text-emerald-400">USID</span>
          </span>
        </div>

        <div class="px-1 my-4">
          <div class="border-t border-slate-800"></div>
        </div>

        <!-- Links de Navegação -->
        <nav class="space-y-1.5">
          <router-link 
            to="/" 
            :title="isCollapsed ? 'Dashboard' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-3.5']"
            class="flex items-center space-x-3 py-2.5 rounded-xl text-sm font-semibold transition duration-200 text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <ChartBarIcon class="h-5 w-5 text-emerald-400 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate">Dashboard</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/historico" 
            :title="isCollapsed ? 'Histórico' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-3.5']"
            class="flex items-center space-x-3 py-2.5 rounded-xl text-sm font-semibold transition duration-200 text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <ClockIcon class="h-5 w-5 text-indigo-400 shrink-0" />
            <span v-if="!isCollapsed" class="truncate">Histórico</span>
          </router-link>
          
          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/configuracoes" 
            :title="isCollapsed ? 'Configurações' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-3.5']"
            class="flex items-center space-x-3 py-2.5 rounded-xl text-sm font-semibold transition duration-200 text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <Cog6ToothIcon class="h-5 w-5 text-amber-400 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate">Configurações</span>
          </router-link>
        </nav>
      </div>

      <!-- Rodapé de Versão da Sidebar -->
      <div v-if="!isCollapsed" class="px-3 pt-3 pb-1 border-t border-slate-800 text-xs text-slate-400 mt-auto truncate transition-opacity duration-200">
        <p class="font-bold text-slate-200 truncate">{{ APP_NAME }}</p>
        <p class="text-[11px] text-slate-500 truncate">Versão {{ APP_VERSION }} | HC-UFPE</p>
      </div>
      <div v-else class="px-2 pt-3 pb-1 border-t border-slate-800 text-[10px] text-center text-slate-500 mt-auto font-mono">
        v{{ APP_VERSION }}
      </div>
    </aside>

    <!-- Conteúdo Principal -->
    <div class="flex-1 flex flex-col bg-slate-50 overflow-y-auto h-full">
      <header class="flex justify-between items-center px-8 py-4 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10">
        <div class="flex items-center gap-3">
          <!-- Botão para Recolher/Expandir Menu Lateral -->
          <button 
            @click="toggleSidebar" 
            class="hidden md:flex p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            :title="isCollapsed ? 'Expandir Menu' : 'Recolher Menu'"
          >
            <ArrowsRightLeftIcon class="h-5 w-5" />
          </button>
          <h1 class="text-xl font-black text-slate-900 tracking-tight">{{ $route.name }}</h1>
        </div>

        <div class="flex items-center space-x-3">
          <!-- Botão Modo Tela Cheia / Painel de Monitoramento -->
          <button 
            @click="toggleFullScreen" 
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-bold transition-all shadow-sm"
            :title="isFullScreen ? 'Sair da Tela Cheia' : 'Modo Painel Tela Cheia'"
          >
            <ArrowsPointingOutIcon v-if="!isFullScreen" class="h-4 w-4 text-emerald-600" />
            <ArrowsPointingInIcon v-else class="h-4 w-4 text-amber-600" />
            <span>{{ isFullScreen ? 'Sair da Tela Cheia' : 'Modo Painel' }}</span>
          </button>

          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  ChartBarIcon,
  ChartBarSquareIcon,
  ClockIcon,
  Cog6ToothIcon,
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  ArrowsRightLeftIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { APP_VERSION, APP_NAME, SYSTEM_TITLE } from '../config/version';

const sidebarOpen = ref(false);
const isCollapsed = ref(false);
const isFullScreen = ref(false);

const route = useRoute();
const authStore = useAuthStore();

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().then(() => {
      isFullScreen.value = true;
      isCollapsed.value = true;
    }).catch(err => {
      console.error("Erro ao ativar tela cheia:", err);
    });
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen().then(() => {
        isFullScreen.value = false;
      });
    }
  }
};

// Fechar sidebar mobile ao navegar
watch(() => route.path, () => {
  sidebarOpen.value = false;
});
</script>