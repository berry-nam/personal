import { describe, it, expect } from "vitest";
import { formatDate, formatNumber, truncate } from "./format";

describe("formatDate", () => {
  it("formats ISO date to dotted format", () => {
    expect(formatDate("2024-06-15")).toBe("2024.06.15");
  });

  it("returns dash for null", () => {
    expect(formatDate(null)).toBe("—");
  });

  it("returns dash for undefined", () => {
    expect(formatDate(undefined)).toBe("—");
  });
});

describe("formatNumber", () => {
  it("formats number with locale", () => {
    const result = formatNumber(1234);
    // ko-KR formatting uses comma separator
    expect(result).toContain("1");
    expect(result).toContain("234");
  });

  it("returns dash for null", () => {
    expect(formatNumber(null)).toBe("—");
  });

  it("returns dash for undefined", () => {
    expect(formatNumber(undefined)).toBe("—");
  });
});

describe("truncate", () => {
  it("returns string unchanged if within limit", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates and adds ellipsis", () => {
    expect(truncate("hello world", 6)).toBe("hello…");
  });

  it("handles exact length", () => {
    expect(truncate("hello", 5)).toBe("hello");
  });
});
