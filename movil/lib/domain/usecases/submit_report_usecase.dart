import 'package:movil/domain/repositories/emergency_repository.dart';

class SubmitReportUseCase {
  const SubmitReportUseCase(this._repository);

  final EmergencyRepository _repository;

  Future<int> execute({
    String? imagePath,
    String? audioPath,
    String? optionalText,
    required int vehicleId,
  }) {
    return _repository.submitReport(imagePath, audioPath, optionalText, vehicleId);
  }
}
