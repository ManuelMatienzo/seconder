import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  AvailableRequestResponse,
  AssignmentDecisionRequest,
  AssignmentTrackingUpdateRequest,
  AssignmentTrackingResponse,
  AssignmentHistoryItemResponse
} from '../models/operations';

@Injectable({
  providedIn: 'root'
})
export class OperationsService {
  private readonly baseUrl = `${environment.apiUrl}/operations`;

  constructor(private http: HttpClient) {}

  getAvailableRequests(): Observable<AvailableRequestResponse[]> {
    return this.http.get<AvailableRequestResponse[]>(`${this.baseUrl}/available-requests`, { headers: this.buildAuthHeaders() });
  }

  decideRequest(incidentId: number, decision: 'aceptado' | 'rechazado'): Observable<any> {
    const payload: AssignmentDecisionRequest = { decision };
    return this.http.patch(`${this.baseUrl}/requests/${incidentId}/decision`, payload, { headers: this.buildAuthHeaders() });
  }

  getTracking(incidentId: number): Observable<AssignmentTrackingResponse> {
    return this.http.get<AssignmentTrackingResponse>(`${this.baseUrl}/assignments/${incidentId}/tracking`, { headers: this.buildAuthHeaders() });
  }

  updateTracking(incidentId: number, payload: AssignmentTrackingUpdateRequest): Observable<AssignmentTrackingResponse> {
    return this.http.patch<AssignmentTrackingResponse>(`${this.baseUrl}/assignments/${incidentId}/tracking`, payload, { headers: this.buildAuthHeaders() });
  }

  getHistory(status?: string): Observable<AssignmentHistoryItemResponse[]> {
    let params = new HttpParams();
    if (status) {
      params = params.set('status', status);
    }
    return this.http.get<AssignmentHistoryItemResponse[]>(`${this.baseUrl}/history`, { headers: this.buildAuthHeaders(), params });
  }

  private buildAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return new HttpHeaders();
    }
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }
}
