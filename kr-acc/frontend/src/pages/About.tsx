export default function About() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-2xl font-bold">kr-acc 소개</h1>
      <p className="mt-2 text-gray-600">
        kr-acc (Korean Accountability Graph)는 한국 국회의원의 입법 활동 데이터를
        그래프 DB로 통합하여 시민 누구나 탐색할 수 있는 투명성 인프라입니다.
      </p>

      <h2 className="mt-8 text-lg font-semibold">데이터 출처</h2>
      <div className="mt-3 space-y-3">
        <div className="rounded-lg border bg-white p-4">
          <p className="font-medium">열린국회정보 API</p>
          <p className="mt-1 text-sm text-gray-500">
            국회의원 인적사항, 의안 정보, 본회의 표결 정보, 위원회 현황 등 233+
            API 엔드포인트에서 데이터를 수집합니다.
          </p>
          <a
            href="https://open.assembly.go.kr"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-sm text-blue-600 hover:underline"
          >
            open.assembly.go.kr →
          </a>
        </div>
      </div>

      <h2 className="mt-8 text-lg font-semibold">법적 근거</h2>
      <div className="mt-3 rounded-lg border bg-white p-4">
        <ul className="space-y-2 text-sm text-gray-600">
          <li>
            <strong>공직자윤리법</strong> — 재산공개 의무 (공개 데이터)
          </li>
          <li>
            <strong>국회법</strong> — 의안 정보, 표결 기록 공개 의무
          </li>
          <li>
            <strong>공공데이터법</strong> — 열린국회정보 API 무료 제공 근거
          </li>
        </ul>
        <p className="mt-3 text-xs text-gray-400">
          kr-acc는 법적으로 공개 의무가 있는 데이터만 수집·표시합니다.
          가족 정보는 표시하지 않습니다.
        </p>
      </div>

      <h2 className="mt-8 text-lg font-semibold">기술 스택</h2>
      <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {[
          { label: "데이터베이스", value: "PostgreSQL 16 + Apache AGE" },
          { label: "백엔드", value: "FastAPI (Python 3.12+)" },
          { label: "ETL", value: "Prefect 3.x" },
          { label: "프론트엔드", value: "React 19 + TypeScript + Vite" },
          { label: "시각화", value: "D3.js (그래프) + Recharts (차트)" },
          { label: "배포", value: "Docker Compose" },
        ].map((item) => (
          <div key={item.label} className="rounded-lg border bg-white p-3">
            <p className="text-xs text-gray-500">{item.label}</p>
            <p className="mt-0.5 text-sm font-medium">{item.value}</p>
          </div>
        ))}
      </div>

      <h2 className="mt-8 text-lg font-semibold">오픈소스</h2>
      <p className="mt-2 text-sm text-gray-600">
        kr-acc는 MIT 라이선스 오픈소스 프로젝트입니다. 기여와 피드백을 환영합니다.
      </p>

      <div className="mt-8 rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-500">
        <p>
          브라질의{" "}
          <a
            href="https://github.com/World-Open-Graph/br-acc"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            br-acc (World-Open-Graph)
          </a>
          에서 영감을 받았습니다.
        </p>
      </div>
    </div>
  );
}
