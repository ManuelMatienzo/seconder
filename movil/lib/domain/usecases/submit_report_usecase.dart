import 'package:movil/domain/repositories/emergency_repository.dart';

class SubmitReportUseCase {
  const SubmitReportUseCase(this._repository);

  final EmergencyRepository _repository;

  Future<void> execute({
    String? imagePath,
    String? audioPath,
    String? optionalText,
  }) {
    return _repository.submitReport(imagePath, audioPath, optionalText);
  }
}
