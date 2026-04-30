import { Component, OnInit, OnDestroy, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { OperationsService } from '../../../services/operations.service';
import { TechnicianService } from '../../../services/technician.service';
import { AvailableRequestResponse, AssignmentHistoryItemResponse, AssignmentTrackingResponse } from '../../../models/operations';
import { TechnicianResponse } from '../../../models/technician';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-taller-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-dashboard.html'
})
export class TallerDashboard implements OnInit, OnDestroy {
  private opsService = inject(OperationsService);
  private techService = inject(TechnicianService);
  private realtimeSocket?: WebSocket;
  private reconnectTimer?: number;
  private toastTimer?: number;

  // States
  nuevasSolicitudes = signal<AvailableRequestResponse[]>([]);
  casosActivos = signal<AssignmentHistoryItemResponse[]>([]);
  tecnicosDisponibles = signal<TechnicianResponse[]>([]);
  
  isLoadingNuevas = signal(false);
  isLoadingActivos = signal(false);

  // Modals / Details
  isModalOpen = signal(false);
  solicitudSeleccionada = signal<any | null>(null);
  isCaseActive = signal(false);

  // Toast
  toastMessage = signal<string | null>(null);

  // Tracking Active Case Details
  activeTracking = signal<{ [incidentId: number]: AssignmentTrackingResponse }>({});

  // Mecanico for the evaluation modal
  mecanicoModalSeleccionado = signal<number | null>(null);

  ngOnInit(): void {
    this.cargarNuevasSolicitudes();
    this.cargarCasosActivos();
    this.cargarTecnicos();
    this.startRealtime();

    // Polling every 15 seconds to look for new assignments and active case status changes
    setInterval(() => {
      this.cargarNuevasSolicitudes(true);
      this.cargarCasosActivos(true);
    }, 15000);
  }

  ngOnDestroy(): void {
    this.stopRealtime();
    this.clearToastTimer();
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

  cargarCasosActivos(isPolling = false) {
    if (!isPolling) {
      this.isLoadingActivos.set(true);
    }
    // Fetch all history but filter out completed/cancelled/rejected in UI or backend
    this.opsService.getHistory()
      .pipe(finalize(() => this.isLoadingActivos.set(false)))
      .subscribe({
        next: (data) => {
          console.log("Historial recibido:", data);
          const activos = data.filter(d => (
            d.status === 'aceptado' || 
            d.status === 'alistando' || 
            d.status === 'en_ruta' || 
            d.status === 'en_sitio' ||
            d.status === 'completado'
          ) && d.payment_status !== 'completado');
          console.log("Casos activos filtrados:", activos);
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

  abrirEvaluacion(solicitud: any, isActive = false) {
    this.solicitudSeleccionada.set(solicitud);
    this.isCaseActive.set(isActive);
    this.mecanicoModalSeleccionado.set(null);
    this.isModalOpen.set(true);
  }

  cerrarModal() {
    this.isModalOpen.set(false);
    this.solicitudSeleccionada.set(null);
    this.isCaseActive.set(false);
    this.mecanicoModalSeleccionado.set(null);
  }

  decidirSolicitud(incidentId: number, decision: 'aceptado' | 'rechazado') {
    if (decision === 'aceptado' && !this.mecanicoModalSeleccionado()) {
      alert("Debes asignar un mecánico antes de aceptar el servicio.");
      return;
    }

    this.opsService.decideRequest(incidentId, decision).subscribe({
      next: () => {
        if (decision === 'aceptado') {
          // Si se aceptó, inmediatamente encadenar la asignación del mecánico
          const id_technician = this.mecanicoModalSeleccionado()!;
          this.opsService.updateTracking(incidentId, { id_technician }).subscribe({
            next: () => {
              this.cerrarModal();
              this.cargarNuevasSolicitudes();
              this.cargarCasosActivos();
            },
            error: () => alert("Servicio aceptado, pero hubo un error al asignar el mecánico.")
          });
        } else {
          this.cerrarModal();
          this.cargarNuevasSolicitudes();
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

  private startRealtime() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return;
    }

    const wsUrl = this.buildWsUrl(`${environment.apiUrl}/ws/notifications?token=${token}`);
    this.realtimeSocket = new WebSocket(wsUrl);

    this.realtimeSocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'new_request') {
          this.cargarNuevasSolicitudes(true);
          const clientName = payload.client_name as string | undefined;
          const message = clientName
            ? `Nueva solicitud de ${clientName}`
            : 'Nueva solicitud recibida';
          this.showToast(message);
        }
      } catch {
        // Ignorar mensajes no JSON
      }
    };

    this.realtimeSocket.onerror = () => {
      this.realtimeSocket?.close();
    };

    this.realtimeSocket.onclose = () => {
      this.reconnectTimer = window.setTimeout(() => this.startRealtime(), 3000);
    };
  }

  private stopRealtime() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
    this.realtimeSocket?.close();
    this.realtimeSocket = undefined;
  }

  private buildWsUrl(url: string): string {
    return url.replace(/^http/, 'ws');
  }

  private showToast(message: string) {
    this.toastMessage.set(message);
    this.clearToastTimer();
    this.toastTimer = window.setTimeout(() => {
      this.toastMessage.set(null);
    }, 3500);
  }

  private clearToastTimer() {
    if (this.toastTimer) {
      window.clearTimeout(this.toastTimer);
      this.toastTimer = undefined;
    }
  }
}