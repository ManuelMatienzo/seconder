import 'package:movil/domain/repositories/emergency_repository.dart';

class CreateEmergencyAlertUseCase {
  const CreateEmergencyAlertUseCase(this._repository);

  final EmergencyRepository _repository;

  Future<void> execute({
    required String vehiclePlate,
    required String description,
  }) {
    return _repository.createEmergencyAlert(
      vehiclePlate: vehiclePlate,
      description: description,
    );
  }
}
