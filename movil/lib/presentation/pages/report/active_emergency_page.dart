import 'dart:async';
import 'dart:convert';
import 'dart:io';
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

class _ActiveEmergencyPageState extends State<ActiveEmergencyPage>
    with SingleTickerProviderStateMixin {
  Timer? _pollingTimer;
  Map<String, dynamic>? _statusData;
  final TextEditingController _amountController = TextEditingController();
  String _paymentMethod = 'tarjeta';
  bool _isPaying = false;
  WebSocket? _notificationSocket;
  StreamSubscription<dynamic>? _notificationSub;
  OverlayEntry? _pushEntry;
  Timer? _pushTimer;
  late final AnimationController _pushController;
  late final Animation<Offset> _pushOffset;

  @override
  void initState() {
    super.initState();
    _pushController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 320),
      reverseDuration: const Duration(milliseconds: 220),
    );
    _pushOffset = Tween<Offset>(begin: const Offset(0, -1.1), end: Offset.zero)
        .animate(
          CurvedAnimation(parent: _pushController, curve: Curves.easeOutCubic),
        );
    // Solo arrancar el polling si hay una emergencia activa
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId != null) {
      _startPolling();
      _startRealtimeNotifications();
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

  void _startRealtimeNotifications() {
    final token = ApiAuthRepository.accessToken;
    if (token == null) return;

    final wsUrl = _buildWsUrl(getBaseUrl(), token);
    WebSocket.connect(wsUrl)
        .then((socket) {
          _notificationSocket = socket;
          _notificationSub = socket.listen(
            (data) {
              _handleRealtimeMessage(data);
            },
            onError: (_) {
              _stopRealtimeNotifications();
            },
            onDone: () {
              _stopRealtimeNotifications();
            },
          );
        })
        .catchError((_) {});
  }

  void _stopRealtimeNotifications() {
    _notificationSub?.cancel();
    _notificationSub = null;
    _notificationSocket?.close();
    _notificationSocket = null;
  }

  String _buildWsUrl(String baseUrl, String token) {
    final uri = Uri.parse(baseUrl);
    final scheme = uri.scheme == 'https' ? 'wss' : 'ws';
    return uri
        .replace(
          scheme: scheme,
          path: '/ws/notifications',
          queryParameters: {'token': token},
        )
        .toString();
  }

  void _handleRealtimeMessage(dynamic data) {
    if (data == null) return;
    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId == null) return;

    try {
      final payload = jsonDecode(data.toString()) as Map<String, dynamic>;
      if (payload['type'] != 'request_accepted') return;
      if (payload['incident_id'] != incidentId) return;

      final workshopName = payload['workshop_name'] as String? ?? 'El taller';
      if (mounted) {
        _showPushOverlay(
          title: 'Solicitud aceptada',
          message: '$workshopName acepto tu solicitud. Ya va en camino.',
        );
      }
      _fetchStatus();
    } catch (_) {
      // Ignorar payloads invalidos
    }
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
    _stopRealtimeNotifications();
    _pushTimer?.cancel();
    _removePushOverlay();
    _pushController.dispose();
    _amountController.dispose();
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
            Icon(
              Icons.shield_outlined,
              size: 80,
              color: AppColors.primaryBlue.withValues(alpha: 0.5),
            ),
            const SizedBox(height: 16),
            const Text(
              'Todo en orden.',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
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
    final normalizedStatus = status.toLowerCase();
    final workshop = _statusData!['workshop'] as Map<String, dynamic>?;
    final workshopName =
        workshop?['workshop_name'] as String? ?? 'Buscando taller...';
    final technician = _statusData!['technician'] as Map<String, dynamic>?;
    final technicianName = technician?['name'] as String? ?? 'No asignado aún';
    final distanceKm = _parseDouble(_statusData!['distance_km']);
    final etaMinutes = _parseInt(_statusData!['estimated_time_min']);
    final showPayment =
        normalizedStatus == 'completado' || normalizedStatus == 'atendido';

    if (normalizedStatus == 'cancelado' || normalizedStatus == 'rechazado') {
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
                style: TextStyle(
                  color: AppColors.textMain,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
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
            _buildKeyInfoCard(
              workshopName: workshopName,
              technicianName: technicianName,
              distanceKm: distanceKm,
              etaMinutes: etaMinutes,
              hasWorkshop: workshop != null,
              hasTechnician: technician != null,
            ),
            const SizedBox(height: 20),
            _buildTimeline(
              status,
              workshopName,
              technicianName,
              workshop != null,
            ),
            const SizedBox(height: 32),
            if (showPayment) _buildPaymentSection(),
          ],
        ),
      ),
    );
  }

  int _getCurrentStep(String status, {required bool hasWorkshop}) {
    status = status.toLowerCase();
    if (status == 'pendiente') return hasWorkshop ? 2 : 1;
    if (['asignado', 'alistando', 'en_ruta', 'en_sitio'].contains(status))
      return 3;
    if (['completado', 'atendido', 'finalizado'].contains(status)) return 4;
    return 0;
  }

  Widget _buildTimeline(
    String status,
    String workshop,
    String technician,
    bool hasWorkshop,
  ) {
    int currentStep = _getCurrentStep(status, hasWorkshop: hasWorkshop);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.primaryBlue.withValues(alpha: 0.3),
          width: 1.5,
        ),
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
            description:
                'Procesando imágenes y audio para priorizar la emergencia.',
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
            description:
                'Solicitud aceptada. El mecánico $technician va en camino.',
            icon: Icons.directions_car,
            isActive: currentStep == 3,
            isCompleted: currentStep > 3,
            isLast: true,
          ),
        ],
      ),
    );
  }

  Widget _buildKeyInfoCard({
    required String workshopName,
    required String technicianName,
    required double? distanceKm,
    required int? etaMinutes,
    required bool hasWorkshop,
    required bool hasTechnician,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primaryBlue.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.primaryBlue.withValues(alpha: 0.25),
          width: 1.2,
        ),
      ),
      child: Column(
        children: [
          _buildKeyInfoRow(
            icon: Icons.storefront,
            label: 'Taller asignado',
            value: workshopName,
            isHighlighted: hasWorkshop,
          ),
          const SizedBox(height: 12),
          _buildKeyInfoRow(
            icon: Icons.engineering,
            label: 'Mecánico asignado',
            value: technicianName,
            isHighlighted: hasTechnician,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatChip(
                  icon: Icons.route,
                  label: 'Distancia',
                  value: _formatDistance(distanceKm),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatChip(
                  icon: Icons.timer,
                  label: 'Tiempo estimado',
                  value: _formatEta(etaMinutes),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildKeyInfoRow({
    required IconData icon,
    required String label,
    required String value,
    required bool isHighlighted,
  }) {
    final highlightColor = isHighlighted
        ? AppColors.primaryBlue
        : AppColors.textMuted;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: highlightColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: highlightColor, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: TextStyle(
                  color: highlightColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatChip({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderSide),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primaryBlue, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    color: AppColors.textMain,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  int? _parseInt(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value);
    return null;
  }

  String _formatDistance(double? distanceKm) {
    if (distanceKm == null) return 'Calculando...';
    return '${distanceKm.toStringAsFixed(1)} km';
  }

  String _formatEta(int? minutes) {
    if (minutes == null) return 'Calculando...';
    return '$minutes min';
  }

  void _showPushOverlay({required String title, required String message}) {
    _pushTimer?.cancel();
    _removePushOverlay();

    final overlay = Overlay.of(context);
    if (overlay == null) {
      return;
    }

    _pushEntry = OverlayEntry(
      builder: (context) {
        return Positioned(
          top: 12,
          left: 0,
          right: 0,
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.only(top: 6),
              child: SlideTransition(
                position: _pushOffset,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Material(
                    color: Colors.transparent,
                    child: Container(
                      decoration: BoxDecoration(
                        color: AppColors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(
                          color: AppColors.primaryBlue,
                          width: 1.2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.16),
                            blurRadius: 18,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.fromLTRB(16, 14, 8, 14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      const Icon(
                                        Icons.notifications_active,
                                        color: AppColors.darkBlue,
                                        size: 20,
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        title,
                                        style: const TextStyle(
                                          color: AppColors.darkBlue,
                                          fontWeight: FontWeight.w900,
                                          fontSize: 15,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    message,
                                    style: const TextStyle(
                                      color: AppColors.textMain,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          IconButton(
                            onPressed: _hidePushOverlay,
                            icon: const Icon(Icons.close, size: 18),
                            color: AppColors.darkBlue,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );

    overlay.insert(_pushEntry!);
    _pushController.forward(from: 0);
    _pushTimer = Timer(const Duration(seconds: 4), _hidePushOverlay);
  }

  void _hidePushOverlay() {
    if (_pushEntry == null) return;
    _pushTimer?.cancel();
    _pushController.reverse().whenComplete(_removePushOverlay);
  }

  void _removePushOverlay() {
    _pushEntry?.remove();
    _pushEntry = null;
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
                color: isCompleted || isActive
                    ? AppColors.primaryBlue
                    : Colors.grey.shade300,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: Colors.white, size: 20),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 40,
                color: isCompleted
                    ? AppColors.primaryBlue
                    : Colors.grey.shade300,
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
                  color: isActive || isCompleted
                      ? AppColors.textMain
                      : Colors.grey,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 14,
                  color: isActive || isCompleted
                      ? AppColors.textMain
                      : Colors.grey,
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
                'El taller ha reportado la finalización del trabajo físico. Ingresa el monto y realiza el pago para cerrar la emergencia.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textMain),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: InputDecoration(
                  hintText: 'Monto (Bs)',
                  filled: true,
                  fillColor: AppColors.white,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 12,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide(
                      color: AppColors.amber.withValues(alpha: 0.6),
                    ),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide(
                      color: AppColors.amber.withValues(alpha: 0.6),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _paymentMethod,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: AppColors.white,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 12,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: 'tarjeta', child: Text('Tarjeta')),
                  DropdownMenuItem(value: 'efectivo', child: Text('Efectivo')),
                ],
                onChanged: _isPaying
                    ? null
                    : (value) {
                        if (value == null) return;
                        setState(() => _paymentMethod = value);
                      },
              ),
              const SizedBox(height: 16),
              CustomButton(
                text: _isPaying ? 'Procesando pago...' : 'Pagar y Finalizar',
                isLoading: _isPaying,
                onPressed: _isPaying ? null : _payIncident,
              ),
            ],
          ),
        ),
      ],
    );
  }

  double? _parseAmount() {
    final raw = _amountController.text.trim().replaceAll(',', '.');
    final amount = double.tryParse(raw);
    if (amount == null || amount <= 0) {
      return null;
    }
    return amount;
  }

  Future<void> _payIncident() async {
    final amount = _parseAmount();
    if (amount == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Ingresa un monto válido.')));
      return;
    }

    final incidentId = context.read<ReportProvider>().activeIncidentId;
    if (incidentId == null) {
      return;
    }

    setState(() => _isPaying = true);
    try {
      final repo = ApiEmergencyRepository();
      await repo.payIncident(incidentId, amount, _paymentMethod);
      await repo.updateTracking(incidentId, 'finalizado');

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pago realizado con éxito. ¡Gracias!')),
      );
      _amountController.clear();
      context.read<ReportProvider>().clearActiveIncident();
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo procesar el pago.')),
      );
    } finally {
      if (mounted) {
        setState(() => _isPaying = false);
      }
    }
  }
}
