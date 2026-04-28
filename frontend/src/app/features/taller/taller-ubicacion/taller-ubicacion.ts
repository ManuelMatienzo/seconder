import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { finalize } from 'rxjs';

import { TalleresService } from '../../../services/talleres.service';
import { WorkshopResponse, WorkshopUpsertRequest } from '../../../models/workshop';

@Component({
  selector: 'app-taller-ubicacion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './taller-ubicacion.html',
  styleUrl: './taller-ubicacion.css'
})
export class TallerUbicacion implements OnInit {
  private talleresService = inject(TalleresService);
  private sanitizer = inject(DomSanitizer);

  workshop = signal<WorkshopResponse | null>(null);
  isLoading = signal(false);
  isUpdating = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  // Computed properties for easy access
  latitude = computed(() => this.workshop()?.latitude ?? 0);
  longitude = computed(() => this.workshop()?.longitude ?? 0);

  // Generates safe URL for the Google Maps iframe
  mapUrl = computed<SafeResourceUrl | null>(() => {
    const lat = this.latitude();
    const lng = this.longitude();
    if (lat === 0 && lng === 0) return null;
    
    const url = `https://maps.google.com/maps?q=${lat},${lng}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  });

  googleMapsLink = computed(() => {
    const lat = this.latitude();
    const lng = this.longitude();
    return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
  });

  ngOnInit(): void {
    this.cargarUbicacionActual();
  }

  cargarUbicacionActual(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    
    this.talleresService.getMyWorkshop()
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (ws) => this.workshop.set(ws),
        error: (err) => {
          if (err.status !== 404) {
            this.errorMessage.set('No se pudo cargar la información de tu ubicación actual.');
          }
        }
      });
  }

  recalibrarUbicacion(): void {
    this.errorMessage.set('');
    this.successMessage.set('');

    if (!navigator.geolocation) {
      this.errorMessage.set('La geolocalización no está soportada por tu navegador.');
      return;
    }

    this.isUpdating.set(true);
    
    // Configuración para pedir alta precisión si es posible
    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      (position) => this.actualizarCoordenadas(position.coords.latitude, position.coords.longitude),
      (error) => {
        this.isUpdating.set(false);
        this.manejarErrorGeolocalizacion(error);
      },
      options
    );
  }

  private actualizarCoordenadas(lat: number, lng: number): void {
    const currentWs = this.workshop();
    
    if (!currentWs) {
      // Auto-create workshop profile if it doesn't exist yet
      const authData = localStorage.getItem('auth_user');
      const userName = authData ? JSON.parse(authData).name : 'Taller Nuevo';
      
      const newPayload: WorkshopUpsertRequest = {
        workshop_name: `Taller ${userName}`,
        address: 'Ubicación GPS',
        latitude: lat,
        longitude: lng,
        phone: 'Sin teléfono',
        specialties: 'General',
        is_available: true
      };

      this.talleresService.registerMyWorkshop(newPayload)
        .pipe(finalize(() => this.isUpdating.set(false)))
        .subscribe({
          next: (createdWs) => {
            this.workshop.set(createdWs);
            this.successMessage.set('¡Taller activado y ubicación guardada correctamente!');
            setTimeout(() => this.successMessage.set(''), 5000);
          },
          error: () => this.errorMessage.set('Ocurrió un error al registrar el taller.')
        });
      return;
    }

    // Payload uses existing data, just updating latitude and longitude
    const payload: WorkshopUpsertRequest = {
      workshop_name: currentWs.workshop_name,
      address: currentWs.address,
      latitude: lat,
      longitude: lng,
      phone: currentWs.phone,
      specialties: currentWs.specialties,
      is_available: currentWs.is_available
    };

    this.talleresService.updateMyWorkshop(payload)
      .pipe(finalize(() => this.isUpdating.set(false)))
      .subscribe({
        next: (updatedWs) => {
          this.workshop.set(updatedWs);
          this.successMessage.set('¡Ubicación actualizada correctamente!');
          setTimeout(() => this.successMessage.set(''), 5000);
        },
        error: () => this.errorMessage.set('Ocurrió un error al guardar la nueva ubicación.')
      });
  }

  private manejarErrorGeolocalizacion(error: GeolocationPositionError): void {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        this.errorMessage.set('Permiso denegado. Debes permitir el acceso a la ubicación en tu navegador.');
        break;
      case error.POSITION_UNAVAILABLE:
        this.errorMessage.set('La información de ubicación no está disponible actualmente.');
        break;
      case error.TIMEOUT:
        this.errorMessage.set('La petición para obtener la ubicación ha caducado. Inténtalo de nuevo.');
        break;
      default:
        this.errorMessage.set('Ocurrió un error desconocido al obtener la ubicación.');
        break;
    }
  }
}
