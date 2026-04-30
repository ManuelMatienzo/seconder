import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/presentation/providers/report_provider.dart';
import 'package:movil/data/repositories/api_emergency_repository.dart';
import 'package:movil/data/repositories/api_auth_repository.dart';
import 'package:movil/presentation/pages/main_wrapper.dart';

class WaitingHelpPage extends StatefulWidget {
  const WaitingHelpPage({super.key});

  @override
  State<WaitingHelpPage> createState() => _WaitingHelpPageState();
}

class _WaitingHelpPageState extends State<WaitingHelpPage> {
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  void _startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) async {
      final incidentId = context.read<ReportProvider>().activeIncidentId;
      if (incidentId == null) {
        _pollingTimer?.cancel();
        return;
      }

      // Guardia: no hay token → no llamar al backend
      if (ApiAuthRepository.accessToken == null) {
        _pollingTimer?.cancel();
        return;
      }

      final repo = ApiEmergencyRepository();
      final data = await repo.checkIncidentStatus(incidentId);

      if (data != null && mounted) {
        final status = data['status'] as String? ?? 'pendiente';
        // Si el incidente ya fue tomado por un taller (no está pendiente), ir a trazabilidad
        if (status.toLowerCase() != 'pendiente') {
          _pollingTimer?.cancel();
          
          if (status.toLowerCase() == 'cancelado' || status.toLowerCase() == 'rechazado') {
            context.read<ReportProvider>().clearActiveIncident();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('No se encontró un taller disponible o la solicitud fue rechazada.'),
                backgroundColor: Colors.red,
              ),
            );
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const MainWrapper(initialIndex: 0)),
              (route) => false,
            );
          } else {
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const MainWrapper(initialIndex: 2)),
              (route) => false,
            );
          }
        }
      }
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  void _cancelRequest() {
    // Aquí se llamaría a la API para cancelar
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Solicitud cancelada')),
    );
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(color: AppColors.primaryBlue),
              const SizedBox(height: 32),
              const Text(
                'Solicitando ayuda...',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textMain,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Estamos buscando el taller más cercano a tu ubicación. Por favor espera.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: AppColors.textMuted,
                ),
              ),
              const SizedBox(height: 48),
              CustomButton(
                text: 'Cancelar Solicitud',
                onPressed: _cancelRequest,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
