<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'
import type { User } from '../../stores/auth'

const auth = useAuthStore()
const form = reactive({
  full_name: '',
  phone: '',
  location: '',
  bio: ''
})
const saving = ref(false)
const message = ref('')

const syncForm = () => {
  form.full_name = auth.user?.full_name ?? ''
  form.phone = auth.user?.phone ?? ''
  form.location = auth.user?.location ?? ''
  form.bio = auth.user?.bio ?? ''
}

watch(
  () => auth.user,
  () => syncForm(),
  { immediate: true }
)

onMounted(async () => {
  if (!auth.user) await auth.fetchMe()
})

const submit = async () => {
  saving.value = true
  message.value = ''
  const { data } = await api.patch<User>('/candidate/profile', {
    full_name: form.full_name,
    phone: form.phone,
    location: form.location,
    bio: form.bio
  })
  auth.user = data
  message.value = 'Profile updated'
  saving.value = false
}
</script>

<template>
  <div class="pb-16">
    <section class="bg-slate-900 text-white">
      <div class="mx-auto flex max-w-4xl flex-col gap-4 px-6 py-14">
        <RouterLink to="/candidate/dashboard" class="text-sm text-white/70 transition hover:text-white">← Back to dashboard</RouterLink>
        <h1 class="text-3xl font-semibold">Your profile</h1>
        <p class="max-w-2xl text-sm text-white/80">Keep your job preferences and headline fresh so recruiters understand your strengths at a glance.</p>
      </div>
    </section>

    <section class="-mt-10">
      <div class="mx-auto max-w-4xl px-6">
        <form class="space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-xl" @submit.prevent="submit">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Full name</label>
            <input v-model="form.full_name" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
          </div>
          <div class="grid gap-6 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Phone</label>
              <input v-model="form.phone" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Location</label>
              <input v-model="form.location" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Headline / summary</label>
            <textarea v-model="form.bio" rows="4" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"></textarea>
          </div>
          <div class="flex items-center gap-3">
            <button type="submit" class="rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save changes' }}
            </button>
            <p v-if="message" class="text-sm text-emerald-600">{{ message }}</p>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>
