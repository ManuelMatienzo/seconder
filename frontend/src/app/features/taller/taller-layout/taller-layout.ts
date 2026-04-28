import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-taller-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './taller-layout.html'
})
export class TallerLayout {
  private router = inject(Router);
  private authService = inject(AuthService);

  isMobileMenuOpen = signal(false);

  private authUser = JSON.parse(localStorage.getItem('auth_user') ?? 'null');

  userName     = this.authUser?.name  ?? 'Usuario';
  userEmail    = this.authUser?.email ?? '';
  userInitials = this.userName
    .split(' ')
    .slice(0, 2)
    .map((w: string) => w.charAt(0).toUpperCase())
    .join('');

  toggleMenu() {
    this.isMobileMenuOpen.update(v => !v);
  }

  cerrarMenu() {
    this.isMobileMenuOpen.set(false);
  }

  cerrarSesion() {
    this.authService.clearSession();
    this.router.navigate(['/login']);
  }
}