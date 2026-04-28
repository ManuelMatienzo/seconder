import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { ClientesService } from '../../../services/clientes.service';
import {
  ClientAdminResponse,
  ClientRegisterRequest,
  ClientUpdateRequest,
} from '../../../models/client';

interface ClienteForm {
  name: string;
  email: string;
  password: string;
  phone: string;
}

const EMPTY_CLIENTE_FORM: ClienteForm = {
  name: '',
  email: '',
  password: '',
  phone: '',
};

@Component({
  selector: 'app-clientes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './clientes.html',
  styleUrl: './clientes.css',
})
export class Clientes implements OnInit {
  listaClientes = signal<ClientAdminResponse[]>([]);
  filtroNombre  = signal('');
  isLoading     = signal(false);
  errorMessage  = signal('');
  showPassword  = signal(false);

  isModalNuevoOpen   = signal(false);
  isModalEditarOpen  = signal(false);

  nuevoCliente      = signal<ClienteForm>({ ...EMPTY_CLIENTE_FORM });
  clienteSeleccionado = signal<ClientAdminResponse | null>(null);

  clientesFiltrados = computed(() => {
    const termino = this.filtroNombre().trim().toLowerCase();
    if (!termino) return this.listaClientes();
    return this.listaClientes().filter(c =>
      c.name.toLowerCase().includes(termino) ||
      c.email.toLowerCase().includes(termino)
    );
  });

  constructor(private clientesService: ClientesService) {}

  ngOnInit(): void {
    this.cargarClientes();
  }

  cargarClientes(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.clientesService
      .listClients()
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: clientes => this.listaClientes.set(clientes),
        error: () => this.errorMessage.set('No se pudieron cargar los clientes.'),
      });
  }

  // ── Modal Nuevo ──────────────────────────────────────────────
  abrirModalNuevo(): void {
    this.errorMessage.set('');
    this.nuevoCliente.set({ ...EMPTY_CLIENTE_FORM });
    this.isModalNuevoOpen.set(true);
  }

  cerrarModalNuevo(): void {
    this.isModalNuevoOpen.set(false);
    this.nuevoCliente.set({ ...EMPTY_CLIENTE_FORM });
  }

  confirmarRegistro(): void {
    const form = this.nuevoCliente();
    if (!form.name.trim() || !form.email.trim() || !form.password.trim()) {
      this.errorMessage.set('Nombre, correo y contraseña son obligatorios.');
      return;
    }
    if (form.password.length < 8) {
      this.errorMessage.set('La contraseña debe tener al menos 8 caracteres.');
      return;
    }

    const payload: ClientRegisterRequest = {
      name:     form.name.trim(),
      email:    form.email.trim().toLowerCase(),
      password: form.password,
      phone:    form.phone.trim() || null,
    };

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.clientesService
      .registerClient(payload)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: () => {
          this.cerrarModalNuevo();
          this.cargarClientes();
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.errorMessage.set(typeof detail === 'string' ? detail : 'No se pudo registrar el cliente.');
        },
      });
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(v => !v);
  }

  // ── Modal Editar ─────────────────────────────────────────────
  abrirEdicion(cliente: ClientAdminResponse): void {
    this.errorMessage.set('');
    this.clienteSeleccionado.set({ ...cliente });
    this.isModalEditarOpen.set(true);
  }

  cerrarModalEditar(): void {
    this.isModalEditarOpen.set(false);
    this.clienteSeleccionado.set(null);
  }

  updateSeleccionadoField<K extends keyof ClientAdminResponse>(key: K, value: ClientAdminResponse[K]): void {
    this.clienteSeleccionado.update(current => {
      if (!current) return current;
      return { ...current, [key]: value } as ClientAdminResponse;
    });
  }

  guardarCambios(): void {
    const cliente = this.clienteSeleccionado();
    if (!cliente) return;

    if (!cliente.name.trim() || !cliente.email.trim()) {
      this.errorMessage.set('Nombre y correo son obligatorios.');
      return;
    }

    const payload: ClientUpdateRequest = {
      name:  cliente.name.trim(),
      email: cliente.email.trim().toLowerCase(),
      phone: cliente.phone?.trim() || null,
    };

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.clientesService
      .updateClient(cliente.id_user, payload)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: updated => {
          this.listaClientes.update(list =>
            list.map(c => (c.id_user === updated.id_user ? updated : c))
          );
          this.cerrarModalEditar();
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.errorMessage.set(typeof detail === 'string' ? detail : 'No se pudo actualizar el cliente.');
        },
      });
  }

  // ── Eliminar ─────────────────────────────────────────────────
  eliminarCliente(cliente: ClientAdminResponse): void {
    if (!confirm(`¿Eliminar al cliente ${cliente.name}? Esta acción también eliminará su cuenta.`)) return;

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.clientesService
      .deleteClient(cliente.id_user)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: () =>
          this.listaClientes.update(list => list.filter(c => c.id_user !== cliente.id_user)),
        error: () => this.errorMessage.set('No se pudo eliminar el cliente.'),
      });
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('es-BO', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  }
}
