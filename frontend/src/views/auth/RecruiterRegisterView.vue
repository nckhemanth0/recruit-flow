<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({
  full_name: '',
  email: '',
  password: ''
})
const error = ref('')

const submit = async () => {
  error.value = ''
  try {
    await auth.registerRecruiter({
      email: form.email,
      password: form.password,
      full_name: form.full_name
    })
    router.push({ name: 'recruiter-jobs' })
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Unable to register recruiter account'
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-100 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow">
      <h1 class="text-2xl font-semibold text-slate-900">Set up recruiter access</h1>
      <p class="mt-2 text-sm text-slate-500">Create a team account to post jobs and review applicants.</p>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Full name</label>
          <input v-model="form.full_name" type="text" required class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Work email</label>
          <input v-model="form.email" type="email" required class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Password</label>
          <input v-model="form.password" type="password" required class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
        </div>
        <button type="submit" class="w-full rounded-lg bg-brand-600 px-4 py-2 text-white hover:bg-brand-700 disabled:opacity-60" :disabled="auth.loading">
          {{ auth.loading ? 'Creating account...' : 'Create recruiter account' }}
        </button>
        <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
      </form>
      <p class="mt-6 text-sm text-slate-500">Already have access? <RouterLink to="/recruiter/login" class="text-brand-600 hover:underline">Log in</RouterLink></p>
    </div>
  </div>
</template>
