import 'package:movil/domain/entities/emergency_case_entity.dart';

abstract class EmergencyRepository {
  Future<List<EmergencyCaseEntity>> getActiveCases();

  Future<void> createEmergencyAlert({
    required String vehiclePlate,
    required String description,
  });

  Future<int> submitReport(
    String? imagePath,
    String? audioPath,
    String? optionalText,
    int vehicleId,
  );
}
