import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:movil/domain/entities/vehicle.dart';
import 'package:movil/data/repositories/api_auth_repository.dart';

class ApiVehicleRepository {
  final String baseUrl = getBaseUrl();

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (ApiAuthRepository.accessToken != null)
      'Authorization': 'Bearer ${ApiAuthRepository.accessToken}',
  };

  Future<List<Vehicle>> getVehicles(String clientId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/clients/$clientId/vehicles'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Vehicle(
        id: json['id_vehicle'].toString(),
        brand: json['brand'] ?? 'Desconocida',
        model: json['model'] ?? 'Desconocido',
        plate: json['plate'] ?? 'XXX-000',
        year: json['year'] ?? 2000,
        color: json['color'] ?? 'Desconocido',
      )).toList();
    }
    return [];
  }

  Future<Vehicle> createVehicle(String clientId, Vehicle vehicle) async {
    final response = await http.post(
      Uri.parse('$baseUrl/vehicles'),
      headers: _headers,
      body: jsonEncode({
        'plate': vehicle.plate,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'year': vehicle.year,
        'color': vehicle.color,
      }),
    );

    if (response.statusCode == 201) {
      final json = jsonDecode(response.body);
      return Vehicle(
        id: json['id_vehicle'].toString(),
        brand: json['brand'] ?? vehicle.brand,
        model: json['model'] ?? vehicle.model,
        plate: json['plate'] ?? vehicle.plate,
        year: json['year'] ?? vehicle.year,
        color: json['color'] ?? vehicle.color,
      );
    }
    throw Exception('Error al crear vehiculo');
  }

  Future<void> deleteVehicle(String vehicleId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/vehicles/$vehicleId'),
      headers: _headers,
    );

    if (response.statusCode != 204 && response.statusCode != 200) {
      throw Exception('Error al eliminar vehiculo');
    }
  }
}
