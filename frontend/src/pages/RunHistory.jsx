import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { listReviewRuns, getPullRequest, rerunReview } from "../api/client.js";
import RiskBadge from "../components/RiskBadge.jsx";

export default function RunHistory() {
  const { prId } = useParams();
  const [runs, setRuns] = useState([]);
  const [pr, setPr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rerunning, setRerunning] = useState(false);

  const load = () => {
    Promise.all([listReviewRuns(prId), getPullRequest(prId)])
      .then(([r, p]) => {
        setRuns(r);
        setPr(p);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [prId]);

  const handleRerun = async () => {
    setRerunning(true);
    try {
      await rerunReview(prId);
      setTimeout(load, 1500);
    } finally {
      setRerunning(false);
    }
  };

  return (
    <div>
      <header className="mb-7 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{pr?.title || "Review runs"}</h1>
          <p className="text-sm text-ink/50 mt-1">
            {pr ? `#${pr.github_pr_number} · ${pr.head_branch} → ${pr.base_branch}` : ""}
          </p>
        </div>
        <button
          onClick={handleRerun}
          disabled={rerunning}
          className="rounded-md bg-sentinel-500 text-white text-sm font-medium px-3.5 py-2 hover:bg-sentinel-600 transition-colors disabled:opacity-50"
        >
          {rerunning ? "Queuing…" : "Re-run review"}
        </button>
      </header>

      {loading && <p className="text-sm text-ink/40">Loading…</p>}

      <div className="flex flex-col gap-2">
        {runs.map((run) => (
          <Link
            key={run.id}
            to={`/runs/${run.id}`}
            className="flex items-center justify-between rounded-lg border border-line bg-surface px-4 py-3 hover:border-sentinel-300 transition-colors"
          >
            <div>
              <p className="text-sm font-mono text-ink/70">{run.trigger_sha.slice(0, 8)}</p>
              <p className="text-xs text-ink/40 mt-0.5">
                {new Date(run.started_at).toLocaleString()} · {run.status}
              </p>
            </div>
            {run.risk_level ? (
              <RiskBadge level={run.risk_level} score={run.risk_score} />
            ) : (
              <span className="text-xs text-ink/40">pending</span>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
