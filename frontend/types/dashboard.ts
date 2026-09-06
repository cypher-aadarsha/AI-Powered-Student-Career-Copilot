import type { CareerListItem } from "./career";
import type { JobListItem } from "./job";
import type { ResumeStatus } from "./resume";

export interface ChecklistItem {
  label: string;
  done: boolean;
}

export interface ProfileCompletion {
  score: number;
  checklist: ChecklistItem[];
}

export interface DashboardResumeSummary {
  id: string;
  original_filename: string;
  status: ResumeStatus;
  ai_score: number | null;
  created_at: string;
}

export interface InterviewStats {
  total_sessions: number;
  completed_sessions: number;
  average_score: number | null;
}

export interface DashboardData {
  profile_completion: ProfileCompletion;
  latest_resume: DashboardResumeSummary | null;
  top_career_matches: CareerListItem[];
  top_job_matches: JobListItem[];
  skill_count: number;
  interview_stats: InterviewStats;
  suggested_actions: string[];
}
