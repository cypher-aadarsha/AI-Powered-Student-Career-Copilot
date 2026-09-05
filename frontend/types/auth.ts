export type UserRole = "student" | "admin";

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
}
