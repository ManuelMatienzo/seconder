import { Component, OnInit, signal, inject, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { OperationsService } from '../../../services/operations.service';
import { TechnicianService } from '../../../services/technician.service';
import { AvailableRequestResponse, AssignmentHistoryItemResponse, AssignmentTrackingResponse } from '../../../models/operations';
import { TechnicianResponse } from '../../../models/technician';

@Component({
  selector: 'app-taller-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-dashboard.html'
})
export class TallerDashboard implements OnInit {
  private opsService = inject(OperationsService);
  private techService = inject(TechnicianService);

  // States
  nuevasSolicitudes = signal<AvailableRequestResponse[]>([]);
  casosActivos = signal<AssignmentHistoryItemResponse[]>([]);
  tecnicosDisponibles = signal<TechnicianResponse[]>([]);
  
  isLoadingNuevas = signal(false);
  isLoadingActivos = signal(false);

  // Modals / Details
  isModalOpen = signal(false);
  solicitudSeleccionada = signal<AvailableRequestResponse | null>(null);

  // Tracking Active Case Details
  activeTracking = signal<{ [incidentId: number]: AssignmentTrackingResponse }>({});

  ngOnInit(): void {
    this.cargarNuevasSolicitudes();
    this.cargarCasosActivos();
    this.cargarTecnicos();

    // Polling every 15 seconds to look for new assignments
    setInterval(() => {
      this.cargarNuevasSolicitudes(true);
    }, 15000);
  }

  cargarNuevasSolicitudes(isPolling = false) {
    if (!isPolling) {
      this.isLoadingNuevas.set(true);
    }
    
    this.opsService.getAvailableRequests()
      .pipe(finalize(() => this.isLoadingNuevas.set(false)))
      .subscribe({
        next: (data) => this.nuevasSolicitudes.set(data),
        error: (err) => console.error("Error cargando nuevas solicitudes:", err)
      });
  }

  cargarCasosActivos() {
    this.isLoadingActivos.set(true);
    // Fetch all history but filter out completed/cancelled/rejected in UI or backend
    this.opsService.getHistory()
      .pipe(finalize(() => this.isLoadingActivos.set(false)))
      .subscribe({
        next: (data) => {
          const activos = data.filter(d => 
            d.status === 'aceptado' || 
            d.status === 'alistando' || 
            d.status === 'en_ruta' || 
            d.status === 'en_sitio'
          );
          this.casosActivos.set(activos);
          // Load detailed tracking for each active case
          activos.forEach(caso => this.loadTrackingDetail(caso.id_incident));
        },
        error: (err) => console.error("Error cargando casos activos:", err)
      });
  }

  cargarTecnicos() {
    this.techService.listTechnicians().subscribe({
      next: (data) => this.tecnicosDisponibles.set(data)
    });
  }

  loadTrackingDetail(incidentId: number) {
    this.opsService.getTracking(incidentId).subscribe({
      next: (data) => {
        this.activeTracking.update(current => ({...current, [incidentId]: data}));
      }
    });
  }

  abrirEvaluacion(solicitud: AvailableRequestResponse) {
    this.solicitudSeleccionada.set(solicitud);
    this.isModalOpen.set(true);
  }

  cerrarModal() {
    this.isModalOpen.set(false);
    this.solicitudSeleccionada.set(null);
  }

  decidirSolicitud(incidentId: number, decision: 'aceptado' | 'rechazado') {
    this.opsService.decideRequest(incidentId, decision).subscribe({
      next: () => {
        this.cerrarModal();
        this.cargarNuevasSolicitudes();
        if (decision === 'aceptado') {
          this.cargarCasosActivos();
        }
      },
      error: (err) => alert("Error al procesar la solicitud.")
    });
  }

  asignarTecnico(incidentId: number, technicianIdStr: string) {
    if (!technicianIdStr) return;
    const id_technician = Number(technicianIdStr);
    this.opsService.updateTracking(incidentId, { id_technician }).subscribe({
      next: (data) => {
        this.activeTracking.update(current => ({...current, [incidentId]: data}));
        this.cargarCasosActivos(); // Refresh history names
        this.cargarTecnicos(); // Refresh availability
      },
      error: (err) => alert("Error al asignar técnico.")
    });
  }

  avanzarEstado(incidentId: number, nuevoEstado: string) {
    this.opsService.updateTracking(incidentId, { status: nuevoEstado }).subscribe({
      next: (data) => {
        this.activeTracking.update(current => ({...current, [incidentId]: data}));
        this.cargarCasosActivos();
        this.cargarTecnicos(); // If completed, technician becomes available again
      },
      error: (err) => {
        // Most likely the user tried to go to en_ruta without a technician
        if (err.status === 409) {
          alert("Asegúrate de asignar un mecánico antes de despachar en ruta.");
        } else {
          alert("Error al avanzar de estado.");
        }
      }
    });
  }
}