import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import "@testing-library/jest-dom/vitest";

// vitest.config.mts doesn't set test.globals, so Testing Library's
// afterEach-based auto-cleanup (which only self-registers when it detects a
// global test framework) never fires on its own — do it explicitly instead,
// otherwise each render() in a file leaks into the next test's DOM.
afterEach(() => {
  cleanup();
});
