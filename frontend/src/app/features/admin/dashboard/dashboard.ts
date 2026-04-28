import { Component, OnInit, signal, computed } from '@angular/core';
import { finalize } from 'rxjs';
import { TalleresService } from '../../../services/talleres.service';
import { WorkshopResponse } from '../../../models/workshop';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private talleres = signal<WorkshopResponse[]>([]);

  talleresEnLinea = computed(() => this.talleres().filter(t => t.is_available).length);
  talleresTotal   = computed(() => this.talleres().length);
  isLoadingStats  = signal(false);

  constructor(private talleresService: TalleresService) {}

  ngOnInit(): void {
    this.isLoadingStats.set(true);
    this.talleresService
      .listWorkshops()
      .pipe(finalize(() => this.isLoadingStats.set(false)))
      .subscribe({
        next: lista => this.talleres.set(lista),
        error: ()   => { /* tarjeta mantiene 0/0 si falla */ },
      });
  }
}
