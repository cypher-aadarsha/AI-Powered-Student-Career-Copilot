import { describe, expect, it } from "vitest";

import { experienceSchema, profileUpdateSchema, projectSchema, skillSchema } from "./schemas";

describe("profileUpdateSchema", () => {
  it("coerces a numeric-string semester to a number within range", () => {
    const result = profileUpdateSchema.safeParse({ semester: "6" });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.semester).toBe(6);
  });

  it("rejects a semester outside 1-12", () => {
    const result = profileUpdateSchema.safeParse({ semester: "13" });
    expect(result.success).toBe(false);
  });

  it("treats an empty string as omitted rather than invalid", () => {
    const result = profileUpdateSchema.safeParse({ university: "", bio: "" });
    expect(result.success).toBe(true);
  });

  it("rejects a github_url that isn't a full http(s) URL", () => {
    const result = profileUpdateSchema.safeParse({ github_url: "github.com/asha" });
    expect(result.success).toBe(false);
  });

  it("accepts a well-formed github_url", () => {
    const result = profileUpdateSchema.safeParse({ github_url: "https://github.com/asha" });
    expect(result.success).toBe(true);
  });
});

describe("skillSchema", () => {
  it("rejects a blank skill name", () => {
    const result = skillSchema.safeParse({ name: "  ", category: "technical", proficiency_level: "beginner" });
    expect(result.success).toBe(false);
  });

  it("rejects a category outside the known set", () => {
    const result = skillSchema.safeParse({ name: "Python", category: "made_up", proficiency_level: "beginner" });
    expect(result.success).toBe(false);
  });
});

describe("projectSchema", () => {
  it("rejects an end_date earlier than the start_date", () => {
    const result = projectSchema.safeParse({
      title: "Career Copilot",
      start_date: "2026-02-01",
      end_date: "2026-01-01",
    });
    expect(result.success).toBe(false);
  });

  it("accepts an end_date on or after the start_date", () => {
    const result = projectSchema.safeParse({
      title: "Career Copilot",
      start_date: "2026-01-01",
      end_date: "2026-02-01",
    });
    expect(result.success).toBe(true);
  });
});

describe("experienceSchema", () => {
  it("requires a start_date", () => {
    const result = experienceSchema.safeParse({
      title: "Backend Intern",
      company: "Some Company",
      employment_type: "internship",
      start_date: "",
    });
    expect(result.success).toBe(false);
  });
});
