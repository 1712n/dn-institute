import { describe, expect, it } from "vitest";
import { parseReviewerAllowlist } from "../common/src/allowlist";

describe("parseReviewerAllowlist", () => {
  it("parses JSON array (preferred format)", () => {
    const s = parseReviewerAllowlist('["Alice","bob","  Carol  "]');
    expect([...s].sort()).toEqual(["alice", "bob", "carol"]);
  });

  it("parses newline/comma separated list", () => {
    const s = parseReviewerAllowlist("Alice\nbob,carol");
    expect([...s].sort()).toEqual(["alice", "bob", "carol"]);
  });

  it("handles empty input", () => {
    expect(parseReviewerAllowlist("").size).toBe(0);
    expect(parseReviewerAllowlist(undefined).size).toBe(0);
  });
});

