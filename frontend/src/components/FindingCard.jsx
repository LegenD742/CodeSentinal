const SEVERITY_DOT = {
  critical: "bg-severity-critical",
  high: "bg-severity-high",
  medium: "bg-severity-medium",
  low: "bg-severity-low",
  info: "bg-severity-info",
};

export default function FindingCard({ finding }) {
  const rejected = finding.critic_verdict === "rejected";

  return (
    <div className={`rounded-lg border border-line bg-surface p-4 ${rejected ? "opacity-50" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${SEVERITY_DOT[finding.severity] || SEVERITY_DOT.info}`} />
          <span className="text-sm font-medium">{finding.title}</span>
        </div>
        <span className="text-xs font-mono text-ink/40">
          {finding.file_path}:{finding.start_line}
        </span>
      </div>

      <p className="mt-2 text-sm text-ink/70 leading-relaxed">{finding.explanation}</p>

      <div className="mt-3 rounded-md bg-paper border border-line px-3 py-2">
        <pre className="text-xs font-mono whitespace-pre-wrap text-ink/80">{finding.evidence}</pre>
      </div>

      {finding.suggested_fix && (
        <p className="mt-2 text-sm text-sentinel-700">
          <span className="font-medium">Suggested fix — </span>
          {finding.suggested_fix}
        </p>
      )}

      <div className="mt-3 flex items-center gap-3 text-xs text-ink/40">
        <span>{finding.source_agent} agent</span>
        <span>·</span>
        <span>{finding.confidence}% confidence</span>
        <span>·</span>
        <span className={rejected ? "text-severity-critical" : "text-sentinel-600"}>
          {rejected ? "rejected by critic" : `verified — ${finding.critic_verdict || "confirmed"}`}
        </span>
      </div>
    </div>
  );
}
