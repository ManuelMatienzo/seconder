export interface LoginRequest {
  email: string;
  password: string;
}

export interface RoleResponse {
  id_role: number;
  name: string;
  description: string | null;
}

export interface UserResponse {
  id_user: number;
  name: string;
  email: string;
  phone: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  id_role: number;
  role: RoleResponse | null;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  token_type: string;
  user: UserResponse;
}
