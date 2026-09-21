const LEVEL_STYLES = {
  low: "bg-sentinel-50 text-sentinel-700 border-sentinel-100",
  medium: "bg-[#FBF3DC] text-severity-medium border-[#F0E1AE]",
  high: "bg-[#FBEBE0] text-severity-high border-[#F2CDA9]",
  critical: "bg-[#FBE4E2] text-severity-critical border-[#F2BEB9]",
};

export default function RiskBadge({ level, score }) {
  const style = LEVEL_STYLES[level] || LEVEL_STYLES.low;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium ${style}`}>
      {typeof score === "number" && <span className="font-mono">{Math.round(score)}</span>}
      {level}
    </span>
  );
}
