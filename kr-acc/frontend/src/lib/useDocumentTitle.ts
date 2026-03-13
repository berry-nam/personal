import { useEffect } from "react";

const BASE_TITLE = "kr-acc — 국회의원 활동 그래프";

export default function useDocumentTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} | kr-acc` : BASE_TITLE;
    return () => {
      document.title = BASE_TITLE;
    };
  }, [title]);
}
