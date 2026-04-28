import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:movil/data/models/emergency_case_model.dart';
import 'package:movil/domain/entities/emergency_case_entity.dart';
import 'package:movil/domain/repositories/emergency_repository.dart';
import 'package:movil/data/repositories/api_auth_repository.dart';
import 'package:geolocator/geolocator.dart';

class ApiEmergencyRepository implements EmergencyRepository {
  final String baseUrl = getBaseUrl();

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (ApiAuthRepository.accessToken != null)
      'Authorization': 'Bearer ${ApiAuthRepository.accessToken}',
  };

  @override
  Future<List<EmergencyCaseEntity>> getActiveCases() async {
    final response = await http.get(Uri.parse('$baseUrl/incidents/active'), headers: _headers);
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => EmergencyCaseModel.fromJson(e)).toList();
    }
    return [];
  }

  @override
  Future<void> createEmergencyAlert({
    required String vehiclePlate,
    required String description,
  }) async {
    // Usado por old flow, ignorado por el nuevo flujo que usa submitReport
  }

  Future<String?> _uploadFile(String filePath) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/upload'));
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      return data['file_url'];
    }
    return null;
  }

  @override
  Future<int> submitReport(
    String? imagePath,
    String? audioPath,
    String? optionalText,
    int vehicleId,
  ) async {
    // 1. Obtener ubicacion actual
    Position position = await Geolocator.getCurrentPosition();

    // 2. Crear incidente
    final incidentResponse = await http.post(
      Uri.parse('$baseUrl/incidents'),
      headers: _headers,
      body: jsonEncode({
        'id_vehicle': vehicleId,
        'latitude': position.latitude,
        'longitude': position.longitude,
        'description_text': optionalText,
        'photos': [],
        'audios': []
      }),
    );

    if (incidentResponse.statusCode != 201) {
      throw Exception('Error al crear incidente');
    }

    final incidentData = jsonDecode(incidentResponse.body);
    final incidentId = incidentData['id_incident'];

    if (imagePath != null) {
      final photoUrl = await _uploadFile(imagePath);
      if (photoUrl != null) {
        await http.post(
          Uri.parse('$baseUrl/incident-photos'),
          headers: _headers,
          body: jsonEncode({
            'id_incident': incidentId,
            'file_url': photoUrl,
          }),
        );
      }
    }

    // 4. Subir y adjuntar audio
    if (audioPath != null) {
      final audioUrl = await _uploadFile(audioPath);
      if (audioUrl != null) {
        await http.post(
          Uri.parse('$baseUrl/incident-audios'),
          headers: _headers,
          body: jsonEncode({
            'id_incident': incidentId,
            'file_url': audioUrl,
          }),
        );
      }
    }

    return incidentId;
  }

  Future<Map<String, dynamic>?> checkIncidentStatus(int incidentId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/client/incidents/$incidentId/status'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }
}
