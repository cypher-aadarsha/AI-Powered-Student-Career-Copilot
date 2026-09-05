export type SkillCategory = "technical" | "soft" | "programming_language" | "framework" | "tool";
export type ProficiencyLevel = "beginner" | "intermediate" | "advanced" | "expert";
export type SkillSource = "manual" | "resume_extracted";
export type EmploymentType = "internship" | "part_time" | "full_time" | "freelance" | "volunteer";

export interface Skill {
  id: string;
  name: string;
  category: SkillCategory;
}

export interface StudentSkill {
  id: string;
  proficiency_level: ProficiencyLevel;
  source: SkillSource;
  skill: Skill;
}

export interface Project {
  id: string;
  title: string;
  description: string | null;
  repo_url: string | null;
  demo_url: string | null;
  start_date: string | null;
  end_date: string | null;
  skills: Skill[];
  created_at: string;
  updated_at: string;
}

export interface Experience {
  id: string;
  title: string;
  company: string;
  employment_type: EmploymentType;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string | null;
  issue_date: string | null;
  credential_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentProfile {
  id: string;
  university: string | null;
  degree: string | null;
  semester: number | null;
  graduation_year: number | null;
  location: string | null;
  bio: string | null;
  profile_picture_url: string | null;
  github_url: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  skills: StudentSkill[];
  projects: Project[];
  experiences: Experience[];
  certifications: Certification[];
  created_at: string;
  updated_at: string;
}
