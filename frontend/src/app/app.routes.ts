import { Routes } from '@angular/router';

// 1. Importamos tus componentes (¡Nota cómo le quitamos el .component al final de la ruta!)
import { Login } from './features/auth/login/login';
import { AdminLayout } from './features/admin/admin-layout/admin-layout';
import { Dashboard } from './features/admin/dashboard/dashboard';
import { Talleres } from './features/admin/talleres/talleres';
import { Clientes } from './features/admin/clientes/clientes';
import { AdminFinanzas } from './features/admin/admin-finanzas/admin-finanzas';
import { TallerLayout } from './features/taller/taller-layout/taller-layout';
import { TallerDashboard } from './features/taller/taller-dashboard/taller-dashboard';
import { TallerHistorial } from './features/taller/taller-historial/taller-historial';
import { TallerRecursos } from './features/taller/taller-recursos/taller-recursos';
import { TallerUbicacion } from './features/taller/taller-ubicacion/taller-ubicacion';

export const routes: Routes = [
  { path: 'login', component: Login },
  
  {
    path: 'admin',
    component: AdminLayout,
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'talleres', component: Talleres },
      { path: 'clientes', component: Clientes },
      { path: 'finanzas', component: AdminFinanzas },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },

  {
    path: 'taller',
    component: TallerLayout,
    children: [
      // Aquí irán las rutas hijas en el siguiente paso
      { path: 'dashboard', component: TallerDashboard },
      { path: 'historial', component: TallerHistorial },
      { path: 'recursos', component: TallerRecursos },
      { path: 'ubicacion', component: TallerUbicacion },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];