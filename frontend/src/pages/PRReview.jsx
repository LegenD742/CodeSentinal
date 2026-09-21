import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getReviewRun } from "../api/client.js";
import RiskBadge from "../components/RiskBadge.jsx";
import FindingCard from "../components/FindingCard.jsx";
import AgentTimeline from "../components/AgentTimeline.jsx";

const CATEGORIES = ["all", "bug", "security", "performance", "quality"];

export default function PRReview() {
  const { runId } = useParams();
  const [run, setRun] = useState(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReviewRun(runId)
      .then(setRun)
      .catch(() => setRun(null))
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading) return <p className="text-sm text-ink/40">Loading…</p>;
  if (!run) return <p className="text-sm text-ink/40">Review run not found.</p>;

  const findings = filter === "all" ? run.findings : run.findings.filter((f) => f.category === filter);

  return (
    <div>
      <header className="mb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold tracking-tight">Review run</h1>
          {run.risk_level && <RiskBadge level={run.risk_level} score={run.risk_score} />}
        </div>
        <div className="mt-3">
          <AgentTimeline status={run.status} />
        </div>
        {run.summary && <p className="mt-4 text-sm text-ink/70 leading-relaxed max-w-2xl">{run.summary}</p>}
      </header>

      <div className="flex items-center gap-1.5 mb-4 border-b border-line pb-3">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              filter === c ? "bg-ink text-white" : "text-ink/50 hover:bg-paper"
            }`}
          >
            {c}
            {c !== "all" && (
              <span className="ml-1.5 text-ink/40">
                {run.findings.filter((f) => f.category === c).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {findings.length === 0 ? (
        <div className="rounded-lg border border-dashed border-line p-8 text-center text-sm text-ink/50">
          No findings in this category.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {findings.map((f) => (
            <FindingCard key={f.id} finding={f} />
          ))}
        </div>
      )}
    </div>
  );
}
