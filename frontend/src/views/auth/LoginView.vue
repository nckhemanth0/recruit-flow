<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const form = reactive({ email: '', password: '' })
const error = ref('')
const role = computed(() => (route.meta.role as string) || 'candidate')
const title = computed(() => (role.value === 'recruiter' ? 'Recruiter sign in' : 'Candidate sign in'))
const subtitle = computed(() =>
  role.value === 'recruiter' ? 'Manage job postings and review applicants.' : 'Track your applications and manage your profile.'
)

const submit = async () => {
  error.value = ''
  try {
    await auth.login(form.email, form.password)
    if (auth.role !== role.value) {
      error.value = 'Account does not have access to this portal'
      await auth.logout()
      return
    }
    const redirect = (route.query.redirect as string) || (role.value === 'recruiter' ? '/recruiter/jobs' : '/candidate/dashboard')
    router.push(redirect)
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Unable to log in'
  }
}
</script>

<template>
  <div class="bg-slate-50">
    <div class="mx-auto flex min-h-[calc(100vh-80px)] max-w-5xl flex-col items-center gap-12 px-6 py-16 lg:flex-row lg:items-start">
      <div class="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-xl sm:max-w-md">
        <h1 class="text-2xl font-semibold text-slate-900">{{ title }}</h1>
        <p class="mt-2 text-sm text-slate-500">{{ subtitle }}</p>
        <form class="mt-6 space-y-5" @submit.prevent="submit">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input v-model="form.email" type="email" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Password</label>
            <input v-model="form.password" type="password" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <button type="submit" class="w-full rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60" :disabled="auth.loading">
            {{ auth.loading ? 'Signing in...' : 'Sign in' }}
          </button>
          <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
        </form>
        <div v-if="role === 'candidate'" class="mt-6 text-sm text-slate-500">
          New here? <RouterLink to="/candidate/register" class="text-brand-600 hover:underline">Create a candidate account</RouterLink>
        </div>
        <div v-else class="mt-6 space-y-2 text-sm text-slate-500">
          <p>Candidate looking to apply? <RouterLink to="/candidate/login" class="text-brand-600 hover:underline">Access candidate portal</RouterLink></p>
          <p>Need recruiter access? <RouterLink to="/recruiter/register" class="text-brand-600 hover:underline">Create an account</RouterLink></p>
        </div>
      </div>

      <div class="w-full max-w-2xl rounded-3xl bg-white/60 p-8 shadow-inner backdrop-blur">
        <h2 class="text-xl font-semibold text-slate-900">A better way to hire and get hired</h2>
        <div class="mt-4 grid gap-4 lg:grid-cols-2">
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 class="text-sm font-semibold text-slate-800">For candidates</h3>
            <p class="mt-2 text-sm text-slate-600">Follow applications in real time, reuse your profile, and receive thoughtful updates.</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 class="text-sm font-semibold text-slate-800">For recruiters</h3>
            <p class="mt-2 text-sm text-slate-600">Launch roles in minutes, manage pipelines, and collaborate with hiring managers.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
