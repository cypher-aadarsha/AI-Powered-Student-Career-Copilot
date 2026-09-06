import type { MatchedSkill } from "./career";
import type { Skill } from "./profile";

export type JobEmploymentType = "full_time" | "part_time" | "internship" | "contract";

export interface JobPostingSummary {
  id: string;
  title: string;
  company: string;
  location: string;
  employment_type: JobEmploymentType;
  is_remote: boolean;
}

export interface JobListItem {
  job: JobPostingSummary;
  score: number;
  matched_skills: number;
  total_skills: number;
}

export interface JobDetail {
  job: JobPostingSummary;
  description: string | null;
  apply_url: string;
  score: number;
  matched_skills: MatchedSkill[];
  missing_skills: Skill[];
  summary: string;
}
