import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { TechnicianService } from '../../../services/technician.service';
import { TechnicianResponse, TechnicianCreateRequest, TechnicianUpdateRequest } from '../../../models/technician';

@Component({
  selector: 'app-taller-recursos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './taller-recursos.html'
})
export class TallerRecursos implements OnInit {
  private technicianService = inject(TechnicianService);
  private fb = inject(FormBuilder);

  // State
  technicians = signal<TechnicianResponse[]>([]);
  isLoading = signal(false);
  errorMessage = signal('');
  
  // Modal State
  isModalOpen = signal(false);
  isSubmitting = signal(false);
  modalMode = signal<'CREATE' | 'EDIT'>('CREATE');
  editingId = signal<number | null>(null);

  recursoForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(3)]],
    phone: [''],
    specialty: ['']
  });

  ngOnInit(): void {
    this.cargarRecursos();
  }

  cargarRecursos(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.technicianService.listTechnicians()
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (data) => this.technicians.set(data),
        error: (err) => {
          if (err.status !== 404) {
            this.errorMessage.set('Error al cargar la lista de recursos.');
          }
        }
      });
  }

  abrirModalNuevo(): void {
    this.modalMode.set('CREATE');
    this.editingId.set(null);
    this.recursoForm.reset();
    this.isModalOpen.set(true);
  }

  abrirModalEditar(tech: TechnicianResponse): void {
    this.modalMode.set('EDIT');
    this.editingId.set(tech.id_technician);
    this.recursoForm.patchValue({
      name: tech.name,
      phone: tech.phone,
      specialty: tech.specialty
    });
    this.isModalOpen.set(true);
  }

  cerrarModal(): void {
    this.isModalOpen.set(false);
  }

  guardarRecurso(): void {
    if (this.recursoForm.invalid) {
      this.recursoForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set('');
    
    const formValue = this.recursoForm.value;

    if (this.modalMode() === 'CREATE') {
      const payload: TechnicianCreateRequest = {
        name: formValue.name,
        phone: formValue.phone || null,
        specialty: formValue.specialty || null,
        is_available: true // By default
      };

      this.technicianService.createTechnician(payload)
        .pipe(finalize(() => this.isSubmitting.set(false)))
        .subscribe({
          next: () => {
            this.cerrarModal();
            this.cargarRecursos();
          },
          error: (err) => {
            if (err.status === 404) {
              this.errorMessage.set('Debes configurar tu Ubicación GPS primero para activar tu taller.');
            } else {
              this.errorMessage.set('Error al crear el recurso.');
            }
          }
        });

    } else {
      const id = this.editingId();
      if (!id) return;

      const payload: TechnicianUpdateRequest = {
        name: formValue.name,
        phone: formValue.phone || null,
        specialty: formValue.specialty || null
      };

      this.technicianService.updateTechnician(id, payload)
        .pipe(finalize(() => this.isSubmitting.set(false)))
        .subscribe({
          next: () => {
            this.cerrarModal();
            this.cargarRecursos();
          },
          error: () => this.errorMessage.set('Error al actualizar el recurso.')
        });
    }
  }

  toggleDisponibilidad(tech: TechnicianResponse): void {
    const newStatus = !tech.is_available;
    // Optimistic update
    this.technicians.update(list => list.map(t => t.id_technician === tech.id_technician ? { ...t, is_available: newStatus } : t));
    
    this.technicianService.updateAvailability(tech.id_technician, { is_available: newStatus })
      .subscribe({
        error: () => {
          // Revert on error
          this.technicians.update(list => list.map(t => t.id_technician === tech.id_technician ? { ...t, is_available: !newStatus } : t));
          this.errorMessage.set('Error al cambiar la disponibilidad.');
        }
      });
  }
}