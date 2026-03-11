import { BrowserRouter, Routes, Route } from "react-router";
import Layout from "@/components/layout/Layout";
import Dashboard from "@/pages/Dashboard";
import PoliticianList from "@/pages/PoliticianList";
import PoliticianDetail from "@/pages/PoliticianDetail";
import BillList from "@/pages/BillList";
import BillDetail from "@/pages/BillDetail";
import VoteList from "@/pages/VoteList";
import VoteDetail from "@/pages/VoteDetail";
import GraphPage from "@/pages/GraphPage";
import NotFound from "@/pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/politicians" element={<PoliticianList />} />
          <Route path="/politicians/:id" element={<PoliticianDetail />} />
          <Route path="/bills" element={<BillList />} />
          <Route path="/bills/:billId" element={<BillDetail />} />
          <Route path="/votes" element={<VoteList />} />
          <Route path="/votes/:voteId" element={<VoteDetail />} />
          <Route path="/graph" element={<GraphPage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
