import { Link } from "react-router";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <p className="text-6xl font-bold text-gray-200">404</p>
      <p className="mt-4 text-lg text-gray-600">페이지를 찾을 수 없습니다</p>
      <Link
        to="/"
        className="mt-6 rounded-md bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-800"
      >
        대시보드로 이동
      </Link>
    </div>
  );
}
