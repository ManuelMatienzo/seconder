import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TallerHistorial } from './taller-historial';

describe('TallerHistorial', () => {
  let component: TallerHistorial;
  let fixture: ComponentFixture<TallerHistorial>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TallerHistorial],
    }).compileComponents();

    fixture = TestBed.createComponent(TallerHistorial);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
