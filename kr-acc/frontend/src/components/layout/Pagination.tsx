interface PaginationProps {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({
  page,
  pages,
  onPageChange,
}: PaginationProps) {
  if (pages <= 1) return null;

  const range: number[] = [];
  const start = Math.max(1, page - 2);
  const end = Math.min(pages, page + 2);
  for (let i = start; i <= end; i++) range.push(i);

  return (
    <div className="flex items-center justify-center gap-1 pt-4">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="rounded px-2 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-40"
      >
        이전
      </button>
      {start > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            className="rounded px-2 py-1 text-sm text-gray-600 hover:bg-gray-100"
          >
            1
          </button>
          {start > 2 && <span className="px-1 text-gray-400">…</span>}
        </>
      )}
      {range.map((p) => (
        <button
          key={p}
          onClick={() => onPageChange(p)}
          className={`rounded px-2 py-1 text-sm ${
            p === page
              ? "bg-gray-900 text-white"
              : "text-gray-600 hover:bg-gray-100"
          }`}
        >
          {p}
        </button>
      ))}
      {end < pages && (
        <>
          {end < pages - 1 && <span className="px-1 text-gray-400">…</span>}
          <button
            onClick={() => onPageChange(pages)}
            className="rounded px-2 py-1 text-sm text-gray-600 hover:bg-gray-100"
          >
            {pages}
          </button>
        </>
      )}
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= pages}
        className="rounded px-2 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-40"
      >
        다음
      </button>
    </div>
  );
}
