import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/core/widgets/custom_input.dart';
import 'package:movil/domain/entities/vehicle.dart';
import 'package:movil/presentation/providers/vehicle_provider.dart';

class VehiclesManagementPage extends StatelessWidget {
  const VehiclesManagementPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<VehicleProvider>(
      builder: (context, provider, _) {
        final vehicles = provider.vehicles;
        return Scaffold(
          backgroundColor: AppColors.background,
          // ── Header ──────────────────────────────────────────────────
          appBar: AppBar(
            backgroundColor: AppColors.background,
            elevation: 0,
            scrolledUnderElevation: 0,
            automaticallyImplyLeading: false,
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Mis Vehículos',
                  style: TextStyle(
                    color: AppColors.textMain,
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  '${vehicles.length} '
                  '${vehicles.length == 1 ? 'vehículo registrado' : 'vehículos registrados'}',
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            toolbarHeight: 72,
          ),
          // ── Lista de tarjetas ────────────────────────────────────────
          body: vehicles.isEmpty
              ? const _EmptyState()
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
                  itemCount: vehicles.length,
                  itemBuilder: (context, index) => _VehicleCard(
                    vehicle: vehicles[index],
                    onDelete: () =>
                        provider.removeVehicle(vehicles[index].id),
                  ),
                ),
          // ── FAB ──────────────────────────────────────────────────────
          floatingActionButton: FloatingActionButton(
            backgroundColor: AppColors.primaryBlue,
            foregroundColor: AppColors.white,
            elevation: 2,
            tooltip: 'Agregar vehículo',
            onPressed: () => _showAddVehicleSheet(context, provider),
            child: const Icon(Icons.add, size: 28),
          ),
        );
      },
    );
  }

  // ── Bottom Sheet — Formulario de alta ─────────────────────────────────

  void _showAddVehicleSheet(BuildContext context, VehicleProvider provider) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _AddVehicleSheet(provider: provider),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Tarjeta de vehículo
// ═══════════════════════════════════════════════════════════════════════

class _VehicleCard extends StatelessWidget {
  const _VehicleCard({required this.vehicle, required this.onDelete});
  final Vehicle vehicle;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSide, width: 1.5),
      ),
      child: ListTile(
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: AppColors.primaryBlue.withValues(alpha: 0.10),
          radius: 24,
          child: const Icon(
            Icons.directions_car,
            color: AppColors.primaryBlue,
            size: 22,
          ),
        ),
        title: Text(
          '${vehicle.brand} ${vehicle.model}',
          style: const TextStyle(
            color: AppColors.textMain,
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(
            '${vehicle.plate}  ·  ${vehicle.year}  ·  ${vehicle.color}',
            style: const TextStyle(
              color: AppColors.textMuted,
              fontSize: 13,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
        trailing: IconButton(
          icon: const Icon(
            Icons.delete_outline,
            color: AppColors.textMuted,
            size: 22,
          ),
          tooltip: 'Eliminar vehículo',
          onPressed: onDelete,
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Estado vacío
// ═══════════════════════════════════════════════════════════════════════

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.directions_car_outlined,
              size: 64, color: AppColors.borderSide),
          SizedBox(height: 16),
          Text(
            'Sin vehículos registrados',
            style: TextStyle(
              color: AppColors.textMain,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            ),
          ),
          SizedBox(height: 6),
          Text(
            'Toca + para agregar tu primer vehículo.',
            style: TextStyle(color: AppColors.textMuted, fontSize: 14),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Bottom Sheet — Formulario de alta
// ═══════════════════════════════════════════════════════════════════════

class _AddVehicleSheet extends StatefulWidget {
  const _AddVehicleSheet({required this.provider});
  final VehicleProvider provider;

  @override
  State<_AddVehicleSheet> createState() => _AddVehicleSheetState();
}

class _AddVehicleSheetState extends State<_AddVehicleSheet> {
  final _brandCtrl = TextEditingController();
  final _modelCtrl = TextEditingController();
  final _plateCtrl = TextEditingController();
  final _yearCtrl = TextEditingController();
  final _colorCtrl = TextEditingController();

  String? _errorMessage;

  @override
  void dispose() {
    _brandCtrl.dispose();
    _modelCtrl.dispose();
    _plateCtrl.dispose();
    _yearCtrl.dispose();
    _colorCtrl.dispose();
    super.dispose();
  }

  void _save() {
    final brand = _brandCtrl.text.trim();
    final model = _modelCtrl.text.trim();
    final plate = _plateCtrl.text.trim();
    final yearStr = _yearCtrl.text.trim();
    final color = _colorCtrl.text.trim();

    if (brand.isEmpty ||
        model.isEmpty ||
        plate.isEmpty ||
        yearStr.isEmpty ||
        color.isEmpty) {
      setState(() => _errorMessage = 'Por favor completa todos los campos.');
      return;
    }

    final year = int.tryParse(yearStr);
    if (year == null || year < 1900 || year > DateTime.now().year + 1) {
      setState(() => _errorMessage = 'Ingresa un año válido.');
      return;
    }

    widget.provider.addVehicle(
      Vehicle(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        brand: brand,
        model: model,
        plate: plate.toUpperCase(),
        year: year,
        color: color,
      ),
    );

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
      ),
      padding: EdgeInsets.fromLTRB(20, 16, 20, 20 + bottomInset),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.borderSide,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 18),
            const Text(
              'Agregar vehículo',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: 18,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 18),

            // ── Campos ──
            CustomInput(
              controller: _brandCtrl,
              labelText: 'Marca',
              hintText: 'Ej. Toyota',
              textInputAction: TextInputAction.next,
              prefixIcon: const Icon(Icons.branding_watermark_outlined,
                  color: AppColors.textMuted, size: 20),
            ),
            const SizedBox(height: 12),
            CustomInput(
              controller: _modelCtrl,
              labelText: 'Modelo',
              hintText: 'Ej. Corolla',
              textInputAction: TextInputAction.next,
              prefixIcon: const Icon(Icons.directions_car_outlined,
                  color: AppColors.textMuted, size: 20),
            ),
            const SizedBox(height: 12),
            CustomInput(
              controller: _plateCtrl,
              labelText: 'Placa',
              hintText: 'Ej. ABC-1234',
              textInputAction: TextInputAction.next,
              prefixIcon: const Icon(Icons.credit_card_outlined,
                  color: AppColors.textMuted, size: 20),
            ),
            const SizedBox(height: 12),
            CustomInput(
              controller: _yearCtrl,
              labelText: 'Año',
              hintText: 'Ej. 2020',
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.next,
              prefixIcon: const Icon(Icons.calendar_today_outlined,
                  color: AppColors.textMuted, size: 20),
            ),
            const SizedBox(height: 12),
            CustomInput(
              controller: _colorCtrl,
              labelText: 'Color',
              hintText: 'Ej. Blanco',
              textInputAction: TextInputAction.done,
              prefixIcon: const Icon(Icons.palette_outlined,
                  color: AppColors.textMuted, size: 20),
            ),

            // ── Error ──
            if (_errorMessage != null) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.redDanger.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                      color: AppColors.redDanger.withValues(alpha: 0.35),
                      width: 1.5),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline,
                        color: AppColors.redDanger, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(
                          color: AppColors.redDanger,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 20),
            CustomButton(text: 'Guardar vehículo', onPressed: _save),
          ],
        ),
      ),
    );
  }
}
