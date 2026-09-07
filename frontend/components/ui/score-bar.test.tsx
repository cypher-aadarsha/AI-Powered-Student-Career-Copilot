import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScoreBar } from "./score-bar";

describe("ScoreBar", () => {
  it("renders the numeric score out of 100", () => {
    render(<ScoreBar score={82} />);
    expect(screen.getByText("82/100")).toBeInTheDocument();
  });

  it.each([
    [85, "bg-emerald-500"],
    [70, "bg-emerald-500"],
    [55, "bg-amber-500"],
    [40, "bg-amber-500"],
    [10, "bg-red-500"],
  ])("colors a score of %i with %s", (score, expectedClass) => {
    const { container } = render(<ScoreBar score={score} />);
    const fill = container.querySelector(`.${expectedClass}`);
    expect(fill).not.toBeNull();
  });
});
