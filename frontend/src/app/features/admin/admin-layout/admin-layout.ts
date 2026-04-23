import { Component, inject, signal } from '@angular/core'; // Añadimos signal
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
//yea
@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive], 
  templateUrl: './admin-layout.html',
})
export class AdminLayout {
  private router = inject(Router);
  
  // 1. Creamos la señal para controlar el menú (empieza cerrado en móviles)
  isSidebarOpen = signal(false);

  // 2. Función para abrir/cerrar el menú
  toggleSidebar() {
    this.isSidebarOpen.update(val => !val);
  }

  // 3. Función para cerrar el menú si hacen clic en un enlace (útil en móviles)
  closeSidebar() {
    this.isSidebarOpen.set(false);
  }

  cerrarSesion() {
    this.router.navigate(['/login']);
  }
}