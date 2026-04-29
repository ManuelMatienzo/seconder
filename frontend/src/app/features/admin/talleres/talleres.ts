import { CommonModule } from '@angular/common';
import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs';

import { TalleresService } from '../../../services/talleres.service';
import { WorkshopAccountCreateRequest, WorkshopResponse, WorkshopUpsertRequest } from '../../../models/workshop';

interface TallerForm {
  name: string;
  email: string;
  password: string;
  workshop_name: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  phone: string;
  specialties: string;
  is_available: boolean;
}

const DEFAULT_COORDINATES = {
  latitude: 0,
  longitude: 0,
};

const EMPTY_TALLER_FORM: TallerForm = {
  name: '',
  email: '',
  password: '',
  workshop_name: '',
  address: '',
  latitude: DEFAULT_COORDINATES.latitude,
  longitude: DEFAULT_COORDINATES.longitude,
  phone: '',
  specialties: '',
  is_available: true,
};

@Component({
  selector: 'app-talleres',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './talleres.html',
  styleUrl: './talleres.css',
})
export class Talleres {
  listaTalleres = signal<WorkshopResponse[]>([]);
  filtroNombre = signal('');
  isLoading = signal(false);
  errorMessage = signal('');
  isModalOpen = signal(false);
  isModalNuevoOpen = signal(false);
  showPassword = signal(false);
  tallerSeleccionado = signal<WorkshopResponse | null>(null);
  nuevoTaller = signal<TallerForm>({ ...EMPTY_TALLER_FORM });

  talleresFiltrados = computed(() => {
    const termino = this.filtroNombre().trim().toLowerCase();
    if (!termino) {
      return this.listaTalleres();
    }

    return this.listaTalleres().filter((taller) =>
      taller.workshop_name.toLowerCase().includes(termino)
    );
  });

  constructor(private talleresService: TalleresService) {}

  ngOnInit(): void {
    this.cargarTalleres();
  }

  cargarTalleres(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.talleresService
      .listWorkshops()
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (talleres) => this.listaTalleres.set(talleres),
        error: () => this.errorMessage.set('No se pudieron cargar los talleres.'),
      });
  }

  abrirModalNuevo() {
    this.errorMessage.set('');
    this.nuevoTaller.set({ ...EMPTY_TALLER_FORM });
    this.isModalNuevoOpen.set(true);
  }

  cerrarModalNuevo() {
    this.isModalNuevoOpen.set(false);
    this.nuevoTaller.set({ ...EMPTY_TALLER_FORM });
  }

  confirmarRegistro() {
    const payload = this.buildRegisterPayload(this.nuevoTaller());
    if (!payload) {
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.talleresService
      .createWorkshopAccount(payload)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (taller) => {
          this.listaTalleres.update((talleres) => [taller, ...talleres]);
          this.cerrarModalNuevo();
        },
        error: (err: HttpErrorResponse) => {
          if (err.error?.detail && typeof err.error.detail === 'string') {
            this.errorMessage.set(err.error.detail);
          } else if (err.status === 422) {
            this.errorMessage.set('Verifica que todos los campos sean validos (ej. correo valido, telefono correcto).');
          } else {
            this.errorMessage.set('No se pudo registrar el taller.');
          }
        },
      });
  }

  togglePasswordVisibility(): void {
    this.showPassword.update((visible) => !visible);
  }

  abrirEdicion(taller: WorkshopResponse) {
    this.errorMessage.set('');
    this.tallerSeleccionado.set({ ...taller });
    this.isModalOpen.set(true);
  }

  cerrarModal() {
    this.isModalOpen.set(false);
    this.tallerSeleccionado.set(null);
  }

  guardarCambios() {
    const editado = this.tallerSeleccionado();
    if (!editado) {
      return;
    }

    const payload = this.buildUpsertPayload(editado);
    if (!payload) {
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.talleresService
      .updateWorkshop(editado.id_user, payload)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (taller) => {
          this.listaTalleres.update((talleres) =>
            talleres.map((item) => (item.id_user === taller.id_user ? taller : item))
          );
          this.cerrarModal();
        },
        error: (err: HttpErrorResponse) => {
          if (err.error?.detail && typeof err.error.detail === 'string') {
            this.errorMessage.set(err.error.detail);
          } else if (err.status === 422) {
            this.errorMessage.set('Verifica que los datos ingresados sean validos.');
          } else {
            this.errorMessage.set('No se pudo actualizar el taller.');
          }
        },
      });
  }

  eliminarTaller(taller: WorkshopResponse) {
    if (!confirm(`¿Eliminar el taller ${taller.workshop_name}?`)) {
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.talleresService
      .deleteWorkshop(taller.id_user)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: () =>
          this.listaTalleres.update((talleres) =>
            talleres.filter((item) => item.id_user !== taller.id_user)
          ),
        error: () => this.errorMessage.set('No se pudo eliminar el taller.'),
      });
  }

  updateNuevoTallerField<K extends keyof TallerForm>(key: K, value: TallerForm[K]): void {
    this.nuevoTaller.update((current) => ({
      ...current,
      [key]: value,
    }));
  }

  updateSeleccionadoField<K extends keyof WorkshopResponse>(
    key: K,
    value: WorkshopResponse[K]
  ): void {
    this.tallerSeleccionado.update((current) => {
      if (!current) {
        return current;
      }

      return {
        ...current,
        [key]: value,
      } as WorkshopResponse;
    });
  }

  toNumber(value: unknown): number {
    return Number(value);
  }

  toNumberOrNull(value: unknown): number | null {
    if (value === '' || value === null || value === undefined) {
      return null;
    }

    const parsed = Number(value);
    return Number.isNaN(parsed) ? null : parsed;
  }

  private buildRegisterPayload(form: TallerForm): WorkshopAccountCreateRequest | null {
    const name = form.name.trim();
    const email = form.email.trim().toLowerCase();
    const password = form.password.trim();

    if (!name || !email || !password) {
      this.errorMessage.set('Nombre, correo y contrasena son obligatorios.');
      return null;
    }

    if (password.length < 8) {
      this.errorMessage.set('La contrasena debe tener al menos 8 caracteres.');
      return null;
    }

    const payload = this.buildUpsertPayload(form);
    if (!payload) {
      return null;
    }

    return {
      name,
      email,
      password,
      ...payload,
    };
  }

  private buildUpsertPayload(form: {
    workshop_name: string;
    address: string;
    latitude: number | null;
    longitude: number | null;
    phone: string | null | undefined;
    specialties: string | null | undefined;
    is_available: boolean;
  }): WorkshopUpsertRequest | null {
    const nombre = form.workshop_name.trim();
    const direccion = form.address.trim();
    const latitude = form.latitude ?? DEFAULT_COORDINATES.latitude;
    const longitude = form.longitude ?? DEFAULT_COORDINATES.longitude;

    if (!nombre || !direccion) {
      this.errorMessage.set('Nombre y direccion son obligatorios.');
      return null;
    }

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      this.errorMessage.set('La ubicacion del taller no es valida.');
      return null;
    }

    const phone = form.phone ? form.phone.trim() : '';
    const specialties = form.specialties ? form.specialties.trim() : '';

    return {
      workshop_name: nombre,
      address: direccion,
      latitude,
      longitude,
      phone: phone ? phone : null,
      specialties: specialties ? specialties : null,
      is_available: Boolean(form.is_available),
    };
  }
}
