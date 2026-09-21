import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FolderGit2 } from "lucide-react";
import { listRepositories } from "../api/client.js";

export default function Dashboard() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRepositories()
      .then(setRepos)
      .catch(() => setRepos([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <header className="mb-7">
        <h1 className="text-xl font-semibold tracking-tight">Repositories</h1>
        <p className="text-sm text-ink/50 mt-1">
          Every repo with CodeSentinel installed. Reviews run automatically on new and updated pull requests.
        </p>
      </header>

      {loading && <p className="text-sm text-ink/40">Loading…</p>}

      {!loading && repos.length === 0 && (
        <div className="rounded-lg border border-dashed border-line p-8 text-center text-sm text-ink/50">
          No repositories yet. Install the CodeSentinel GitHub App on a repository to get started.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {repos.map((repo) => (
          <Link
            key={repo.id}
            to={`/repos/${repo.id}`}
            className="rounded-lg border border-line bg-surface p-4 hover:border-sentinel-300 transition-colors"
          >
            <div className="flex items-center gap-2">
              <FolderGit2 size={16} className="text-sentinel-500" />
              <span className="text-sm font-medium">{repo.full_name}</span>
            </div>
            <p className="mt-1 text-xs text-ink/40">Default branch: {repo.default_branch}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
