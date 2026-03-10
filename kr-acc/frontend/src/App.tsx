import { BrowserRouter, Routes, Route } from "react-router";
import Layout from "@/components/layout/Layout";
import Dashboard from "@/pages/Dashboard";
import PoliticianList from "@/pages/PoliticianList";
import PoliticianDetail from "@/pages/PoliticianDetail";
import BillList from "@/pages/BillList";
import VoteList from "@/pages/VoteList";
import GraphPage from "@/pages/GraphPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/politicians" element={<PoliticianList />} />
          <Route path="/politicians/:id" element={<PoliticianDetail />} />
          <Route path="/bills" element={<BillList />} />
          <Route path="/bills/:billId" element={<BillList />} />
          <Route path="/votes" element={<VoteList />} />
          <Route path="/graph" element={<GraphPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
