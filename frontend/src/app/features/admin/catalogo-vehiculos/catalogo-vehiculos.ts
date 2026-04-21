import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

// Definimos la estructura de datos para la IA
export interface VehiculoSoportado {
  id: number;
  marca: string;
  modelo: string;
  categoria: string; // Ej: Sedán, SUV, Camioneta
  anioBase: string; // Desde qué año el modelo tiene esa forma
  estado: 'Activo' | 'Inactivo';
}

@Component({
  selector: 'app-catalogo-vehiculos',
  standalone: true,
  imports: [FormsModule], // Fundamental para el [(ngModel)] del formulario
  templateUrl: './catalogo-vehiculos.html',
})
export class CatalogoVehiculos {
  // Lista inicial (El diccionario de la IA)
  listaVehiculos = signal<VehiculoSoportado[]>([
    { id: 1, marca: 'Toyota', modelo: 'Hilux', categoria: 'Camioneta', anioBase: '2016+', estado: 'Activo' },
    { id: 2, marca: 'Suzuki', modelo: 'Swift', categoria: 'Hatchback', anioBase: '2018+', estado: 'Activo' },
    { id: 3, marca: 'Nissan', modelo: 'Frontier', categoria: 'Camioneta', anioBase: '2015+', estado: 'Activo' },
    { id: 4, marca: 'Honda', modelo: 'Civic', categoria: 'Sedán', anioBase: '2017+', estado: 'Activo' }
  ]);

  // Control del modal
  isModalOpen = signal(false);
  
  // Objeto temporal para el formulario
  nuevoVehiculo: Partial<VehiculoSoportado> = {};

  abrirModal() {
    this.nuevoVehiculo = { estado: 'Activo' }; // Valores por defecto
    this.isModalOpen.set(true);
  }

  cerrarModal() {
    this.isModalOpen.set(false);
  }

  guardarVehiculo() {
    if (!this.nuevoVehiculo.marca || !this.nuevoVehiculo.modelo) return; // Validación básica

    const vehiculoCompleto: VehiculoSoportado = {
      id: Date.now(),
      marca: this.nuevoVehiculo.marca,
      modelo: this.nuevoVehiculo.modelo,
      categoria: this.nuevoVehiculo.categoria || 'No definida',
      anioBase: this.nuevoVehiculo.anioBase || '2000+',
      estado: 'Activo'
    };

    // Actualizamos la lista
    this.listaVehiculos.update(lista => [...lista, vehiculoCompleto]);
    this.cerrarModal();
  }

  cambiarEstado(vehiculo: VehiculoSoportado) {
    vehiculo.estado = vehiculo.estado === 'Activo' ? 'Inactivo' : 'Activo';
  }
}