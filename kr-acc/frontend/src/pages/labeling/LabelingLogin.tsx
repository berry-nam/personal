import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useLogin, useRegister } from "@/api/labelingQueries";

export default function LabelingLogin() {
  const navigate = useNavigate();

  useEffect(() => {
    document.title = "CookieDeal Labeler";
  }, []);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState("");

  const loginMutation = useLogin();
  const registerMutation = useRegister();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      let data;
      if (mode === "login") {
        data = await loginMutation.mutateAsync({ email, password });
      } else {
        data = await registerMutation.mutateAsync({
          email,
          display_name: displayName,
          password,
          invite_code: inviteCode,
        });
      }
      localStorage.setItem("labeling_token", data.access_token);
      localStorage.setItem("labeling_user", JSON.stringify(data.user));
      navigate("/labeling");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "An error occurred";
      setError(msg);
    }
  };

  const isPending = loginMutation.isPending || registerMutation.isPending;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500 text-lg font-black text-white shadow-lg shadow-brand-500/25">CD</div>
          <h1 className="text-2xl font-bold text-gray-900">CookieDeal Labeler</h1>
          <p className="mt-1 text-sm text-gray-500">기업탐색 Fine-tuning 라벨링 도구</p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow-sm">
          {/* Mode toggle */}
          <div className="mb-6 flex rounded-lg bg-gray-100 p-1">
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`flex-1 rounded-md py-1.5 text-sm font-medium transition-all ${
                mode === "login"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              로그인
            </button>
            <button
              type="button"
              onClick={() => setMode("register")}
              className={`flex-1 rounded-md py-1.5 text-sm font-medium transition-all ${
                mode === "register"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              가입
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-3">
            <input
              type="email"
              placeholder="이메일"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/20"
            />

            {mode === "register" && (
              <input
                type="text"
                placeholder="이름"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/20"
              />
            )}

            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/20"
            />

            {mode === "register" && (
              <input
                type="text"
                placeholder="초대 코드"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                required
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/20"
              />
            )}

            <button
              type="submit"
              disabled={isPending}
              className="mt-2 rounded-lg bg-brand-500 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
            >
              {isPending ? "..." : mode === "login" ? "로그인" : "가입하기"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
