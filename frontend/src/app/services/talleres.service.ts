import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  WorkshopAccountCreateRequest,
  WorkshopAdminUpsertRequest,
  WorkshopResponse,
  WorkshopUpsertRequest,
} from '../models/workshop';

@Injectable({
  providedIn: 'root'
})
export class TalleresService {
  private readonly baseUrl = `${environment.apiUrl}/workshops`;

  constructor(private http: HttpClient) {}

  listWorkshops(): Observable<WorkshopResponse[]> {
    return this.http.get<WorkshopResponse[]>(this.baseUrl, { headers: this.buildAuthHeaders() });
  }

  createWorkshop(payload: WorkshopAdminUpsertRequest): Observable<WorkshopResponse> {
    return this.http.post<WorkshopResponse>(this.baseUrl, payload, { headers: this.buildAuthHeaders() });
  }

  createWorkshopAccount(payload: WorkshopAccountCreateRequest): Observable<WorkshopResponse> {
    return this.http.post<WorkshopResponse>(`${this.baseUrl}/register`, payload, { headers: this.buildAuthHeaders() });
  }

  updateWorkshop(idUser: number, payload: WorkshopUpsertRequest): Observable<WorkshopResponse> {
    return this.http.put<WorkshopResponse>(`${this.baseUrl}/${idUser}`, payload, { headers: this.buildAuthHeaders() });
  }

  deleteWorkshop(idUser: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${idUser}`, { headers: this.buildAuthHeaders() });
  }

  private buildAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return new HttpHeaders();
    }

    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }
}
