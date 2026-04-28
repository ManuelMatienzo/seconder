import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/presentation/providers/report_provider.dart';
import 'package:movil/data/repositories/api_emergency_repository.dart';

class ActiveEmergencyPage extends StatefulWidget {
  const ActiveEmergencyPage({super.key});

  @override
  State<ActiveEmergencyPage> createState() => _ActiveEmergencyPageState();
}

class _ActiveEmergencyPageState extends State<ActiveEmergencyPage> {
  Timer? _pollingTimer;
  Map<String, dynamic>? _statusData;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  void _startPolling() {
    _fetchStatus(); // fetch inmediatamente
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _fetchStatus();
    });
  }

  Future<void> _fetchStatus() async {
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId == null) return;

    if (!mounted) return;
    
    // Un simple read al repo, no queremos un provider complejo por ahora
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
    _pollingTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final incidentId = context.watch<ReportProvider>().activeIncidentId;

    if (incidentId == null) {
      return const Center(
        child: Text(
          'No tienes ninguna emergencia activa.',
          style: TextStyle(color: AppColors.textMuted, fontSize: 16),
        ),
      );
    }

    if (_statusData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final status = _statusData!['status'] as String? ?? 'Desconocido';
    final workshopName = _statusData!['workshop_name'] as String? ?? 'Buscando taller...';
    final technicianName = _statusData!['technician_name'] as String? ?? 'No asignado aún';

    return SafeArea(
      child: Padding(
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
            _buildStatusCard(status, workshopName, technicianName),
            const SizedBox(height: 32),
            if (status.toUpperCase() == 'FINALIZADO') _buildPaymentSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard(String status, String workshop, String technician) {
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
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primaryBlue.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.car_repair, color: AppColors.primaryBlue),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Estado: ${status.toUpperCase()}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.primaryBlue,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Taller: $workshop',
                      style: const TextStyle(fontSize: 14, color: AppColors.textMain),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const Divider(height: 32),
          Text(
            'Mecánico Asignado:',
            style: const TextStyle(fontSize: 12, color: AppColors.textMuted, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            technician,
            style: const TextStyle(fontSize: 15, color: AppColors.textMain, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Pago del Servicio',
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
                'Tu emergencia ha sido atendida. Por favor, realiza el pago simulado para finalizar.',
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
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    Navigator.pop(context); // cerrar modal
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Pago realizado con éxito.')),
    );
    // Limpiar estado
    // Aqui podriamos resetear el provider
  }
}
