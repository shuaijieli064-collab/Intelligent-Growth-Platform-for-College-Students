import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { PageLoader } from '@/components/ui/PageLoader'
import { RequireAuth } from '@/components/RequireAuth'

const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const DataEntryPage = lazy(() => import('@/pages/DataEntryPage'))
const DigitalTwinPage = lazy(() => import('@/pages/DigitalTwinPage'))
const GradePredictPage = lazy(() => import('@/pages/GradePredictPage'))
const KnowledgeGraphPage = lazy(() => import('@/pages/KnowledgeGraphPage'))
const AICoachPage = lazy(() => import('@/pages/AICoachPage'))
const RiskWarningPage = lazy(() => import('@/pages/RiskWarningPage'))
const StudyPlanPage = lazy(() => import('@/pages/StudyPlanPage'))
const ResourcePage = lazy(() => import('@/pages/ResourcePage'))
const FocusMonitorPage = lazy(() => import('@/pages/FocusMonitorPage'))
const GrowthArchivePage = lazy(() => import('@/pages/GrowthArchivePage'))
const VisualizationPage = lazy(() => import('@/pages/VisualizationPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))

const withSuspense = (element: React.ReactNode) => (
  <Suspense fallback={<PageLoader />}>{element}</Suspense>
)

export const router = createBrowserRouter([
  {
    path: '/login',
    element: withSuspense(<LoginPage />),
  },
  {
    path: '/register',
    element: withSuspense(<RegisterPage />),
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'data-entry',
        element: withSuspense(<DataEntryPage />),
      },
      {
        path: 'dashboard',
        element: withSuspense(<DashboardPage />),
      },
      {
        path: 'digital-twin',
        element: withSuspense(<DigitalTwinPage />),
      },
      {
        path: 'grade-predict',
        element: withSuspense(<GradePredictPage />),
      },
      {
        path: 'knowledge-graph',
        element: withSuspense(<KnowledgeGraphPage />),
      },
      {
        path: 'ai-coach',
        element: withSuspense(<AICoachPage />),
      },
      {
        path: 'risk-warning',
        element: withSuspense(<RiskWarningPage />),
      },
      {
        path: 'study-plan',
        element: withSuspense(<StudyPlanPage />),
      },
      {
        path: 'resource',
        element: withSuspense(<ResourcePage />),
      },
      {
        path: 'focus-monitor',
        element: withSuspense(<FocusMonitorPage />),
      },
      {
        path: 'growth-archive',
        element: withSuspense(<GrowthArchivePage />),
      },
      {
        path: 'visualization',
        element: withSuspense(<VisualizationPage />),
      },
      {
        path: 'settings',
        element: withSuspense(<SettingsPage />),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
])
