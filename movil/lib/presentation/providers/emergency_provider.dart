import 'package:flutter/material.dart';
import 'package:movil/domain/entities/emergency_case_entity.dart';
import 'package:movil/domain/usecases/create_emergency_alert_usecase.dart';
import 'package:movil/domain/usecases/get_active_cases_usecase.dart';

class EmergencyProvider extends ChangeNotifier {
  EmergencyProvider({
    required GetActiveCasesUseCase getActiveCasesUseCase,
    required CreateEmergencyAlertUseCase createEmergencyAlertUseCase,
  }) : _getActiveCasesUseCase = getActiveCasesUseCase,
       _createEmergencyAlertUseCase = createEmergencyAlertUseCase;

  final GetActiveCasesUseCase _getActiveCasesUseCase;
  final CreateEmergencyAlertUseCase _createEmergencyAlertUseCase;

  List<EmergencyCaseEntity> _cases = const [];
  bool _isLoading = false;
  bool _isSending = false;
  String? _errorMessage;
  String _vehiclePlate = '';
  String _description = '';

  List<EmergencyCaseEntity> get cases => _cases;
  bool get isLoading => _isLoading;
  bool get isSending => _isSending;
  String? get errorMessage => _errorMessage;

  void setVehiclePlate(String value) {
    _vehiclePlate = value;
    _errorMessage = null;
    notifyListeners();
  }

  void setDescription(String value) {
    _description = value;
    _errorMessage = null;
    notifyListeners();
  }

  Future<void> loadCases() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _cases = await _getActiveCasesUseCase.execute();
    } catch (_) {
      _errorMessage = 'No se pudieron cargar los casos.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> sendEmergencyAlert() async {
    if (_description.trim().isEmpty) {
      _errorMessage = 'Describe la emergencia para continuar.';
      notifyListeners();
      return;
    }

    _isSending = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _createEmergencyAlertUseCase.execute(
        vehiclePlate: _vehiclePlate,
        description: _description,
      );
      _description = '';
      _vehiclePlate = '';
      await loadCases();
    } catch (_) {
      _errorMessage = 'No se pudo enviar la alerta.';
    } finally {
      _isSending = false;
      notifyListeners();
    }
  }
}
