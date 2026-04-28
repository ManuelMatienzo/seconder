import 'package:movil/domain/entities/emergency_case_entity.dart';
import 'package:movil/domain/repositories/emergency_repository.dart';

class GetActiveCasesUseCase {
  const GetActiveCasesUseCase(this._repository);

  final EmergencyRepository _repository;

  Future<List<EmergencyCaseEntity>> execute() {
    return _repository.getActiveCases();
  }
}
