import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TimeoutError, finalize, timeout } from 'rxjs';

import { LoginRequest, LoginResponse } from '../../../models/auth';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export class Login {
  loginForm: FormGroup;
  isSubmitting = false;
  errorMessage = '';
  showPassword = false;

  constructor(private fb: FormBuilder, private router: Router, private authService: AuthService) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email, Validators.maxLength(254)]],
      password: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(128)]],
    });

    this.loginForm.valueChanges.subscribe(() => {
      if (this.errorMessage) {
        this.errorMessage = '';
      }
    });
  }

  iniciarSesion(): void {
    if (this.isSubmitting) {
      return;
    }

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.errorMessage = 'Completa los campos requeridos antes de continuar.';
      return;
    }

    const payload: LoginRequest = {
      email: String(this.loginForm.value.email ?? '').trim(),
      password: String(this.loginForm.value.password ?? ''),
    };

    this.isSubmitting = true;
    this.errorMessage = '';

    this.authService
      .login(payload)
      .pipe(
        timeout(12000),
        finalize(() => (this.isSubmitting = false))
      )
      .subscribe({
        next: (response: LoginResponse) => {
          this.authService.saveSession(response);

          const route = this.authService.resolveHomeRoute(response.user);
          if (!route) {
            this.errorMessage = 'Tu rol no tiene una vista asignada en el sistema.';
            return;
          }

          this.router.navigateByUrl(route);
        },
        error: (error: unknown) => {
          if (error instanceof TimeoutError) {
            this.errorMessage = 'La validacion tardo demasiado. Revisa la conexion con el servidor y vuelve a intentar.';
            return;
          }

          if (error instanceof HttpErrorResponse) {
            this.errorMessage = this.resolveAuthError(error);
            return;
          }

          this.errorMessage = 'Ocurrio un error inesperado durante el inicio de sesion.';
        },
      });
  }

  private resolveAuthError(error: HttpErrorResponse): string {
    const detail = this.extractBackendDetail(error.error);

    if (error.status === 0) {
      return 'No se pudo contactar al backend. Verifica que el servidor este en ejecucion.';
    }

    if (error.status === 401) {
      return 'Credenciales invalidas. Verifica tu correo y contrasena.';
    }

    if (error.status === 422) {
      return detail ?? 'Los datos enviados no son validos. Revisa el correo y la contrasena.';
    }

    if (error.status >= 500) {
      return 'El servidor tuvo un problema. Intenta nuevamente en unos segundos.';
    }

    return detail ?? 'No se pudo iniciar sesion. Intenta nuevamente en unos segundos.';
  }

  private extractBackendDetail(payload: unknown): string | null {
    if (!payload) {
      return null;
    }

    if (typeof payload === 'string') {
      return payload;
    }

    if (typeof payload !== 'object') {
      return null;
    }

    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: unknown };
      if (typeof first?.msg === 'string') {
        return first.msg;
      }
    }

    return null;
  }
}
