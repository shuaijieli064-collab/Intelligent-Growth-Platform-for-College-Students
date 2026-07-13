export function PageLoader() {
  return (
    <div className="animate-fade-in">
      <div className="h-8 bg-bg-active rounded w-48 mb-6 animate-pulse" />
      <div className="h-4 bg-bg-active rounded w-72 mb-8 animate-pulse" />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-bg-card border border-border-default rounded-xl p-6 animate-pulse">
            <div className="h-4 bg-bg-active rounded w-24 mb-4" />
            <div className="h-10 bg-bg-active rounded w-20 mb-2" />
            <div className="h-3 bg-bg-active rounded w-32" />
          </div>
        ))}
      </div>

      <div className="bg-bg-card border border-border-default rounded-xl overflow-hidden animate-pulse">
        <div className="px-6 py-5 border-b border-border-default">
          <div className="h-5 bg-bg-active rounded w-32 mb-2" />
          <div className="h-4 bg-bg-active rounded w-48" />
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-bg-hover/30">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-bg-active" />
                  <div className="flex-1">
                    <div className="h-4 bg-bg-active rounded w-24 mb-2" />
                    <div className="h-3 bg-bg-active rounded w-32 mb-3" />
                    <div className="h-2 bg-bg-active rounded w-full" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
