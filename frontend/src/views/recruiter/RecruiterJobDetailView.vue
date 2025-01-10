<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

type Stage = {
  id: number
  name: string
  position: number
}

type Note = {
  id: number
  body: string
  created_at: string
  author_id: number | null
  author_name: string | null
}

type Candidate = {
  id: number
  email: string
  full_name: string | null
  role: string
  phone: string | null
  location: string | null
  bio: string | null
  created_at: string
}

type Application = {
  id: number
  status: string
  resume_path: string | null
  cover_letter: string | null
  created_at: string
  updated_at: string
  stage: Stage | null
  job_id: number
  job_title: string
  candidate: Candidate
  notes: Note[]
}

type JobDetailResponse = {
  job: {
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
    stages: Stage[]
    applications_count: number
  }
  applications: Application[]
}

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const detail = ref<JobDetailResponse | null>(null)
const loading = ref(true)
const error = ref('')
const noteDrafts = reactive<Record<number, string>>({})

const loadDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<JobDetailResponse>(`/recruiter/jobs/${route.params.id}`)
    detail.value = data
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Unable to load job'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!auth.isAuthenticated) await auth.initialize()
  await loadDetail()
})

const stages = computed(() => detail.value?.job.stages ?? [])

const applicationsByStage = computed(() => {
  if (!detail.value) return []
  return stages.value.map((stage) => ({
    stage,
    items: detail.value?.applications.filter((app) => app.stage?.id === stage.id) ?? []
  }))
})

const moveApplication = async (application: Application, stageId: number) => {
  if (!detail.value) return
  await api.post(`/recruiter/applications/${application.id}/move`, { stage_id: stageId })
  await loadDetail()
}

const addNote = async (application: Application) => {
  const body = noteDrafts[application.id]?.trim()
  if (!body) return
  await api.post(`/recruiter/applications/${application.id}/notes`, { body })
  noteDrafts[application.id] = ''
  await loadDetail()
}

const goBack = () => router.push({ name: 'recruiter-jobs' })

const getResumeUrl = (resumePath: string): string => {
  if (resumePath.startsWith('http://') || resumePath.startsWith('https://')) {
    return resumePath
  }
  const backendUrl = import.meta.env.VITE_API_URL?.replace('/api/v1', '') ?? 'http://localhost:8000'
  return `${backendUrl}${resumePath.startsWith('/') ? resumePath : '/' + resumePath}`
}
</script>

<template>
  <div class="pb-16">
    <section class="bg-slate-900 text-white">
      <div class="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-16 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-xs uppercase tracking-[0.4em] text-white/70">Recruiter console</p>
          <h1 v-if="detail" class="text-3xl font-semibold md:text-4xl">{{ detail.job.title }}</h1>
          <p v-if="detail" class="mt-2 text-sm text-white/80">{{ detail.job.company }} · {{ detail.job.location }} · {{ detail.job.employment_type }}</p>
        </div>
        <button type="button" @click="goBack" class="text-sm text-white/80 underline-offset-2 hover:text-white">← Back to job list</button>
      </div>
    </section>

    <section class="-mt-12">
      <div class="mx-auto max-w-6xl space-y-8 px-6">
        <div v-if="loading" class="space-y-4">
          <div class="h-6 w-1/2 rounded-2xl border border-slate-200 bg-white shadow"></div>
          <div class="h-24 rounded-2xl border border-slate-200 bg-white shadow"></div>
        </div>

        <div v-else-if="error" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-12 text-center text-slate-500">
          {{ error }}
        </div>

        <div v-else-if="detail" class="space-y-8">
          <article class="rounded-2xl border border-slate-200 bg-white p-8 shadow-xl">
            <h2 class="text-lg font-semibold text-slate-900">Role overview</h2>
            <p class="mt-2 text-sm text-slate-600">Applicants: {{ detail.applications.length }}</p>
            <p class="mt-4 whitespace-pre-line text-sm text-slate-600">{{ detail.job.description }}</p>
            <div v-if="detail.job.requirements" class="mt-6 rounded-xl bg-slate-50 p-5">
              <h3 class="text-sm font-semibold text-slate-800">Requirements</h3>
              <p class="mt-2 whitespace-pre-line text-sm text-slate-600">{{ detail.job.requirements }}</p>
            </div>
          </article>

          <section class="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <h2 class="text-lg font-semibold text-slate-900">Pipeline</h2>
              <p class="text-sm text-slate-500">Drag-free stage changes keep things simple. Use notes to align with interviewers.</p>
            </div>
            <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              <div
                v-for="stageBlock in applicationsByStage"
                :key="stageBlock.stage.id"
                class="flex h-full flex-col rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <header class="flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-slate-700">{{ stageBlock.stage.name }}</h3>
                  <span class="text-xs text-slate-400">{{ stageBlock.items.length }} candidates</span>
                </header>
                <div class="mt-4 space-y-4">
                  <p v-if="stageBlock.items.length === 0" class="rounded-lg border border-dashed border-slate-200 bg-white p-4 text-sm text-slate-500">
                    No candidates in this stage yet.
                  </p>
                  <article
                    v-for="application in stageBlock.items"
                    :key="application.id"
                    class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div class="flex items-start justify-between gap-3">
                      <div>
                        <h4 class="text-sm font-semibold text-slate-900">{{ application.candidate.full_name || application.candidate.email }}</h4>
                        <p class="text-xs text-slate-500">Applied {{ new Date(application.created_at).toLocaleDateString() }}</p>
                      </div>
                      <a
                        v-if="application.resume_path"
                        :href="getResumeUrl(application.resume_path)"
                        target="_blank"
                        rel="noopener"
                        class="text-xs font-semibold text-brand-600"
                      >
                        Resume
                      </a>
                    </div>
                    <div class="mt-3">
                      <label class="text-xs font-medium text-slate-500">Move to stage</label>
                      <select
                        class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                        :value="application.stage?.id"
                        @change="(event) => moveApplication(application, Number((event.target as HTMLSelectElement).value))"
                      >
                        <option v-for="stage in stages" :key="stage.id" :value="stage.id">{{ stage.name }}</option>
                      </select>
                    </div>
                    <div class="mt-3 space-y-2 text-xs text-slate-500">
                      <div
                        v-for="note in application.notes"
                        :key="note.id"
                        class="rounded-lg border border-slate-200 bg-slate-50 p-3"
                      >
                        <p>{{ note.body }}</p>
                        <span class="mt-1 block text-[10px] text-slate-400">{{ note.author_name || 'System' }} · {{ new Date(note.created_at).toLocaleString() }}</span>
                      </div>
                    </div>
                    <div class="mt-3 space-y-2">
                      <textarea
                        v-model="noteDrafts[application.id]"
                        rows="2"
                        placeholder="Add internal note"
                        class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                      ></textarea>
                      <button type="button" class="rounded-full bg-brand-600 px-3 py-2 text-xs font-semibold text-white hover:bg-brand-700" @click="addNote(application)">
                        Add note
                      </button>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  </div>
</template>
