import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router";
import Layout from "@/components/layout/Layout";
import ErrorBoundary from "@/components/ErrorBoundary";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const PoliticianList = lazy(() => import("@/pages/PoliticianList"));
const PoliticianDetail = lazy(() => import("@/pages/PoliticianDetail"));
const BillList = lazy(() => import("@/pages/BillList"));
const BillDetail = lazy(() => import("@/pages/BillDetail"));
const VoteList = lazy(() => import("@/pages/VoteList"));
const VoteDetail = lazy(() => import("@/pages/VoteDetail"));
const GraphPage = lazy(() => import("@/pages/GraphPage"));

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
              path="/bills"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <BillList />
                </Suspense>
              }
            />
            <Route
              path="/bills/:billId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <BillDetail />
                </Suspense>
              }
            />
            <Route
              path="/votes"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <VoteList />
                </Suspense>
              }
            />
            <Route
              path="/votes/:voteId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <VoteDetail />
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
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
