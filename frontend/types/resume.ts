export type ResumeStatus = "uploaded" | "parsing" | "parsed" | "failed";

export interface ResumeParsedData {
  emails: string[];
  phones: string[];
  urls: string[];
  github_url: string | null;
  linkedin_url: string | null;
  detected_skills: string[];
}

export interface Resume {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  status: ResumeStatus;
  parse_error: string | null;
  parsed_data: ResumeParsedData | null;
  ai_summary: string | null;
  ai_strengths: string[] | null;
  ai_suggestions: string[] | null;
  ai_score: number | null;
  ai_provider_used: string | null;
  created_at: string;
  updated_at: string;
}
