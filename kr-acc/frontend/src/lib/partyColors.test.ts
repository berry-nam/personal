import { describe, it, expect } from "vitest";
import { getPartyColor } from "./partyColors";

describe("getPartyColor", () => {
  it("returns correct color for 국민의힘", () => {
    expect(getPartyColor("국민의힘")).toBe("#E61E2B");
  });

  it("returns correct color for 더불어민주당", () => {
    expect(getPartyColor("더불어민주당")).toBe("#004EA2");
  });

  it("returns default gray for unknown party", () => {
    expect(getPartyColor("무소속")).toBe("#9CA3AF");
  });

  it("returns default gray for null", () => {
    expect(getPartyColor(null)).toBe("#9CA3AF");
  });

  it("returns default gray for undefined", () => {
    expect(getPartyColor(undefined)).toBe("#9CA3AF");
  });
});
