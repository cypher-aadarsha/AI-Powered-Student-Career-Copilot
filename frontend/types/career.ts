import type { ProficiencyLevel, Skill } from "./profile";

export interface CareerRoleSummary {
  id: string;
  title: string;
  description: string | null;
}

export interface CareerListItem {
  role: CareerRoleSummary;
  score: number;
  matched_required: number;
  total_required: number;
  matched_preferred: number;
  total_preferred: number;
}

export interface MatchedSkill {
  skill: Skill;
  proficiency_level: ProficiencyLevel;
}

export interface CareerDetail {
  role: CareerRoleSummary;
  score: number;
  matched_skills: MatchedSkill[];
  missing_required_skills: Skill[];
  missing_preferred_skills: Skill[];
  summary: string;
}
