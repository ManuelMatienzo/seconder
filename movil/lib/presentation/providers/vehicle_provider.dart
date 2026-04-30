import 'package:flutter/material.dart';
import 'package:movil/domain/entities/vehicle.dart';
import 'package:movil/data/repositories/api_vehicle_repository.dart';

class VehicleProvider extends ChangeNotifier {
  VehicleProvider(this.apiVehicleRepository);

  final ApiVehicleRepository apiVehicleRepository;
  List<Vehicle> _vehicles = [];
  bool isLoading = false;
  
  List<Vehicle> get vehicles => List.unmodifiable(_vehicles);

  Future<void> loadVehicles(String clientId) async {
    isLoading = true;
    notifyListeners();
    try {
      _vehicles = await apiVehicleRepository.getVehicles(clientId);
    } catch (e) {
      // Ignorar error por ahora
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addVehicle(String clientId, Vehicle vehicle) async {
    try {
      final newVehicle = await apiVehicleRepository.createVehicle(clientId, vehicle);
      _vehicles = [..._vehicles, newVehicle];
      notifyListeners();
    } catch (e) {
      // Ignorar error por ahora
    }
  }

  Future<void> removeVehicle(String id) async {
    try {
      await apiVehicleRepository.deleteVehicle(id);
      _vehicles = _vehicles.where((v) => v.id != id).toList();
      notifyListeners();
    } catch (e) {
      // Ignorar error por ahora
    }
  }

  void updateVehicle(Vehicle updated) {
    _vehicles = _vehicles
        .map((v) => v.id == updated.id ? updated : v)
        .toList();
    notifyListeners();
  }
}
