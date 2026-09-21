import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import RepoDetail from "./pages/RepoDetail.jsx";
import PRReview from "./pages/PRReview.jsx";
import RunHistory from "./pages/RunHistory.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 px-8 py-7 max-w-6xl">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/repos/:repoId" element={<RepoDetail />} />
          <Route path="/prs/:prId" element={<RunHistory />} />
          <Route path="/runs/:runId" element={<PRReview />} />
        </Routes>
      </main>
    </div>
  );
}
