import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EmergencyService {
  private url = `${environment.apiUrl}/emergencias`; // Ajusta segun tus rutas de FastAPI

  constructor(private http: HttpClient) { }

  // Ejemplo: Obtener lista de incidentes
  getEmergencias() {
    return this.http.get(this.url);
  }
}
