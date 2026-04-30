import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/presentation/providers/report_provider.dart';
import 'package:movil/data/repositories/api_emergency_repository.dart';
import 'package:movil/data/repositories/api_auth_repository.dart';

class ActiveEmergencyPage extends StatefulWidget {
  const ActiveEmergencyPage({super.key});

  @override
  State<ActiveEmergencyPage> createState() => _ActiveEmergencyPageState();
}

class _ActiveEmergencyPageState extends State<ActiveEmergencyPage> {
  Timer? _pollingTimer;
  Map<String, dynamic>? _statusData;

  @override
  void initState() {
    super.initState();
    // Solo arrancar el polling si hay una emergencia activa
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId != null) {
      _startPolling();
    }
  }

  void _startPolling() {
    _stopPolling(); // cancelar cualquier timer previo antes de crear uno nuevo
    _fetchStatus();
    // Intervalo de 10s para no saturar el servidor
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _fetchStatus();
    });
  }

  void _stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  Future<void> _fetchStatus() async {
    // Guardia 1: no hay emergencia activa → no hacer nada
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId == null) {
      _stopPolling();
      return;
    }

    // Guardia 2: no hay token → no llamar al backend para evitar el 401
    if (ApiAuthRepository.accessToken == null) {
      _stopPolling();
      return;
    }

    if (!mounted) return;

    final repo = ApiEmergencyRepository();
    final data = await repo.checkIncidentStatus(incidentId);

    if (data != null && mounted) {
      setState(() {
        _statusData = data;
      });
    }
  }

  @override
  void dispose() {
    _stopPolling();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final incidentId = context.watch<ReportProvider>().activeIncidentId;

    if (incidentId == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.shield_outlined, size: 80, color: AppColors.primaryBlue.withValues(alpha: 0.5)),
            const SizedBox(height: 16),
            const Text(
              'Todo en orden.',
              style: TextStyle(color: AppColors.textMain, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'No tienes ninguna emergencia activa.',
              style: TextStyle(color: AppColors.textMuted, fontSize: 16),
            ),
          ],
        ),
      );
    }

    if (_statusData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final status = _statusData!['incident_status'] as String? ?? 'desconocido';
    final workshop = _statusData!['workshop'] as Map<String, dynamic>?;
    final workshopName = workshop?['workshop_name'] as String? ?? 'Buscando taller...';
    final technician = _statusData!['technician'] as Map<String, dynamic>?;
    final technicianName = technician?['name'] as String? ?? 'No asignado aún';

    if (status.toLowerCase() == 'cancelado' || status.toLowerCase() == 'rechazado') {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 80, color: Colors.red),
              const SizedBox(height: 16),
              const Text(
                'Solicitud Cancelada',
                style: TextStyle(color: AppColors.textMain, fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'No se pudo encontrar un taller disponible o la solicitud fue rechazada.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textMuted, fontSize: 16),
              ),
              const SizedBox(height: 24),
              CustomButton(
                text: 'Entendido',
                onPressed: () {
                  context.read<ReportProvider>().clearActiveIncident();
                },
              ),
            ],
          ),
        ),
      );
    }

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Trazabilidad de Emergencia',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: AppColors.textMain,
              ),
            ),
            const SizedBox(height: 24),
            _buildTimeline(status, workshopName, technicianName),
            const SizedBox(height: 32),
            if (status.toLowerCase() == 'completado') _buildPaymentSection(),
          ],
        ),
      ),
    );
  }

  int _getCurrentStep(String status) {
    status = status.toLowerCase();
    if (status == 'pendiente') return 2;
    if (['asignado', 'alistando', 'en_ruta', 'en_sitio'].contains(status)) return 3;
    if (status == 'completado') return 4;
    return 0;
  }

  Widget _buildTimeline(String status, String workshop, String technician) {
    int currentStep = _getCurrentStep(status);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primaryBlue.withValues(alpha: 0.3), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryBlue.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildTimelineStep(
            title: 'Recepción de Reporte',
            description: 'El reporte ha sido enviado exitosamente.',
            icon: Icons.check_circle_outline,
            isActive: currentStep == 0,
            isCompleted: currentStep > 0,
            isLast: false,
          ),
          _buildTimelineStep(
            title: 'Análisis de IA',
            description: 'Procesando imágenes y audio para priorizar la emergencia.',
            icon: Icons.auto_awesome,
            isActive: currentStep == 1,
            isCompleted: currentStep > 1,
            isLast: false,
          ),
          _buildTimelineStep(
            title: 'Despacho Automotriz',
            description: 'Taller localizado. Esperando respuesta de $workshop.',
            icon: Icons.storefront,
            isActive: currentStep == 2,
            isCompleted: currentStep > 2,
            isLast: false,
          ),
          _buildTimelineStep(
            title: 'Unidad en Camino',
            description: 'Solicitud aceptada. El mecánico $technician va en camino.',
            icon: Icons.directions_car,
            isActive: currentStep == 3,
            isCompleted: currentStep > 3,
            isLast: true,
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineStep({
    required String title,
    required String description,
    required IconData icon,
    required bool isActive,
    required bool isCompleted,
    required bool isLast,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isCompleted || isActive ? AppColors.primaryBlue : Colors.grey.shade300,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: Colors.white, size: 20),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 40,
                color: isCompleted ? AppColors.primaryBlue : Colors.grey.shade300,
              ),
          ],
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: isActive || isCompleted ? AppColors.textMain : Colors.grey,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 14,
                  color: isActive || isCompleted ? AppColors.textMain : Colors.grey,
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Servicio Finalizado',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.textMain,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.amber.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.amber, width: 1.5),
          ),
          child: Column(
            children: [
              const Text(
                'El taller ha reportado la finalización del trabajo físico. Por favor, realiza el pago simulado para finalizar la emergencia.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textMain),
              ),
              const SizedBox(height: 16),
              CustomButton(
                text: 'Pagar Simulado (100 Bs)',
                onPressed: _simulatePayment,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _simulatePayment() async {
    // Simular el pago local
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(child: CircularProgressIndicator()),
    );
    
    // Llamar al endpoint para finalizar el incidente
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId != null) {
      final repo = ApiEmergencyRepository();
      // En un futuro aqui se mandaria el pago real, por ahora finalizamos el tracking
      await repo.updateTracking(incidentId, 'finalizado');
    }
    
    if (!mounted) return;
    Navigator.pop(context); // cerrar modal
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Pago realizado con éxito. ¡Gracias!')),
    );
    // Limpiar estado
    context.read<ReportProvider>().clearActiveIncident();
  }
}

