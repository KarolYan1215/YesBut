export default function SessionLoading(): JSX.Element {
  return (
    <div className="h-full flex flex-col animate-pulse">
      <div className="h-12 border-b border-ink-20 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="h-4 w-32 bg-ink-10 rounded" />
          <div className="h-5 w-20 bg-ink-10 rounded" />
        </div>
        <div className="flex items-center gap-2">
          <div className="h-6 w-16 bg-ink-10 rounded" />
          <div className="h-6 w-16 bg-ink-10 rounded" />
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 bg-paper p-4">
          <div className="h-full border border-ink-10 rounded-md flex items-center justify-center">
            <div className="text-sm text-ink-40">Loading graph...</div>
          </div>
        </div>

        <div className="w-80 border-l border-ink-20 p-4 space-y-4">
          <div className="h-6 w-24 bg-ink-10 rounded" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-ink-05 rounded" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
