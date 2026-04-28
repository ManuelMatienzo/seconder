export interface WorkshopUpsertRequest {
  workshop_name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string | null;
  specialties: string | null;
  is_available: boolean;
}

export interface WorkshopAdminUpsertRequest extends WorkshopUpsertRequest {
  id_user: number;
}

export interface WorkshopAccountCreateRequest extends WorkshopUpsertRequest {
  name: string;
  email: string;
  password: string;
}

export interface WorkshopResponse {
  id_user: number;
  workshop_name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string | null;
  specialties: string | null;
  is_available: boolean;
  rating: number | null;
}
