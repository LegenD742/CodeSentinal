const STAGES = ["fetching", "analyzing", "reasoning", "verifying", "posting", "completed"];

export default function AgentTimeline({ status }) {
  const currentIndex = STAGES.indexOf(status);

  return (
    <div className="flex items-center gap-2">
      {STAGES.map((stage, i) => {
        const done = currentIndex > i || status === "completed";
        const active = i === currentIndex;
        return (
          <div key={stage} className="flex items-center gap-2">
            <div
              className={`h-1.5 w-8 rounded-full ${
                done ? "bg-sentinel-500" : active ? "bg-sentinel-300" : "bg-line"
              }`}
            />
          </div>
        );
      })}
      <span className="ml-2 text-xs text-ink/50 font-mono">{status}</span>
    </div>
  );
}
