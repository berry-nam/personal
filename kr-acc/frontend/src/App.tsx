import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import Layout from "@/components/layout/Layout";
import ErrorBoundary from "@/components/ErrorBoundary";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const PoliticianList = lazy(() => import("@/pages/PoliticianList"));
const PoliticianDetail = lazy(() => import("@/pages/PoliticianDetail"));
const LegislationPage = lazy(() => import("@/pages/LegislationPage"));
const BillDetail = lazy(() => import("@/pages/BillDetail"));
const VoteDetail = lazy(() => import("@/pages/VoteDetail"));
const AssetsOverview = lazy(() => import("@/pages/AssetsOverview"));
const GraphPage = lazy(() => import("@/pages/GraphPage"));

// Labeling tool (separate route tree)
const LabelingLayout = lazy(() => import("@/components/labeling/LabelingLayout"));
const LabelingLogin = lazy(() => import("@/pages/labeling/LabelingLogin"));
const LabelingDashboard = lazy(() => import("@/pages/labeling/LabelingDashboard"));
const LabelingWorkspace = lazy(() => import("@/pages/labeling/LabelingWorkspace"));

function LoadingSpinner() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-900" />
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route
              path="/"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <Dashboard />
                </Suspense>
              }
            />
            <Route
              path="/politicians"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <PoliticianList />
                </Suspense>
              }
            />
            <Route
              path="/politicians/:id"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <PoliticianDetail />
                </Suspense>
              }
            />
            <Route
              path="/legislation"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <LegislationPage />
                </Suspense>
              }
            />
            <Route
              path="/legislation/bills/:billId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <BillDetail />
                </Suspense>
              }
            />
            <Route
              path="/legislation/votes/:voteId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <VoteDetail />
                </Suspense>
              }
            />
            <Route
              path="/assets"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <AssetsOverview />
                </Suspense>
              }
            />
            <Route
              path="/graph"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <GraphPage />
                </Suspense>
              }
            />
            {/* Redirects for old routes */}
            <Route path="/bills" element={<Navigate to="/legislation" replace />} />
            <Route path="/bills/:billId" element={<Navigate to="/legislation" replace />} />
            <Route path="/votes" element={<Navigate to="/legislation?tab=votes" replace />} />
            <Route path="/votes/:voteId" element={<Navigate to="/legislation" replace />} />
          </Route>

          {/* Labeling tool — separate route tree with own layout */}
          <Route
            path="/labeling/login"
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LabelingLogin />
              </Suspense>
            }
          />
          <Route
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LabelingLayout />
              </Suspense>
            }
          >
            <Route
              path="/labeling"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <LabelingDashboard />
                </Suspense>
              }
            />
            <Route
              path="/labeling/tasks/:taskId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <LabelingWorkspace />
                </Suspense>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
