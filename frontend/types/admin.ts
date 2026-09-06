import type { JobEmploymentType } from "./job";
import type { QuestionCategory, QuestionDifficulty } from "./interview";
import type { ResourceType } from "./learning";
import type { Skill, SkillCategory } from "./profile";

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "admin";
  is_active: boolean;
  created_at: string;
}

/** Skills on admin write requests are given by name + category, resolved
 * server-side via get_or_create — the same shape the student-facing "add
 * skill" form already uses. */
export interface AdminSkillRef {
  name: string;
  category: SkillCategory;
}

export interface AdminCareerRole {
  id: string;
  title: string;
  description: string | null;
  required_skills: Skill[];
  preferred_skills: Skill[];
}

export interface AdminCareerRoleInput {
  title: string;
  description: string | null;
  required_skills: AdminSkillRef[];
  preferred_skills: AdminSkillRef[];
}

export interface AdminLearningResourceInput {
  title: string;
  description: string | null;
  url: string;
  provider: string;
  resource_type: ResourceType;
  skills: AdminSkillRef[];
}

export interface AdminJobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  employment_type: JobEmploymentType;
  is_remote: boolean;
  description: string | null;
  apply_url: string;
  skills: Skill[];
}

export interface AdminJobPostingInput {
  title: string;
  company: string;
  location: string;
  employment_type: JobEmploymentType;
  is_remote: boolean;
  description: string | null;
  apply_url: string;
  skills: AdminSkillRef[];
}

export interface AdminInterviewQuestion {
  id: string;
  question_text: string;
  category: QuestionCategory;
  difficulty: QuestionDifficulty;
  model_answer: string | null;
  skills: Skill[];
}

export interface AdminInterviewQuestionInput {
  question_text: string;
  category: QuestionCategory;
  difficulty: QuestionDifficulty;
  model_answer: string | null;
  skills: AdminSkillRef[];
}
