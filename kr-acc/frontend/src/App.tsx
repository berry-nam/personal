import { BrowserRouter, Routes, Route } from "react-router";

function Landing() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">kr-acc</h1>
        <p className="mt-2 text-lg text-gray-600">국회의원 활동 그래프</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
      </Routes>
    </BrowserRouter>
  );
}
