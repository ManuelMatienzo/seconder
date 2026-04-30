import 'package:flutter/material.dart';
import 'package:movil/domain/usecases/submit_report_usecase.dart';

class ReportProvider extends ChangeNotifier {
  ReportProvider({required SubmitReportUseCase submitReportUseCase})
    : _submitReportUseCase = submitReportUseCase;

  final SubmitReportUseCase _submitReportUseCase;

  bool _isSubmitting = false;
  String? _errorMessage;
  int? _activeIncidentId;

  bool get isSubmitting => _isSubmitting;
  String? get errorMessage => _errorMessage;
  int? get activeIncidentId => _activeIncidentId;

  Future<bool> submitReport({
    String? imagePath,
    String? audioPath,
    String? optionalText,
    required int vehicleId,
  }) async {
    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final incidentId = await _submitReportUseCase.execute(
        imagePath: imagePath,
        audioPath: audioPath,
        optionalText: optionalText,
        vehicleId: vehicleId,
      );
      _activeIncidentId = incidentId;
      return true;
    } catch (error) {
      _errorMessage = error.toString().replaceFirst('Exception: ', '');
      return false;
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  void clearActiveIncident() {
    _activeIncidentId = null;
    notifyListeners();
  }
}
