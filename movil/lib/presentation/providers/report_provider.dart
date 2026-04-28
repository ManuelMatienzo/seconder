import 'package:flutter/material.dart';
import 'package:movil/domain/usecases/submit_report_usecase.dart';

class ReportProvider extends ChangeNotifier {
  ReportProvider({required SubmitReportUseCase submitReportUseCase})
    : _submitReportUseCase = submitReportUseCase;

  final SubmitReportUseCase _submitReportUseCase;

  bool _isSubmitting = false;
  String? _errorMessage;

  bool get isSubmitting => _isSubmitting;
  String? get errorMessage => _errorMessage;

  Future<bool> submitReport({
    String? imagePath,
    String? audioPath,
    String? optionalText,
  }) async {
    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _submitReportUseCase.execute(
        imagePath: imagePath,
        audioPath: audioPath,
        optionalText: optionalText,
      );
      return true;
    } catch (error) {
      _errorMessage = error.toString().replaceFirst('Exception: ', '');
      return false;
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }
}
