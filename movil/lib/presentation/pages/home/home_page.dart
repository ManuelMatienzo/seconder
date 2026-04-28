import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/presentation/pages/report/multimodal_report_page.dart';
import 'package:provider/provider.dart';
import 'package:movil/presentation/providers/vehicle_provider.dart';
import 'package:movil/presentation/providers/auth_provider.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  int _selectedVehicleIndex = 0;

  // ── Animación de pulso del botón de pánico ────────────────────────────
  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnim;

  // ── Ubicación ─────────────────────────────────────────────────────────
  Position? _currentPosition;
  bool _isLoadingLocation = true;
  String? _locationError;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _pulseAnim = Tween<double>(begin: 1.0, end: 1.18).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _getCurrentLocation();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final user = context.read<AuthProvider>().currentUser;
      if (user != null) {
        context.read<VehicleProvider>().loadVehicles(user.id);
      }
    });
  }

  Future<void> _getCurrentLocation() async {
    setState(() {
      _isLoadingLocation = true;
      _locationError = null;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _locationError = 'Los servicios de ubicación están desactivados.';
          _isLoadingLocation = false;
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _locationError = 'Permiso de ubicación denegado.';
            _isLoadingLocation = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _locationError = 'Permisos denegados permanentemente.';
          _isLoadingLocation = false;
        });
        return;
      }

      Position position = await Geolocator.getCurrentPosition();
      setState(() {
        _currentPosition = position;
        _isLoadingLocation = false;
      });
    } catch (e) {
      setState(() {
        _locationError = 'Error al obtener ubicación.';
        _isLoadingLocation = false;
      });
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Saludo ────────────────────────────────────────────────────
            Text(
              'Hola, ${context.watch<AuthProvider>().currentUser?.name ?? 'Usuario'} 👋',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'Tu asistente vehicular está listo.',
              style: TextStyle(
                color: AppColors.textMuted,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 24),

            const Text(
              '1. Confirma tu vehículo actual',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Consumer<VehicleProvider>(
              builder: (context, vehicleProvider, _) {
                final _vehicles = vehicleProvider.vehicles;
                if (vehicleProvider.isLoading) {
                  return const SizedBox(
                    height: 110,
                    child: Center(child: CircularProgressIndicator()),
                  );
                }
                if (_vehicles.isEmpty) {
                  return const SizedBox(
                    height: 110,
                    child: Center(child: Text('No tienes vehículos registrados.')),
                  );
                }
                return SizedBox(
                  height: 110,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _vehicles.length,
                    itemBuilder: (context, index) {
                      final vehicle = _vehicles[index];
                      final isSelected = index == _selectedVehicleIndex;
                      return Padding(
                        padding: const EdgeInsets.only(right: 12),
                        child: VehicleCard(
                          name: '${vehicle.brand} ${vehicle.model}',
                          plate: vehicle.plate,
                          selected: isSelected,
                          onTap: () => setState(() => _selectedVehicleIndex = index),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
            const SizedBox(height: 24),

            // ── Sección 2: Mapa ──────────────────────────────────────────
            const Text(
              '2. Verifica tu ubicación',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _LocationStatusCard(
              currentPosition: _currentPosition,
              isLoading: _isLoadingLocation,
              errorText: _locationError,
              onRetry: _getCurrentLocation,
            ),
            const SizedBox(height: 28),

            // ── Sección 3: Botón de pánico ───────────────────────────────
            Center(
              child: _PanicButton(
                pulseAnim: _pulseAnim,
                onPressed: () {
                  if (_currentPosition == null) {
                    ScaffoldMessenger.of(context)
                      ..hideCurrentSnackBar()
                      ..showSnackBar(
                        const SnackBar(
                          backgroundColor: AppColors.redDanger,
                          content: Text('Esperando señal de GPS. Por favor asegure su ubicación primero.'),
                        ),
                      );
                    return;
                  }
                  final vehicleProvider = context.read<VehicleProvider>();
                  if (vehicleProvider.vehicles.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Por favor registre un vehículo primero.')),
                    );
                    return;
                  }
                  final selectedVehicle = vehicleProvider.vehicles[_selectedVehicleIndex];

                  Navigator.push(
                    context,
                    MaterialPageRoute<void>(
                      builder: (_) => MultimodalReportPage(
                        currentPosition: _currentPosition!,
                        vehicleId: int.parse(selectedVehicle.id),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// VehicleCard — con badge "Estado: OK"
// ═══════════════════════════════════════════════════════════════════════

class VehicleCard extends StatelessWidget {
  const VehicleCard({
    super.key,
    required this.name,
    required this.plate,
    required this.selected,
    required this.onTap,
  });

  final String name;
  final String plate;
  final bool selected;
  final VoidCallback onTap;

  static const _green = Color(0xFF16A34A);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 220,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: selected ? AppColors.primaryBlue : AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? AppColors.primaryBlue : AppColors.borderSide,
            width: 1.5,
          ),
          boxShadow: selected
              ? [
                  BoxShadow(
                    color: AppColors.primaryBlue.withValues(alpha: 0.25),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          children: [
            // Ícono del vehículo
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: selected
                    ? AppColors.white.withValues(alpha: 0.15)
                    : AppColors.primaryBlue.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.directions_car,
                color: selected ? AppColors.white : AppColors.primaryBlue,
                size: 20,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: selected ? AppColors.white : AppColors.textMain,
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(
                        plate,
                        style: TextStyle(
                          color: selected
                              ? AppColors.white.withValues(alpha: 0.80)
                              : AppColors.textMuted,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(width: 6),
                      // Badge "Estado: OK"
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 5, vertical: 2),
                        decoration: BoxDecoration(
                          color: selected
                              ? AppColors.white.withValues(alpha: 0.20)
                              : _green.withValues(alpha: 0.10),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: selected
                                ? AppColors.white.withValues(alpha: 0.40)
                                : _green.withValues(alpha: 0.60),
                            width: 1,
                          ),
                        ),
                        child: Text(
                          '● OK',
                          style: TextStyle(
                            color:
                                selected ? AppColors.white : _green,
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Tarjeta de Ubicación (Paso 0)
// ═══════════════════════════════════════════════════════════════════════

class _LocationStatusCard extends StatelessWidget {
  const _LocationStatusCard({
    required this.currentPosition,
    required this.isLoading,
    required this.errorText,
    required this.onRetry,
  });

  final Position? currentPosition;
  final bool isLoading;
  final String? errorText;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.borderSide,
          width: 1.5,
        ),
      ),
      child: _buildContent(context),
    );
  }

  Widget _buildContent(BuildContext context) {
    if (isLoading) {
      return const Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: AppColors.primaryBlue,
            ),
          ),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              'Obteniendo ubicación precisa...',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      );
    }

    if (errorText != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.location_off, color: AppColors.redDanger, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  errorText!,
                  style: const TextStyle(
                    color: AppColors.redDanger,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            height: 40,
            child: OutlinedButton(
              onPressed: errorText == 'Permisos denegados permanentemente.'
                  ? () => Geolocator.openAppSettings()
                  : onRetry,
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: AppColors.redDanger, width: 1.5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                errorText == 'Permisos denegados permanentemente.'
                    ? 'Abrir configuración'
                    : 'Reintentar',
                style: const TextStyle(color: AppColors.redDanger, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      );
    }

    if (currentPosition != null) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.location_on, color: AppColors.primaryBlue, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Ubicación asegurada en tiempo real',
                  style: TextStyle(
                    color: AppColors.textMain,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Lat: ${currentPosition!.latitude}\nLng: ${currentPosition!.longitude}',
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 12,
                    fontFamily: 'monospace',
                  ),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return const SizedBox();
  }
}


// ═══════════════════════════════════════════════════════════════════════
// Botón de pánico con efecto pulso
// ═══════════════════════════════════════════════════════════════════════

class _PanicButton extends StatelessWidget {
  const _PanicButton({
    required this.onPressed,
    required this.pulseAnim,
  });

  final VoidCallback onPressed;
  final Animation<double> pulseAnim;

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Halo pulsante (externo)
        ScaleTransition(
          scale: pulseAnim,
          child: Container(
            width: 210,
            height: 210,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.redDanger.withValues(alpha: 0.12),
            ),
          ),
        ),
        // Halo intermedio fijo
        Container(
          width: 190,
          height: 190,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: AppColors.redDanger.withValues(alpha: 0.08),
          ),
        ),
        // Botón central
        GestureDetector(
          onTap: onPressed,
          child: Container(
            width: 168,
            height: 168,
            decoration: BoxDecoration(
              gradient: RadialGradient(
                colors: [
                  const Color(0xFFEF4444),
                  AppColors.redDanger,
                ],
                center: Alignment.topCenter,
                radius: 0.85,
              ),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppColors.redDanger.withValues(alpha: 0.45),
                  blurRadius: 24,
                  spreadRadius: 4,
                  offset: const Offset(0, 6),
                ),
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.15),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.warning_amber_rounded,
                    color: AppColors.white, size: 46),
                SizedBox(height: 8),
                Text(
                  'PEDIR AUXILIO',
                  style: TextStyle(
                    color: AppColors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.8,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

