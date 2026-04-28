export interface TechnicianResponse {
  id_technician: number;
  id_workshop: number;
  name: string;
  phone: string | null;
  specialty: string | null;
  is_available: boolean;
  created_at: string;
}

export interface TechnicianCreateRequest {
  name: string;
  phone?: string | null;
  specialty?: string | null;
  is_available?: boolean;
}

export interface TechnicianUpdateRequest {
  name: string;
  phone?: string | null;
  specialty?: string | null;
}

export interface TechnicianAvailabilityUpdateRequest {
  is_available: boolean;
}
