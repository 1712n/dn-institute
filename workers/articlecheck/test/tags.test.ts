import { describe, expect, it } from "vitest";
import { extractAllBetweenTags, extractLastBetweenTags } from "../common/src/tags";

describe("tags", () => {
  it("extracts all occurrences", () => {
    const out = extractAllBetweenTags("statement", "<statement>a</statement> x <statement>b</statement>");
    expect(out).toEqual(["a", "b"]);
  });

  it("extracts last occurrence", () => {
    const out = extractLastBetweenTags("answer", "<answer>one</answer><answer>two</answer>");
    expect(out).toBe("two");
  });
});

