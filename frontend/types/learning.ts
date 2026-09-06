import type { CareerRoleSummary } from "./career";
import type { Skill } from "./profile";

export type ResourceType = "course" | "tutorial" | "article" | "video" | "book" | "documentation";

export interface LearningResource {
  id: string;
  title: string;
  description: string | null;
  url: string;
  provider: string;
  resource_type: ResourceType;
  skills: Skill[];
}

export interface SkillWithResources {
  skill: Skill;
  resources: LearningResource[];
}

export interface RoleLearningPlan {
  role: CareerRoleSummary;
  missing_required: SkillWithResources[];
  missing_preferred: SkillWithResources[];
}
