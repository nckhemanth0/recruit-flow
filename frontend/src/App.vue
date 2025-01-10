<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activePath = computed(() => route.name)

const logout = async () => {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <RouterLink to="/" class="flex items-center gap-2 text-lg font-semibold text-slate-900 transition hover:text-brand-600">
          <span class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-white">RF</span>
          <span>Recruit Flow</span>
        </RouterLink>
        <nav class="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
          <RouterLink
            to="/"
            :class="[
              'transition hover:text-brand-600',
              activePath === 'careers' || route.path === '/' ? 'text-brand-600' : ''
            ]"
          >
            Careers
          </RouterLink>
          <RouterLink
            to="/candidate/login"
            class="transition hover:text-brand-600"
          >
            Candidate Portal
          </RouterLink>
          <RouterLink
            to="/recruiter/login"
            class="transition hover:text-brand-600"
          >
            Recruiter Console
          </RouterLink>
        </nav>
        <div class="flex items-center gap-3 text-sm">
          <RouterLink
            v-if="auth.isAuthenticated"
            :to="auth.role === 'recruiter' ? '/recruiter/jobs' : '/candidate/dashboard'"
            class="hidden rounded-full bg-brand-600 px-4 py-2 font-semibold text-white shadow-sm transition hover:bg-brand-700 md:inline-flex"
          >
            Go to dashboard
          </RouterLink>
          <RouterLink
            v-else
            to="/candidate/register"
            class="hidden rounded-full bg-brand-600 px-4 py-2 font-semibold text-white shadow-sm transition hover:bg-brand-700 md:inline-flex"
          >
            Join us
          </RouterLink>
          <button
            v-if="auth.isAuthenticated"
            type="button"
            class="text-xs font-medium text-slate-500 underline-offset-2 hover:text-brand-600 hover:underline"
            @click="logout"
          >
            Sign out
          </button>
        </div>
      </div>
      <div class="flex flex-col gap-2 px-6 pb-4 text-sm font-medium text-slate-600 md:hidden">
        <RouterLink to="/" class="rounded-lg bg-slate-100 px-3 py-2" :class="activePath === 'careers' || route.path === '/' ? 'text-brand-600 bg-brand-50' : ''">Careers</RouterLink>
        <RouterLink to="/candidate/login" class="rounded-lg bg-slate-100 px-3 py-2 hover:text-brand-600">Candidate Portal</RouterLink>
        <RouterLink to="/recruiter/login" class="rounded-lg bg-slate-100 px-3 py-2 hover:text-brand-600">Recruiter Console</RouterLink>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
