import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const CareersList = () => import('../views/public/CareersListView.vue')
const JobDetail = () => import('../views/public/JobDetailView.vue')
const CandidateRegister = () => import('../views/auth/CandidateRegisterView.vue')
const LoginView = () => import('../views/auth/LoginView.vue')
const RecruiterRegister = () => import('../views/auth/RecruiterRegisterView.vue')
const CandidateDashboard = () => import('../views/candidate/CandidateDashboardView.vue')
const CandidateProfile = () => import('../views/candidate/CandidateProfileView.vue')
const RecruiterJobs = () => import('../views/recruiter/RecruiterJobsView.vue')
const RecruiterJobDetail = () => import('../views/recruiter/RecruiterJobDetailView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'careers', component: CareersList },
    { path: '/jobs/:id', name: 'job-detail', component: JobDetail },
    { path: '/candidate/register', name: 'candidate-register', component: CandidateRegister, meta: { authPage: true } },
    { path: '/candidate/login', name: 'candidate-login', component: LoginView, meta: { authPage: true, role: 'candidate' } },
    { path: '/candidate/dashboard', name: 'candidate-dashboard', component: CandidateDashboard, meta: { requiresAuth: true, role: 'candidate' } },
    { path: '/candidate/profile', name: 'candidate-profile', component: CandidateProfile, meta: { requiresAuth: true, role: 'candidate' } },
    { path: '/recruiter/login', name: 'recruiter-login', component: LoginView, meta: { authPage: true, role: 'recruiter' } },
    { path: '/recruiter/register', name: 'recruiter-register', component: RecruiterRegister, meta: { authPage: true } },
    { path: '/recruiter/jobs', name: 'recruiter-jobs', component: RecruiterJobs, meta: { requiresAuth: true, role: 'recruiter' } },
    { path: '/recruiter/jobs/:id', name: 'recruiter-job-detail', component: RecruiterJobDetail, meta: { requiresAuth: true, role: 'recruiter' } },
  ]
})

const candidateHome = '/candidate/dashboard'
const recruiterHome = '/recruiter/jobs'

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user && auth.token) {
    await auth.fetchMe()
  }
  const requiresAuth = Boolean(to.meta.requiresAuth)
  const requiredRole = to.meta.role as string | undefined
  const isAuthPage = Boolean(to.meta.authPage)

  if (requiresAuth && !auth.isAuthenticated) {
    if (requiredRole === 'recruiter') return '/recruiter/login'
    return '/candidate/login'
  }

  if (requiredRole && auth.isAuthenticated && auth.role !== requiredRole) {
    return auth.role === 'recruiter' ? recruiterHome : candidateHome
  }

  if (isAuthPage && auth.isAuthenticated) {
    return auth.role === 'recruiter' ? recruiterHome : candidateHome
  }

  return true
})

export default router
