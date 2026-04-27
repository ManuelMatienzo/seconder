import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { provideRouter } from '@angular/router';

import { Login } from './login';
import { AuthService } from '../../../services/auth.service';

describe('Login', () => {
  let component: Login;
  let fixture: ComponentFixture<Login>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: {
            login: () => of({
              message: 'Login correcto',
              access_token: 'token',
              token_type: 'bearer',
              user: {
                id_user: 1,
                name: 'Admin',
                email: 'admin@demo.com',
                phone: null,
                status: 'activo',
                created_at: '2026-01-01T00:00:00Z',
                updated_at: '2026-01-01T00:00:00Z',
                id_role: 1,
                role: { id_role: 1, name: 'admin', description: null }
              }
            }),
            saveSession: () => undefined,
            resolveHomeRoute: () => '/admin/dashboard'
          }
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Login);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
