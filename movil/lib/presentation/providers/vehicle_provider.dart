import 'package:flutter/material.dart';
import 'package:movil/domain/entities/vehicle.dart';

class VehicleProvider extends ChangeNotifier {
  VehicleProvider() : _vehicles = _initialVehicles();

  List<Vehicle> _vehicles;

  List<Vehicle> get vehicles => List.unmodifiable(_vehicles);

  // ── Seed data de prueba ──────────────────────────────────────────────

  static List<Vehicle> _initialVehicles() => [
        const Vehicle(
          id: 'v-001',
          brand: 'Toyota',
          model: 'Corolla',
          plate: 'ABC-1234',
          year: 2020,
          color: 'Blanco',
        ),
        const Vehicle(
          id: 'v-002',
          brand: 'Suzuki',
          model: 'Jimny',
          plate: 'XYZ-5678',
          year: 2022,
          color: 'Verde',
        ),
      ];

  // ── Operaciones CRUD ─────────────────────────────────────────────────

  void addVehicle(Vehicle vehicle) {
    _vehicles = [..._vehicles, vehicle];
    notifyListeners();
  }

  void removeVehicle(String id) {
    _vehicles = _vehicles.where((v) => v.id != id).toList();
    notifyListeners();
  }

  void updateVehicle(Vehicle updated) {
    _vehicles = _vehicles
        .map((v) => v.id == updated.id ? updated : v)
        .toList();
    notifyListeners();
  }
}
