export interface AvailableRequestResponse {
  id_incident: number;
  latitude: number;
  longitude: number;
  status: string;
  created_at: string;
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
  id_workshop: number;
  status: string;
  assigned_at: string;
  accepted_at: string | null;
  completed_at: string | null;
  technician_name: string | null;
  incident_description: string | null;
  client_name: string;
  vehicle_summary: string;
}
