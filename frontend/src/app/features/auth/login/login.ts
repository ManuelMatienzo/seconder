import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export class Login {
  loginForm: FormGroup;
  rolSeleccionado = signal<'ADMIN' | 'TALLER'>('ADMIN');

  constructor(private fb: FormBuilder, private router: Router) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  cambiarRol(rol: 'ADMIN' | 'TALLER'): void {
    this.rolSeleccionado.set(rol);
  }

  iniciarSesion(): void {
    if (this.loginForm.invalid) {
      console.error('Formulario inválido');
      return;
    }

    this.router.navigate(['/admin/dashboard']);
  }
}
