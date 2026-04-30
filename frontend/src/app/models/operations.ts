export interface AvailableRequestResponse {
  id_incident: number;
  latitude: number;
  longitude: number;
  status: string;
  description_text: string | null;
  created_at: string;
  photo_url: string | null;
  audio_url: string | null;
  client: {
    id_client: number;
    name: string;
    phone: string | null;
  } | null;
  vehicle: {
    id_vehicle: number;
    brand: string;
    model: string;
    year: number;
    color: string | null;
    license_plate: string;
  } | null;
  ai_analysis: {
    audio_transcription: string | null;
    classification: string | null;
    priority_level: string | null;
    structured_summary: string | null;
  } | null;
}

export interface AssignmentDecisionRequest {
  decision: 'aceptado' | 'rechazado';
}

export interface AssignmentTrackingUpdateRequest {
  id_technician?: number;
  status?: string;
  estimated_time_min?: number;
  distance_km?: number;
  service_price?: number;
  observations?: string;
}

export interface AssignmentTrackingResponse {
  id_assignment: number;
  id_incident: number;
  id_workshop: number;
  id_technician: number | null;
  status: string;
  estimated_time_min: number | null;
  distance_km: number | null;
  service_price: number | null;
  observations: string | null;
  assigned_at: string;
  accepted_at: string | null;
  completed_at: string | null;
  incident_status: string;
  workshop: {
    id_workshop: number;
    workshop_name: string;
  };
  technician: {
    id_technician: number;
    name: string;
    phone: string | null;
    specialty: string | null;
    is_available: boolean;
  } | null;
}

export interface AssignmentHistoryItemResponse {
  id_assignment: number;
  id_incident: number;
  status: string;
  assignment_status: string;
  incident_status: string;
  assigned_at: string;
  accepted_at: string | null;
  completed_at: string | null;
  client_name: string;
  vehicle_summary: string;
  technician_name: string | null;
  incident_description: string | null;
  client?: {
    id_client: number;
    name: string;
    phone: string | null;
  } | null;
  vehicle?: {
    id_vehicle: number;
    brand: string;
    model: string;
    year: number;
    color: string | null;
    license_plate: string;
    plate?: string; // Add plate as alias for license_plate if needed
  } | null;
  ai_analysis?: {
    audio_transcription?: string | null;
    classification: string | null;
    priority_level: string | null;
    structured_summary: string | null;
  } | null;
  photo_url?: string | null;
  audio_url?: string | null;
}
