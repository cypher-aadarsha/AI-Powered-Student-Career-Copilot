import { describe, expect, it } from "vitest";

import { loginSchema, registerSchema } from "./schemas";

describe("registerSchema", () => {
  it("accepts a valid registration", () => {
    const result = registerSchema.safeParse({
      full_name: "Asha Sharma",
      email: "asha@example.edu.np",
      password: "password123",
    });
    expect(result.success).toBe(true);
  });

  it("rejects a password shorter than 8 characters", () => {
    const result = registerSchema.safeParse({
      full_name: "Asha Sharma",
      email: "asha@example.edu.np",
      password: "short",
    });
    expect(result.success).toBe(false);
  });

  it("rejects a malformed email", () => {
    const result = registerSchema.safeParse({
      full_name: "Asha Sharma",
      email: "not-an-email",
      password: "password123",
    });
    expect(result.success).toBe(false);
  });

  it("rejects an empty full name", () => {
    const result = registerSchema.safeParse({
      full_name: "",
      email: "asha@example.edu.np",
      password: "password123",
    });
    expect(result.success).toBe(false);
  });
});

describe("loginSchema", () => {
  it("accepts any non-empty password (strength is only enforced at registration)", () => {
    const result = loginSchema.safeParse({ email: "asha@example.edu.np", password: "x" });
    expect(result.success).toBe(true);
  });

  it("rejects an empty password", () => {
    const result = loginSchema.safeParse({ email: "asha@example.edu.np", password: "" });
    expect(result.success).toBe(false);
  });

  it("rejects a malformed email", () => {
    const result = loginSchema.safeParse({ email: "not-an-email", password: "x" });
    expect(result.success).toBe(false);
  });
});
