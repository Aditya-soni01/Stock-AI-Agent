import {
  Activity,
  BrainCircuit,
  HelpCircle,
  LayoutDashboard,
  LineChart,
  LogOut,
  WalletCards,
} from "lucide-react";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", active: true },
  { icon: LineChart, label: "Markets", active: false },
  { icon: Activity, label: "Strategy", active: false },
  { icon: WalletCards, label: "Portfolio", active: false },
  { icon: BrainCircuit, label: "AI Insights", active: false },
];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-[#1a2e1a] bg-[#040904] shadow-[4px_0_24px_rgba(0,0,0,0.45)] md:flex">
      <div className="border-b border-[#1a2e1a] px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#00ff88] bg-[#0d1a0d]">
            <BrainCircuit className="h-5 w-5 text-[#00ff88]" />
          </div>
          <div>
            <h2 className="text-2xl font-bold leading-none text-[#00ff88]">StockAI</h2>
            <p className="mt-1 text-[10px] uppercase tracking-[0.22em] text-[#8fa98f]">Terminal v2.4</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-0 py-4">
        {navItems.map((item) => (
          <button
            key={item.label}
            type="button"
            className={`group flex w-full items-center gap-3 px-6 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] transition-all ${
              item.active
                ? "border-l-[3px] border-[#00ff88] bg-[#0d1a0d] text-[#00ff88] shadow-[inset_0_0_12px_rgba(0,255,136,0.16)]"
                : "text-[#8fa98f] hover:bg-[#0d1a0d] hover:text-[#00ff88]"
            }`}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="space-y-4 px-5 pb-6">
        <button
          type="button"
          className="h-14 w-full rounded-2xl bg-[#00ff88] text-lg font-bold tracking-wide text-black transition-transform hover:scale-[1.01]"
        >
          New Trade
        </button>

        <div className="space-y-1">
          <button
            type="button"
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-[#8fa98f] transition-colors hover:text-[#00ff88]"
          >
            <HelpCircle className="h-4 w-4" />
            Support
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-[#8fa98f] transition-colors hover:text-[#ff7a7a]"
          >
            <LogOut className="h-4 w-4" />
            Log Out
          </button>
        </div>
      </div>
    </aside>
  );
}
