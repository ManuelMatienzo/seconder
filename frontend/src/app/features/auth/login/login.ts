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

  constructor(private fb: FormBuilder, private router: Router, private authService: AuthService) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });

    this.loginForm.valueChanges.subscribe(() => {
      if (this.errorMessage) {
        this.errorMessage = '';
      }
    });
  }

  iniciarSesion(): void {
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

          if (error instanceof HttpErrorResponse && error.status === 0) {
            this.errorMessage = 'No se pudo contactar al backend. Verifica que el servidor este en ejecucion.';
            return;
          }

          if (error instanceof HttpErrorResponse && error.status === 401) {
            this.errorMessage = 'Credenciales invalidas. Verifica tu correo y contrasena.';
            return;
          }

          if (error instanceof HttpErrorResponse) {
            this.errorMessage = 'No se pudo iniciar sesion. Intenta nuevamente en unos segundos.';
            return;
          }

          this.errorMessage = 'Ocurrio un error inesperado durante el inicio de sesion.';
        },
      });
  }
}
