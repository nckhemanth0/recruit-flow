<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

type Job = {
  id: number
  title: string
  company: string
  location: string
  department: string | null
  employment_type: string
  status: string
  description: string
  requirements: string | null
  min_salary: number | null
  max_salary: number | null
  created_at: string
}

const router = useRouter()
const auth = useAuthStore()

const jobs = ref<Job[]>([])
const loading = ref(true)
const search = ref('')
const appliedJobIds = ref<Set<number>>(new Set())

const loadJobs = async () => {
  loading.value = true
  try {
    const { data } = await api.get<Job[]>('/jobs')
    jobs.value = data
  } finally {
    loading.value = false
  }
}

const loadAppliedJobs = async () => {
  if (!auth.isAuthenticated || auth.role !== 'candidate') {
    appliedJobIds.value = new Set()
    return
  }
  try {
    const { data } = await api.get<Array<{ job_id: number }>>('/candidate/applications')
    appliedJobIds.value = new Set(data.map((item) => item.job_id))
  } catch {
    appliedJobIds.value = new Set()
  }
}

onMounted(async () => {
  await loadJobs()
  await loadAppliedJobs()
})

watch(
  () => auth.user,
  async () => {
    await loadAppliedJobs()
  }
)

const filteredJobs = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return jobs.value
  return jobs.value.filter((job) =>
    [job.title, job.company, job.location, job.department].some((field) =>
      (field ?? '').toLowerCase().includes(term)
    )
  )
})

const goToJob = (id: number) => {
  router.push({ name: 'job-detail', params: { id } })
}

const isApplied = (id: number) => appliedJobIds.value.has(id)
</script>

<template>
  <div class="pb-16">
    <section class="bg-gradient-to-r from-brand-600 via-brand-500 to-brand-600 text-white">
      <div class="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-20 md:flex-row md:items-center md:justify-between">
        <div class="max-w-2xl space-y-4">
          <p class="text-xs uppercase tracking-[0.4em] text-white/80">Recruit Flow Careers</p>
          <h1 class="text-4xl font-semibold md:text-5xl">Build the teams that ship tomorrow</h1>
          <p class="text-white/80">
            Explore opportunities across product, engineering, operations, and more. Join a culture focused on craft, empathy,
            and delivering candidate-first experiences.
          </p>
        </div>
        <div class="w-full max-w-sm rounded-2xl bg-white/10 p-6 backdrop-blur md:self-start">
          <h2 class="text-lg font-semibold">Why Recruit Flow</h2>
          <ul class="mt-3 space-y-2 text-sm text-white/80">
            <li>• Modern tools and flexible work</li>
            <li>• Transparent hiring process</li>
            <li>• Purpose-driven teams</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="-mt-16">
      <div class="mx-auto max-w-6xl px-6">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="flex-1">
              <label class="sr-only" for="search-jobs">Search jobs</label>
              <input
                id="search-jobs"
                v-model="search"
                type="search"
                placeholder="Search by title, team, or location"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
              />
            </div>
            <p class="text-sm text-slate-500">Open roles: {{ jobs.length }}</p>
          </div>

          <div v-if="loading" class="mt-8 grid gap-4 md:grid-cols-2">
            <div v-for="n in 4" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-slate-50 p-6">
              <div class="mb-4 h-4 w-1/2 rounded bg-slate-200"></div>
              <div class="mb-2 h-3 w-1/3 rounded bg-slate-200"></div>
              <div class="h-16 rounded bg-slate-100"></div>
            </div>
          </div>

          <div v-else class="mt-8">
            <p v-if="filteredJobs.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-500">
              No openings match your search right now. Follow us to hear about new opportunities as soon as they land.
            </p>
            <div v-else class="grid gap-5 md:grid-cols-2">
              <article
                v-for="job in filteredJobs"
                :key="job.id"
                class="flex h-full flex-col justify-between rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
              >
                <div class="space-y-4">
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-600">
                      {{ job.employment_type }}
                    </span>
                    <span
                      v-if="isApplied(job.id)"
                      class="inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
                    >
                      Applied
                    </span>
                  </div>
                  <div>
                    <h2 class="text-xl font-semibold text-slate-900">{{ job.title }}</h2>
                    <p class="mt-1 text-sm text-slate-600">{{ job.company }} · {{ job.location }}</p>
                  </div>
                  <p class="text-sm text-slate-500">
                    {{ job.description.length > 200 ? job.description.slice(0, 200) + '…' : job.description }}
                  </p>
                  <p v-if="job.min_salary" class="text-sm font-medium text-slate-700">
                    {{ job.min_salary.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}
                    <span v-if="job.max_salary"> – {{ job.max_salary.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}</span>
                  </p>
                </div>
                <button
                  type="button"
                  class="mt-6 w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700"
                  @click="goToJob(job.id)"
                >
                  View details
                </button>
              </article>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
