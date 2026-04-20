import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Taller {
  nombre: string;
  email: string;
  especialidad: string;
  tieneGrua: boolean;
  estado: 'Activo' | 'Pendiente' | 'Suspendido';
  comision: number;
}

@Component({
  selector: 'app-talleres',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './talleres.html',
  styleUrl: './talleres.css',
})
export class Talleres {
  listaTalleres = signal<Taller[]>([
    { nombre: 'Taller 1', email: 'taller1@example.com', especialidad: 'Frenos', tieneGrua: true, estado: 'Activo', comision: 10 },
    { nombre: 'Taller 2', email: 'taller2@example.com', especialidad: 'Motor', tieneGrua: false, estado: 'Pendiente', comision: 15 },
    { nombre: 'Taller 3', email: 'taller3@example.com', especialidad: 'Suspensión', tieneGrua: true, estado: 'Suspendido', comision: 8 },
    { nombre: 'Taller 4', email: 'taller4@example.com', especialidad: 'Electricidad', tieneGrua: false, estado: 'Activo', comision: 12 },
    { nombre: 'Taller 5', email: 'taller5@example.com', especialidad: 'Pintura', tieneGrua: true, estado: 'Pendiente', comision: 20 },
    { nombre: 'Taller 6', email: 'taller6@example.com', especialidad: 'Alineación', tieneGrua: false, estado: 'Activo', comision: 9 },
    { nombre: 'Taller 7', email: 'taller7@example.com', especialidad: 'Transmisión', tieneGrua: true, estado: 'Suspendido', comision: 14 },
    { nombre: 'Taller 8', email: 'taller8@example.com', especialidad: 'Llantas', tieneGrua: false, estado: 'Pendiente', comision: 11 },
    { nombre: 'Taller 9', email: 'taller9@example.com', especialidad: 'Diagnóstico', tieneGrua: true, estado: 'Activo', comision: 13 },
    { nombre: 'Taller 10', email: 'taller10@example.com', especialidad: 'Inyección', tieneGrua: false, estado: 'Pendiente', comision: 16 },
    { nombre: 'Taller 11', email: 'taller11@example.com', especialidad: 'Frenos', tieneGrua: true, estado: 'Activo', comision: 10 },
    { nombre: 'Taller 12', email: 'taller12@example.com', especialidad: 'Motor', tieneGrua: false, estado: 'Suspendido', comision: 18 },
    { nombre: 'Taller 13', email: 'taller13@example.com', especialidad: 'Suspensión', tieneGrua: true, estado: 'Pendiente', comision: 7 },
    { nombre: 'Taller 14', email: 'taller14@example.com', especialidad: 'Electricidad', tieneGrua: false, estado: 'Activo', comision: 12 },
    { nombre: 'Taller 15', email: 'taller15@example.com', especialidad: 'Pintura', tieneGrua: true, estado: 'Suspendido', comision: 19 },
    { nombre: 'Taller 16', email: 'taller16@example.com', especialidad: 'Alineación', tieneGrua: false, estado: 'Pendiente', comision: 10 },
    { nombre: 'Taller 17', email: 'taller17@example.com', especialidad: 'Transmisión', tieneGrua: true, estado: 'Activo', comision: 15 },
    { nombre: 'Taller 18', email: 'taller18@example.com', especialidad: 'Llantas', tieneGrua: false, estado: 'Suspendido', comision: 8 },
    { nombre: 'Taller 19', email: 'taller19@example.com', especialidad: 'Diagnóstico', tieneGrua: true, estado: 'Activo', comision: 11 },
    { nombre: 'Taller 20', email: 'taller20@example.com', especialidad: 'Inyección', tieneGrua: false, estado: 'Pendiente', comision: 17 },
  ]);

  isModalOpen = signal(false);
  tallerSeleccionado = signal<Taller | null>(null);
  comisionGlobal = signal(10);
  isModalNuevoOpen = signal(false);
  nuevoTaller = signal<Omit<Taller, 'comision'> & { comision?: number; password?: string }>({
    nombre: '',
    email: '',
    especialidad: '',
    tieneGrua: false,
    estado: 'Pendiente',
    comision: 10,
  });

  abrirModalNuevo() {
    this.nuevoTaller.set({
      nombre: '',
      email: '',
      especialidad: '',
      tieneGrua: false,
      estado: 'Pendiente',
      comision: this.comisionGlobal(),
    });
    this.isModalNuevoOpen.set(true);
  }

  cerrarModalNuevo() {
    this.isModalNuevoOpen.set(false);
    this.nuevoTaller.set({
      nombre: '',
      email: '',
      especialidad: '',
      tieneGrua: false,
      estado: 'Pendiente',
      comision: this.comisionGlobal(),
    });
  }

  confirmarRegistro() {
    const nuevo = this.nuevoTaller();
    if (nuevo.nombre && nuevo.email && nuevo.especialidad) {
      const tallerCompleto: Taller = {
        nombre: nuevo.nombre,
        email: nuevo.email,
        especialidad: nuevo.especialidad,
        tieneGrua: nuevo.tieneGrua,
        estado: nuevo.estado as 'Activo' | 'Pendiente' | 'Suspendido',
        comision: nuevo.comision ?? this.comisionGlobal(),
      };
      this.listaTalleres.update(talleres => [...talleres, tallerCompleto]);
      this.cerrarModalNuevo();
    }
  }

  abrirEdicion(taller: Taller) {
    this.tallerSeleccionado.set({ ...taller });
    this.isModalOpen.set(true);
  }

  cerrarModal() {
    this.isModalOpen.set(false);
    this.tallerSeleccionado.set(null);
  }

  guardarCambios() {
    const editado = this.tallerSeleccionado();
    if (editado) {
      this.listaTalleres.update(talleres => {
        const index = talleres.findIndex(t => t.email === editado.email);
        if (index > -1) {
          const nuevaLista = [...talleres];
          nuevaLista[index] = editado;
          return nuevaLista;
        } else {
          return [...talleres, editado];
        }
      });
    }
    this.cerrarModal();
  }
}
