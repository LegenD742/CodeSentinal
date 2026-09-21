import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { GitPullRequest } from "lucide-react";
import { listPullRequests } from "../api/client.js";

export default function RepoDetail() {
  const { repoId } = useParams();
  const [prs, setPrs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listPullRequests(repoId)
      .then(setPrs)
      .catch(() => setPrs([]))
      .finally(() => setLoading(false));
  }, [repoId]);

  return (
    <div>
      <header className="mb-7">
        <h1 className="text-xl font-semibold tracking-tight">Pull requests</h1>
        <p className="text-sm text-ink/50 mt-1">Review history for this repository.</p>
      </header>

      {loading && <p className="text-sm text-ink/40">Loading…</p>}

      <div className="flex flex-col gap-2">
        {prs.map((pr) => (
          <Link
            key={pr.id}
            to={`/prs/${pr.id}`}
            className="flex items-center justify-between rounded-lg border border-line bg-surface px-4 py-3 hover:border-sentinel-300 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <GitPullRequest size={16} className="text-sentinel-500" />
              <div>
                <p className="text-sm font-medium">{pr.title}</p>
                <p className="text-xs text-ink/40 mt-0.5">
                  #{pr.github_pr_number} by {pr.author_login} · {pr.head_branch} → {pr.base_branch}
                </p>
              </div>
            </div>
            <span className="text-xs font-mono text-ink/40">
              +{pr.additions} −{pr.deletions}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
