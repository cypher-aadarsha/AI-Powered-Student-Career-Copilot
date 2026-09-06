import type { CareerRoleSummary } from "./career";
import type { Skill } from "./profile";

export type QuestionCategory = "behavioral" | "technical" | "situational";
export type QuestionDifficulty = "easy" | "medium" | "hard";
export type SessionStatus = "in_progress" | "completed";

export interface InterviewQuestion {
  id: string;
  question_text: string;
  category: QuestionCategory;
  difficulty: QuestionDifficulty;
  skills: Skill[];
}

export interface MockInterviewAnswer {
  id: string;
  question_id: string;
  answer_text: string;
  ai_feedback: string[] | null;
  ai_score: number | null;
  ai_provider_used: string | null;
  created_at: string;
}

export interface MockInterviewSessionSummary {
  id: string;
  career_role: CareerRoleSummary | null;
  status: SessionStatus;
  question_count: number;
  answered_count: number;
  average_score: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface MockInterviewSessionDetail {
  id: string;
  career_role: CareerRoleSummary | null;
  status: SessionStatus;
  questions: InterviewQuestion[];
  answers: MockInterviewAnswer[];
  average_score: number | null;
  created_at: string;
  completed_at: string | null;
}
