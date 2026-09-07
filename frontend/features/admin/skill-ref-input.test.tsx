import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import type { AdminSkillRef } from "@/types/admin";

import { SkillRefInput } from "./skill-ref-input";

// A tiny controlled-state wrapper — SkillRefInput itself is fully
// controlled (value/onChange), so the test drives it the same way a real
// admin form does.
function Wrapper() {
  const [value, setValue] = useState<AdminSkillRef[]>([]);
  return <SkillRefInput label="Required skills" value={value} onChange={setValue} />;
}

describe("SkillRefInput", () => {
  it("adds a typed skill as a chip and clears the input", async () => {
    const user = userEvent.setup();
    render(<Wrapper />);

    await user.type(screen.getByPlaceholderText("Skill name"), "Python");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Skill name")).toHaveValue("");
  });

  it("adds a skill on Enter without submitting a form", async () => {
    const user = userEvent.setup();
    render(<Wrapper />);

    await user.type(screen.getByPlaceholderText("Skill name"), "FastAPI{Enter}");
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
  });

  it("de-duplicates case-insensitively instead of adding a second chip", async () => {
    const user = userEvent.setup();
    render(<Wrapper />);

    await user.type(screen.getByPlaceholderText("Skill name"), "Python{Enter}");
    await user.type(screen.getByPlaceholderText("Skill name"), "python{Enter}");

    expect(screen.getAllByText(/^python$/i)).toHaveLength(1);
  });

  it("removes a chip via its remove button", async () => {
    const user = userEvent.setup();
    render(<Wrapper />);

    await user.type(screen.getByPlaceholderText("Skill name"), "Python{Enter}");
    expect(screen.getByText("Python")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Remove Python" }));
    expect(screen.queryByText("Python")).not.toBeInTheDocument();
  });

  it("ignores an empty/whitespace-only submission", async () => {
    const user = userEvent.setup();
    render(<Wrapper />);

    await user.type(screen.getByPlaceholderText("Skill name"), "   {Enter}");
    expect(screen.queryByRole("button", { name: /^Remove/ })).not.toBeInTheDocument();
  });
});
