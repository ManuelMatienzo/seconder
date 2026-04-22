import { Component, signal } from '@angular/core';

export interface ServicioHistorico {
  id: string;
  fecha: string;
  cliente: string;
  vehiculo: string;
  tipoEmergencia: string;
  costo: number;
  estado: 'Completado' | 'Cancelado';
  diagnosticoIA: string;
}

@Component({
  selector: 'app-taller-historial',
  standalone: true,
  templateUrl: './taller-historial.html'
})
export class TallerHistorial {
  // Simulamos la base de datos de servicios previos
  historial = signal<ServicioHistorico[]>([
    {
      id: 'SRV-8890',
      fecha: '18 Abr 2026 · 14:30',
      cliente: 'Carlos Mendoza',
      vehiculo: 'Toyota Hilux 2021',
      tipoEmergencia: 'Cambio de Batería',
      costo: 350.00,
      estado: 'Completado',
      diagnosticoIA: 'Voltaje inferior a 11.5V detectado. Batería reemplazada exitosamente in situ.'
    },
    {
      id: 'SRV-8885',
      fecha: '17 Abr 2026 · 09:15',
      cliente: 'Ana Suárez',
      vehiculo: 'Nissan Sentra 2018',
      tipoEmergencia: 'Falla de Motor (Temperatura)',
      costo: 1200.00,
      estado: 'Completado',
      diagnosticoIA: 'Fuga en manguera del radiador confirmada por imagen. Vehículo remolcado y reparado en taller.'
    },
    {
      id: 'SRV-8882',
      fecha: '15 Abr 2026 · 22:45',
      cliente: 'Roberto Gómez',
      vehiculo: 'Suzuki Swift 2022',
      tipoEmergencia: 'Pinchazo Múltiple',
      costo: 0,
      estado: 'Cancelado',
      diagnosticoIA: 'Dos neumáticos comprometidos. Cliente canceló la solicitud al conseguir ayuda particular.'
    }
  ]);
}