import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  ClientAdminResponse,
  ClientRegisterRequest,
  ClientUpdateRequest,
} from '../models/client';

@Injectable({
  providedIn: 'root'
})
export class ClientesService {
  private readonly baseUrl = `${environment.apiUrl}/clients`;

  constructor(private http: HttpClient) {}

  listClients(): Observable<ClientAdminResponse[]> {
    return this.http.get<ClientAdminResponse[]>(this.baseUrl, { headers: this.buildAuthHeaders() });
  }

  registerClient(payload: ClientRegisterRequest): Observable<{ message: string; client: { id_user: number } }> {
    return this.http.post<{ message: string; client: { id_user: number } }>(
      `${this.baseUrl}/register`,
      payload,
      { headers: this.buildAuthHeaders() }
    );
  }

  updateClient(idUser: number, payload: ClientUpdateRequest): Observable<ClientAdminResponse> {
    return this.http.put<ClientAdminResponse>(
      `${this.baseUrl}/${idUser}`,
      payload,
      { headers: this.buildAuthHeaders() }
    );
  }

  deleteClient(idUser: number): Observable<void> {
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
