import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { InlineConfirmButton } from "./inline-confirm-button";

describe("InlineConfirmButton", () => {
  it("requires a second click before calling onConfirm", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    render(<InlineConfirmButton onConfirm={onConfirm} />);

    await user.click(screen.getByRole("button", { name: "Delete" }));
    expect(onConfirm).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Confirm?" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirm?" }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("cancels back to the armed-off state without calling onConfirm", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    render(<InlineConfirmButton onConfirm={onConfirm} />);

    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onConfirm).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
  });

  it("supports custom labels", async () => {
    const user = userEvent.setup();
    render(<InlineConfirmButton onConfirm={vi.fn()} label="Remove" confirmLabel="Really remove?" />);

    await user.click(screen.getByRole("button", { name: "Remove" }));
    expect(screen.getByRole("button", { name: "Really remove?" })).toBeInTheDocument();
  });
});
