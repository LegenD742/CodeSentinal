import { NavLink } from "react-router-dom";
import { ShieldCheck, LayoutGrid, History } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-line bg-surface px-5 py-7 flex flex-col gap-8">
      <div className="flex items-center gap-2">
        <ShieldCheck size={22} className="text-sentinel-500" strokeWidth={2.2} />
        <span className="font-semibold text-[15px] tracking-tight">CodeSentinel</span>
      </div>

      <nav className="flex flex-col gap-1 text-sm">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex items-center gap-2 rounded-md px-3 py-2 transition-colors ${
              isActive ? "bg-sentinel-50 text-sentinel-700 font-medium" : "text-ink/70 hover:bg-paper"
            }`
          }
        >
          <LayoutGrid size={16} />
          Repositories
        </NavLink>
      </nav>

      <div className="mt-auto text-xs text-ink/40 leading-relaxed">
        Autonomous PR review
        <br />
        Bug · Security · Performance · Quality
      </div>
    </aside>
  );
}
