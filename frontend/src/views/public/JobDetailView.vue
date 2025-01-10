<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

type JobStage = {
  id: number
  name: string
  position: number
}

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
  stages: JobStage[]
  applications_count: number
}

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const job = ref<Job | null>(null)
const loading = ref(true)
const jobError = ref('')
const fullName = ref('')
const emailField = ref('')
const phoneField = ref('')
const coverLetter = ref('')
const resumeFile = ref<File | null>(null)
const submitting = ref(false)
const autofillLoading = ref(false)
const autofillMessage = ref('')
const successMessage = ref('')
const applyError = ref('')
const hasApplied = ref(false)
const activeTab = ref<'overview' | 'application'>('overview')

const loadJob = async () => {
  loading.value = true
  jobError.value = ''
  try {
    const { data } = await api.get<Job>(`/jobs/${route.params.id}`)
    job.value = data
  } catch (err) {
    jobError.value = 'Job not found'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await auth.initialize()
  if (auth.user) {
    fullName.value = auth.user.full_name ?? ''
    emailField.value = auth.user.email
    phoneField.value = auth.user.phone ?? ''
  }
  await loadJob()
  await loadAppliedStatus()
})

watch(
  () => auth.user,
  async (user) => {
    if (!user) return
    fullName.value = user.full_name ?? ''
    emailField.value = user.email
    phoneField.value = user.phone ?? ''
    await loadAppliedStatus()
  }
)

const loadAppliedStatus = async () => {
  if (!auth.isAuthenticated || auth.role !== 'candidate') {
    hasApplied.value = false
    return
  }
  try {
    const { data } = await api.get<Array<{ job_id: number }>>('/candidate/applications')
    hasApplied.value = data.some((item) => item.job_id === Number(route.params.id))
  } catch {
    hasApplied.value = false
  }
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  resumeFile.value = input.files && input.files[0] ? input.files[0] : null
  autofillMessage.value = ''
}

const autofillFromResume = async () => {
  if (!resumeFile.value) {
    applyError.value = 'Upload a resume to autofill your details.'
    return
  }
  autofillLoading.value = true
  applyError.value = ''
  try {
    const form = new FormData()
    form.append('resume', resumeFile.value)
    const { data } = await api.post<{ full_name?: string | null; email?: string | null; phone?: string | null }>(
      '/candidate/resume/autofill',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    if (data.full_name) fullName.value = data.full_name
    if (data.email) emailField.value = data.email
    if (data.phone) phoneField.value = data.phone
    autofillMessage.value = 'We filled what we could from your resume. Please review before submitting.'
  } catch (err: any) {
    applyError.value = err.response?.data?.detail ?? 'Unable to read resume for autofill.'
  } finally {
    autofillLoading.value = false
  }
}

const apply = async () => {
  if (!job.value) return
  if (!auth.isAuthenticated || auth.role !== 'candidate') {
    router.push({ name: 'candidate-login', query: { redirect: route.fullPath } })
    return
  }
  submitting.value = true
  successMessage.value = ''
  applyError.value = ''
  try {
    await api.patch('/candidate/profile', {
      full_name: fullName.value || null,
      phone: phoneField.value || null,
      location: auth.user?.location || null,
    })
    await auth.fetchMe()
    const form = new FormData()
    form.append('job_id', String(job.value.id))
    if (coverLetter.value) form.append('cover_letter', coverLetter.value)
    if (resumeFile.value) form.append('resume', resumeFile.value)
    await api.post('/candidate/applications', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    successMessage.value = 'Application submitted successfully'
    coverLetter.value = ''
    resumeFile.value = null
    autofillMessage.value = ''
    hasApplied.value = true
  } catch (err: any) {
    applyError.value = err.response?.data?.detail ?? 'Unable to submit application.'
  } finally {
    submitting.value = false
  }
}

const tabClasses = (tab: 'overview' | 'application') =>
  [
    'relative py-3 text-sm font-semibold transition',
    activeTab.value === tab ? 'text-brand-600' : 'text-slate-500 hover:text-brand-500',
  ].join(' ')

const indicatorClasses = (tab: 'overview' | 'application') =>
  activeTab.value === tab ? 'absolute inset-x-0 -bottom-0.5 h-0.5 rounded-full bg-brand-600' : 'hidden'
</script>

<template>
  <div class="pb-16">
    <section class="bg-slate-900 text-white">
      <div class="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-16">
        <RouterLink to="/" class="inline-flex items-center text-sm text-white/70 transition hover:text-white/90">← Back to all roles</RouterLink>
        <div v-if="loading" class="space-y-3">
          <div class="h-10 w-3/4 rounded bg-white/10"></div>
          <div class="h-4 w-1/2 rounded bg-white/10"></div>
        </div>
        <div v-else-if="jobError" class="rounded-xl bg-white/10 p-8 text-center text-white/80">
          {{ jobError }}
        </div>
        <div v-else-if="job" class="max-w-3xl space-y-4">
          <p class="inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white/80">
            {{ job.employment_type }}
          </p>
          <h1 class="text-4xl font-semibold">{{ job.title }}</h1>
          <p class="text-base text-white/80">{{ job.company }} · {{ job.location }}</p>
          <p v-if="job.min_salary" class="text-sm font-medium text-brand-200">
            {{ job.min_salary.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}
            <span v-if="job.max_salary"> – {{ job.max_salary.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}</span>
          </p>
          <p class="text-sm text-white/70">Applicants so far: {{ job.applications_count }}</p>
        </div>
      </div>
    </section>

    <section class="-mt-10 bg-slate-50">
      <div class="mx-auto max-w-5xl px-6 pb-16">
        <nav class="bg-white">
          <div class="flex items-center gap-6 border-b border-slate-200 px-2 text-sm font-semibold">
            <button type="button" :class="tabClasses('overview')" @click="activeTab = 'overview'">
              Overview
              <span :class="indicatorClasses('overview')"></span>
            </button>
            <button type="button" :class="tabClasses('application')" @click="activeTab = 'application'">
              Application
              <span :class="indicatorClasses('application')"></span>
            </button>
          </div>
        </nav>

        <div v-if="activeTab === 'overview'" class="mt-8 space-y-8">
          <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-xl">
            <section class="space-y-8 text-slate-700">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">About the team</h2>
                <p class="mt-3 whitespace-pre-line leading-relaxed">{{ job?.description }}</p>
              </div>
              <div v-if="job?.requirements">
                <h2 class="text-lg font-semibold text-slate-900">What we're looking for</h2>
                <p class="mt-3 whitespace-pre-line leading-relaxed">{{ job.requirements }}</p>
              </div>
            </section>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <h2 class="text-lg font-semibold text-slate-900">Hiring stages</h2>
            <ol class="mt-4 grid gap-3 md:grid-cols-2">
              <li
                v-for="stage in job?.stages ?? []"
                :key="stage.id"
                class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600"
              >
                <span class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-brand-700">{{ stage.position }}</span>
                <span class="font-medium text-slate-800">{{ stage.name }}</span>
              </li>
            </ol>
          </div>
        </div>

        <div v-else class="mt-8 grid gap-8 lg:grid-cols-[1.3fr,1fr]">
          <article class="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs uppercase tracking-wide text-slate-500">Resume match</p>
                  <p class="font-semibold text-slate-900">We’ll surface the top keywords from your resume.</p>
                </div>
                <span class="rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-600">Beta</span>
              </div>
              <p class="mt-3 text-xs text-slate-400">Upload your resume to compare with job requirements.</p>
            </div>
            <div class="space-y-6 text-sm text-slate-600">
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">Role summary</h3>
                <p class="mt-2 whitespace-pre-line">{{ job?.description?.slice(0, 500) }}...</p>
              </div>
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">Team snapshot</h3>
                <ul class="mt-2 grid gap-2 md:grid-cols-2">
                  <li class="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-500">Location: {{ job?.location }}</li>
                  <li class="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-500">Employment: {{ job?.employment_type }}</li>
                  <li class="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-500">Department: {{ job?.department || 'Not specified' }}</li>
                  <li v-if="job?.min_salary" class="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-500">
                    Salary: {{ job?.min_salary?.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}
                    <span v-if="job?.max_salary"> – {{ job?.max_salary?.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </article>

          <aside class="space-y-4">
            <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <h2 class="text-lg font-semibold text-slate-900">Application</h2>
            <p class="mt-2 text-sm text-slate-500">Save time with autofill, update anything that needs tweaking, then submit in seconds.</p>
            <div v-if="auth.isAuthenticated && auth.role === 'candidate'" class="mt-6 space-y-4 text-sm text-slate-600">
              <p v-if="hasApplied" class="rounded-lg bg-emerald-50 px-4 py-2 text-xs font-semibold text-emerald-700">You already applied for this role.</p>
              <div class="grid gap-4 md:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Name</label>
                  <input v-model="fullName" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
                  <input v-model="emailField" type="email" disabled class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-slate-500" />
                </div>
              </div>
              <div>
                <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Phone</label>
                <input v-model="phoneField" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Cover note</label>
                <textarea
                  v-model="coverLetter"
                  rows="5"
                  placeholder="Share a quick introduction (optional)"
                  class="w-full rounded-xl border border-slate-200 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                ></textarea>
              </div>
              <div class="rounded-xl border border-dashed border-slate-300 bg-white p-4">
                <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div class="flex items-center gap-2 text-xs font-medium text-slate-600">
                    <span class="rounded-full bg-brand-100 px-2 py-1 text-brand-600">Autofill from resume</span>
                    <span>Upload and we’ll pre-fill key info</span>
                  </div>
                  <button
                    type="button"
                    class="rounded-full border border-brand-500 px-4 py-2 text-xs font-semibold text-brand-600 hover:bg-brand-50 disabled:opacity-60"
                    :disabled="!resumeFile || autofillLoading"
                    @click="autofillFromResume"
                  >
                    {{ autofillLoading ? 'Reading…' : 'Autofill now' }}
                  </button>
                </div>
                <div class="mt-4 flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
                  <input type="file" accept=".pdf,.doc,.docx,.txt" class="hidden" id="resume-upload" @change="handleFileChange" />
                  <label for="resume-upload" class="cursor-pointer rounded-full bg-white px-4 py-2 text-sm font-semibold text-brand-600 shadow hover:bg-brand-50">
                    Upload file
                  </label>
                  <p>or drag and drop here</p>
                  <p v-if="resumeFile" class="text-xs text-slate-400">Selected: {{ resumeFile.name }}</p>
                </div>
                <p v-if="autofillMessage" class="mt-2 text-xs text-emerald-600">{{ autofillMessage }}</p>
              </div>
              <button
                type="button"
                class="mt-6 w-full rounded-full bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-brand-700 disabled:opacity-60"
                :disabled="submitting || hasApplied"
                @click="apply"
              >
                {{ hasApplied ? 'Application already submitted' : submitting ? 'Submitting…' : 'Submit application' }}
              </button>
              <p v-if="successMessage" class="text-sm text-emerald-600">{{ successMessage }}</p>
              <p v-if="applyError" class="text-sm text-rose-600">{{ applyError }}</p>
            </div>
            <div v-else class="mt-6 space-y-4 text-sm text-slate-600">
              <RouterLink to="/candidate/register" class="block rounded-lg bg-brand-600 px-4 py-2 text-center font-semibold text-white hover:bg-brand-700">
                Create candidate account
              </RouterLink>
              <RouterLink to="/candidate/login" class="block rounded-lg border border-brand-500 px-4 py-2 text-center font-semibold text-brand-600 hover:bg-brand-50">
                Already registered? Log in
              </RouterLink>
              <p v-if="applyError" class="text-sm text-rose-600">{{ applyError }}</p>
            </div>
          </div>
          </aside>
        </div>
      </div>
    </section>
  </div>
</template>
