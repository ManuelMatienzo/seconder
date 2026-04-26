import 'package:movil/data/models/emergency_case_model.dart';
import 'package:movil/domain/entities/emergency_case_entity.dart';
import 'package:movil/domain/repositories/emergency_repository.dart';

class MockEmergencyRepository implements EmergencyRepository {
  final List<EmergencyCaseModel> _cases = [
    EmergencyCaseModel(
      id: '1',
      caseCode: 'CASO-07',
      status: 'PENDIENTE',
      location: 'Av. Independencia 1430',
      summary: 'Choque lateral con posible lesion leve.',
      reportedAt: DateTime(2026, 4, 23, 10, 20),
      gpsActive: true,
    ),
    EmergencyCaseModel(
      id: '2',
      caseCode: 'CASO-11',
      status: 'EN PROCESO',
      location: 'Circunvalacion Km 5',
      summary: 'Vehiculo detenido bloqueando carril derecho.',
      reportedAt: DateTime(2026, 4, 23, 9, 45),
      gpsActive: true,
    ),
  ];

  int _nextId = 3;

  @override
  Future<void> createEmergencyAlert({
    required String vehiclePlate,
    required String description,
  }) async {
    await Future.delayed(const Duration(milliseconds: 900));

    final safePlate = vehiclePlate.trim().isEmpty
        ? 'SIN-PLACA'
        : vehiclePlate.trim();

    _cases.insert(
      0,
      EmergencyCaseModel(
        id: _nextId.toString(),
        caseCode: 'CASO-${_nextId.toString().padLeft(2, '0')}',
        status: 'PENDIENTE',
        location: 'Ubicacion enviada desde app movil',
        summary: '$safePlate - ${description.trim()}',
        reportedAt: DateTime.now(),
        gpsActive: true,
      ),
    );

    _nextId += 1;
  }

  @override
  Future<List<EmergencyCaseEntity>> getActiveCases() async {
    await Future.delayed(const Duration(milliseconds: 800));
    return List<EmergencyCaseEntity>.unmodifiable(_cases);
  }

  @override
  Future<void> submitReport(
    String? imagePath,
    String? audioPath,
    String? optionalText,
  ) async {
    await Future.delayed(const Duration(seconds: 3));
  }
}
