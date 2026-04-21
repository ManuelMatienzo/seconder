import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CatalogoVehiculos } from './catalogo-vehiculos';

describe('CatalogoVehiculos', () => {
  let component: CatalogoVehiculos;
  let fixture: ComponentFixture<CatalogoVehiculos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CatalogoVehiculos],
    }).compileComponents();

    fixture = TestBed.createComponent(CatalogoVehiculos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
