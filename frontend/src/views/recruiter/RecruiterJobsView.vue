<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
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
  min_salary: number | null
  max_salary: number | null
  created_at: string
  applications_count: number
}

const auth = useAuthStore()
const router = useRouter()
const jobs = ref<Job[]>([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const form = reactive({
  title: '',
  company: '',
  location: '',
  department: '',
  employment_type: 'Full-time',
  status: 'open',
  description: '',
  requirements: '',
  min_salary: '',
  max_salary: '',
  stages: 'Applied\nScreening\nInterview\nOffer\nHired'
})
const saving = ref(false)

const fetchJobs = async () => {
  loading.value = true
  const { data } = await api.get<Job[]>('/recruiter/jobs')
  jobs.value = data
  loading.value = false
}

onMounted(async () => {
  if (!auth.isAuthenticated) await auth.initialize()
  await fetchJobs()
})

const createJob = async () => {
  saving.value = true
  error.value = ''
  try {
    const stageNames = form.stages
      .split(/[\n,]/)
      .map((name) => name.trim())
      .filter(Boolean)
    const payload = {
      title: form.title,
      company: form.company,
      location: form.location,
      department: form.department || null,
      employment_type: form.employment_type,
      status: form.status,
      description: form.description,
      requirements: form.requirements || null,
      min_salary: form.min_salary ? Number(form.min_salary) : null,
      max_salary: form.max_salary ? Number(form.max_salary) : null,
      stage_names: stageNames
    }
    const { data } = await api.post<Job>('/recruiter/jobs', payload)
    showForm.value = false
    Object.assign(form, {
      title: '',
      company: '',
      location: '',
      department: '',
      employment_type: 'Full-time',
      status: 'open',
      description: '',
      requirements: '',
      min_salary: '',
      max_salary: '',
      stages: 'Applied\nScreening\nInterview\nOffer\nHired'
    })
    await fetchJobs()
    router.push({ name: 'recruiter-job-detail', params: { id: data.id } })
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Unable to create job'
  } finally {
    saving.value = false
  }
}

const goToJob = (id: number) => router.push({ name: 'recruiter-job-detail', params: { id } })

const logout = async () => {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="pb-16">
    <section class="bg-slate-900 text-white">
      <div class="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-16 md:flex-row md:items-center md:justify-between">
        <div class="space-y-3">
          <p class="text-xs uppercase tracking-[0.4em] text-white/70">Recruiter console</p>
          <h1 class="text-3xl font-semibold md:text-4xl">Welcome back, {{ auth.user?.full_name || auth.user?.email }}</h1>
          <p class="max-w-xl text-sm text-white/80">Launch roles in minutes, collaborate with hiring managers, and deliver standout candidate journeys.</p>
        </div>
        <div class="flex flex-col items-start gap-3 text-sm text-white/80 md:items-end">
          <RouterLink to="/" class="rounded-full border border-white/40 px-4 py-2 font-semibold transition hover:bg-white/10">View careers site</RouterLink>
          <button type="button" class="text-xs underline-offset-2 hover:text-white" @click="logout">Sign out</button>
        </div>
      </div>
    </section>

    <section class="-mt-12">
      <div class="mx-auto max-w-6xl px-6">
        <div class="space-y-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Open roles</h2>
              <p class="text-sm text-slate-500">You currently have {{ jobs.length }} live posting{{ jobs.length === 1 ? '' : 's' }}.</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700"
              @click="showForm = !showForm"
            >
              {{ showForm ? 'Close form' : 'Post a new job' }}
            </button>
          </div>

          <div v-if="showForm" class="rounded-2xl border border-slate-200 bg-slate-50 p-6">
            <form class="grid gap-4 md:grid-cols-2" @submit.prevent="createJob">
              <div class="md:col-span-2">
                <label class="mb-1 block text-sm font-medium text-slate-700">Job title</label>
                <input v-model="form.title" type="text" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Company</label>
                <input v-model="form.company" type="text" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Location</label>
                <input v-model="form.location" type="text" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Department</label>
                <input v-model="form.department" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Employment type</label>
                <select v-model="form.employment_type" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200">
                  <option>Full-time</option>
                  <option>Part-time</option>
                  <option>Contract</option>
                  <option>Internship</option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label class="mb-1 block text-sm font-medium text-slate-700">Description</label>
                <textarea v-model="form.description" rows="4" required class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"></textarea>
              </div>
              <div class="md:col-span-2">
                <label class="mb-1 block text-sm font-medium text-slate-700">Requirements</label>
                <textarea v-model="form.requirements" rows="3" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"></textarea>
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Min salary</label>
                <input v-model="form.min_salary" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Max salary</label>
                <input v-model="form.max_salary" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div class="md:col-span-2">
                <label class="mb-1 block text-sm font-medium text-slate-700">Pipeline stages (one per line)</label>
                <textarea v-model="form.stages" rows="3" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"></textarea>
              </div>
              <div class="md:col-span-2 flex items-center gap-3">
                <button type="submit" class="rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60" :disabled="saving">
                  {{ saving ? 'Publishing...' : 'Publish job' }}
                </button>
                <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
              </div>
            </form>
          </div>

          <div>
            <div v-if="loading" class="space-y-3">
              <div v-for="n in 4" :key="n" class="h-20 animate-pulse rounded-xl border border-slate-200 bg-slate-50"></div>
            </div>
            <div v-else-if="jobs.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-500">
              No jobs posted yet. Use the button above to create your first role and start collecting applications.
            </div>
            <div v-else class="grid gap-4">
              <article
                v-for="job in jobs"
                :key="job.id"
                class="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <h3 class="text-lg font-semibold text-slate-900">{{ job.title }}</h3>
                  <p class="text-sm text-slate-500">{{ job.location }} · {{ job.employment_type }}</p>
                  <p class="text-xs text-slate-400">Posted {{ new Date(job.created_at).toLocaleDateString() }}</p>
                </div>
                <div class="flex flex-col items-start gap-2 text-right text-sm text-slate-600 md:items-end">
                  <span>{{ job.applications_count }} applicants</span>
                  <button type="button" class="rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700" @click="goToJob(job.id)">
                    View pipeline
                  </button>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
