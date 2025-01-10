<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({
  full_name: '',
  email: '',
  password: '',
  phone: '',
  location: ''
})
const error = ref('')

const submit = async () => {
  error.value = ''
  try {
    await auth.registerCandidate({
      email: form.email,
      password: form.password,
      full_name: form.full_name,
      phone: form.phone,
      location: form.location
    })
    router.push({ name: 'candidate-dashboard' })
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Unable to register'
  }
}
</script>

<template>
  <div class="bg-slate-50">
    <div class="mx-auto flex min-h-[calc(100vh-80px)] max-w-5xl flex-col-reverse items-center gap-12 px-6 py-16 lg:flex-row lg:items-start">
      <div class="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-xl sm:max-w-lg">
        <h1 class="text-2xl font-semibold text-slate-900">Create your candidate profile</h1>
        <p class="mt-2 text-sm text-slate-500">Keep your details in one place and get transparent updates every step of the way.</p>
        <form class="mt-6 space-y-5" @submit.prevent="submit">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Full name</label>
            <input v-model="form.full_name" type="text" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input v-model="form.email" type="email" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Password</label>
            <input v-model="form.password" type="password" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Phone (optional)</label>
              <input v-model="form.phone" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Location (optional)</label>
              <input v-model="form.location" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
            </div>
          </div>
          <button type="submit" class="w-full rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60" :disabled="auth.loading">
            {{ auth.loading ? 'Creating account...' : 'Create account' }}
          </button>
          <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
        </form>
        <div class="mt-6 space-y-2 text-sm text-slate-500">
          <p>Already registered? <RouterLink to="/candidate/login" class="text-brand-600 hover:underline">Log in</RouterLink></p>
          <p>Recruiter? <RouterLink to="/recruiter/register" class="text-brand-600 hover:underline">Request recruiter access</RouterLink></p>
        </div>
      </div>

      <div class="w-full max-w-2xl rounded-3xl bg-white/60 p-8 shadow-inner backdrop-blur lg:sticky lg:top-28">
        <h2 class="text-xl font-semibold text-slate-900">What candidates gain</h2>
        <ul class="mt-4 space-y-4 text-sm text-slate-600">
          <li class="flex gap-3">
            <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
            Personalized dashboard to track applications and status updates in real time.
          </li>
          <li class="flex gap-3">
            <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
            Single profile used across every role you apply to at Recruit Flow partner companies.
          </li>
          <li class="flex gap-3">
            <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
            Quick re-apply experience with stored resumes, contact information, and preferences.
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
