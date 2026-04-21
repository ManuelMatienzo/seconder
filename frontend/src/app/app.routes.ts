import { Routes } from '@angular/router';

// 1. Importamos tus componentes (¡Nota cómo le quitamos el .component al final de la ruta!)
import { Login } from './features/auth/login/login'; // (Si tu login sí tiene el .component, déjalo así)
import { AdminLayout } from './features/admin/admin-layout/admin-layout';
import { Dashboard } from './features/admin/dashboard/dashboard';
import { Talleres } from './features/admin/talleres/talleres';
import { CatalogoVehiculos } from './features/admin/catalogo-vehiculos/catalogo-vehiculos';

export const routes: Routes = [
  { path: 'login', component: Login },
  
  {
    path: 'admin',
    component: AdminLayout,
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'talleres', component: Talleres },
      { path: 'vehiculos', component: CatalogoVehiculos },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];