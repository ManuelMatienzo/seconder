export interface ClientRegisterRequest {
  name: string;
  email: string;
  password: string;
  phone: string | null;
}

export interface ClientUpdateRequest {
  name: string;
  email: string;
  phone: string | null;
}

export interface ClientAdminResponse {
  id_user: number;
  name: string;
  email: string;
  phone: string | null;
  status: string;
  created_at: string;
}
