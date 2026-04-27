import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { LoginRequest, LoginResponse, UserResponse } from '../models/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly loginUrl = `${environment.apiUrl}/auth/login`;

  constructor(private http: HttpClient) {}

  login(payload: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(this.loginUrl, payload);
  }

  saveSession(response: LoginResponse): void {
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('token_type', response.token_type);
    localStorage.setItem('auth_user', JSON.stringify(response.user));
  }

  clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('auth_user');
  }

  resolveHomeRoute(user: UserResponse): string | null {
    const roleName = (user.role?.name ?? '').toLowerCase();

    if (roleName.includes('admin') || roleName.includes('administrador')) {
      return '/admin/dashboard';
    }

    if (roleName.includes('taller') || roleName.includes('workshop')) {
      return '/taller/dashboard';
    }

    if (user.id_role === 1) {
      return '/admin/dashboard';
    }

    if (user.id_role === 2) {
      return '/taller/dashboard';
    }

    return null;
  }
}
