import styles from "./SjBadge.module.css";

const cls: Record<string, string> = {
  BS:  styles.bs,
  IS:  styles.is,
  CFS: styles.cfs,
  CIS: styles.cis,
};

export default function SjBadge({ sj }: { sj: string }) {
  return (
    <span className={`${styles.badge} ${cls[sj] ?? styles.fallback}`}>{sj}</span>
  );
}
