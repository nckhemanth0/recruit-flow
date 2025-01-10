<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

type Application = {
  id: number
  status: string
  resume_path: string | null
  cover_letter: string | null
  created_at: string
  updated_at: string
  stage: { id: number; name: string; position: number } | null
  job_id: number
  job_title: string
}

const auth = useAuthStore()
const router = useRouter()
const loading = ref(true)
const applications = ref<Application[]>([])

const loadApplications = async () => {
  loading.value = true
  const { data } = await api.get<Application[]>('/candidate/applications')
  applications.value = data
  loading.value = false
}

onMounted(async () => {
  if (!auth.isAuthenticated) {
    await auth.initialize()
  }
  await loadApplications()
})

const goToJob = (id: number) => {
  router.push({ name: 'job-detail', params: { id } })
}

const logout = async () => {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="pb-16">
    <section class="bg-gradient-to-r from-brand-700 via-brand-600 to-brand-700 text-white">
      <div class="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-16 md:flex-row md:items-center md:justify-between">
        <div class="space-y-3">
          <p class="text-xs uppercase tracking-[0.4em] text-white/70">Candidate dashboard</p>
          <h1 class="text-3xl font-semibold md:text-4xl">Welcome back, {{ auth.user?.full_name || auth.user?.email }}</h1>
          <p class="text-sm text-white/80">Track every application, update your profile, and discover new roles tailored to you.</p>
        </div>
        <div class="flex flex-col items-start gap-3 md:items-end">
          <RouterLink to="/candidate/profile" class="rounded-full border border-white/40 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10">
            Update profile
          </RouterLink>
          <button type="button" class="text-xs text-white/70 underline-offset-2 hover:text-white" @click="logout">
            Sign out
          </button>
        </div>
      </div>
    </section>

    <section class="-mt-10">
      <div class="mx-auto max-w-5xl px-6">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Your applications</h2>
              <p class="text-sm text-slate-500">Stay on top of every stage and revisit role details anytime.</p>
            </div>
            <RouterLink to="/" class="inline-flex items-center rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700">
              Browse open roles
            </RouterLink>
          </div>

          <div v-if="loading" class="mt-6 space-y-3">
            <div v-for="n in 3" :key="n" class="h-20 animate-pulse rounded-xl border border-slate-200 bg-slate-50"></div>
          </div>

          <div v-else-if="applications.length === 0" class="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-500">
            You haven’t applied anywhere yet. Explore roles that match your skills and apply in minutes.
          </div>

          <div v-else class="mt-6 space-y-4">
            <div
              v-for="application in applications"
              :key="application.id"
              class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 class="text-lg font-semibold text-slate-900">{{ application.job_title }}</h3>
                  <p class="text-sm text-slate-500">Applied {{ new Date(application.created_at).toLocaleDateString() }}</p>
                  <p v-if="application.stage" class="mt-2 inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-600">
                    {{ application.stage.name }}
                  </p>
                </div>
                <div class="flex flex-col items-start gap-2 text-sm text-slate-500 md:items-end">
                  <button
                    type="button"
                    class="rounded-full border border-brand-500 px-4 py-2 font-semibold text-brand-600 transition hover:bg-brand-50"
                    @click="goToJob(application.job_id)"
                  >
                    View role
                  </button>
                  <a v-if="application.resume_path" :href="application.resume_path" target="_blank" rel="noopener" class="text-xs underline">
                    View resume
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
