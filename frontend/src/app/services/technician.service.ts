import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  TechnicianResponse,
  TechnicianCreateRequest,
  TechnicianUpdateRequest,
  TechnicianAvailabilityUpdateRequest
} from '../models/technician';

@Injectable({
  providedIn: 'root'
})
export class TechnicianService {
  private readonly baseUrl = `${environment.apiUrl}/technicians`;

  constructor(private http: HttpClient) {}

  listTechnicians(): Observable<TechnicianResponse[]> {
    return this.http.get<TechnicianResponse[]>(this.baseUrl, { headers: this.buildAuthHeaders() });
  }

  getTechnician(id: number): Observable<TechnicianResponse> {
    return this.http.get<TechnicianResponse>(`${this.baseUrl}/${id}`, { headers: this.buildAuthHeaders() });
  }

  createTechnician(payload: TechnicianCreateRequest): Observable<TechnicianResponse> {
    return this.http.post<TechnicianResponse>(this.baseUrl, payload, { headers: this.buildAuthHeaders() });
  }

  updateTechnician(id: number, payload: TechnicianUpdateRequest): Observable<TechnicianResponse> {
    return this.http.put<TechnicianResponse>(`${this.baseUrl}/${id}`, payload, { headers: this.buildAuthHeaders() });
  }

  updateAvailability(id: number, payload: TechnicianAvailabilityUpdateRequest): Observable<TechnicianResponse> {
    return this.http.patch<TechnicianResponse>(`${this.baseUrl}/${id}/availability`, payload, { headers: this.buildAuthHeaders() });
  }

  private buildAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return new HttpHeaders();
    }
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }
}
