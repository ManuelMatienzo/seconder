import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';

import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/core/widgets/custom_input.dart';
import 'package:movil/presentation/providers/report_provider.dart';
import 'package:movil/presentation/pages/report/waiting_help_page.dart';

class MultimodalReportPage extends StatefulWidget {
  const MultimodalReportPage({super.key, required this.currentPosition, required this.vehicleId});
  final Position currentPosition;
  final int vehicleId;

  @override
  State<MultimodalReportPage> createState() => _MultimodalReportPageState();
}

class _MultimodalReportPageState extends State<MultimodalReportPage> {
  final TextEditingController _detailsController = TextEditingController();

  // — Cámara —
  File? _imageFile;
  bool _isPickingImage = false;

  // — Audio —
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  int _recordingSeconds = 0;
  Timer? _recordingTimer;
  String? _audioPath;

  // ─────────────────────────── Ciclo de vida ───────────────────────────

  @override
  void dispose() {
    _detailsController.dispose();
    _recordingTimer?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  // ─────────────────────────── Cámara ──────────────────────────────────

  Future<void> _pickImage(ImageSource source) async {
    if (_isPickingImage) return;
    setState(() => _isPickingImage = true);

    try {
      final picker = ImagePicker();
      final XFile? photo = await picker.pickImage(
        source: source,
        imageQuality: 80,
        maxWidth: 1280,
      );
      if (photo != null) {
        setState(() => _imageFile = File(photo.path));
      }
    } catch (_) {
      if (mounted) {
        _showErrorSnackBar('No se pudo acceder a la cámara o galería.');
      }
    } finally {
      if (mounted) setState(() => _isPickingImage = false);
    }
  }

  void _discardImage() => setState(() => _imageFile = null);

  void _showImageSourceDialog(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) {
        return Container(
          decoration: const BoxDecoration(
            color: AppColors.background,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(16),
              topRight: Radius.circular(16),
            ),
          ),
          child: SafeArea(
            top: false,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 12),
                // Drag handle
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.borderSide,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Seleccionar imagen',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                const Divider(color: AppColors.borderSide, height: 1),
                ListTile(
                  leading: const Icon(
                    Icons.camera_alt,
                    color: AppColors.primaryBlue,
                  ),
                  title: const Text(
                    'Tomar Foto',
                    style: TextStyle(
                      color: AppColors.textMain,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: const Icon(
                    Icons.photo_library,
                    color: AppColors.primaryBlue,
                  ),
                  title: const Text(
                    'Elegir de la Galería',
                    style: TextStyle(
                      color: AppColors.textMain,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.gallery);
                  },
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showFullScreenImage(BuildContext context) {
    if (_imageFile == null) return;
    Navigator.push(
      context,
      PageRouteBuilder<void>(
        opaque: false,
        barrierColor: Colors.black,
        transitionDuration: const Duration(milliseconds: 220),
        pageBuilder: (context, animation, secondary) =>
            _FullScreenImageViewer(imageFile: _imageFile!),
        transitionsBuilder: (context, animation, _, child) =>
            FadeTransition(opacity: animation, child: child),
      ),
    );
  }

  // ─────────────────────────── Audio ───────────────────────────────────

  Future<void> _startRecording() async {
    // Verificar permiso de micrófono antes de intentar grabar
    final hasPermission = await _audioRecorder.hasPermission();
    if (!hasPermission) {
      if (mounted) _showErrorSnackBar('Permiso de micrófono denegado.');
      return;
    }

    // Obtener directorio temporal y construir ruta única
    final dir = await getTemporaryDirectory();
    final path =
        '${dir.path}/voice_note_${DateTime.now().millisecondsSinceEpoch}.m4a';

    // Iniciar grabación con codec AAC-LC (compatible Android + iOS)
    await _audioRecorder.start(
      const RecordConfig(encoder: AudioEncoder.aacLc),
      path: path,
    );

    setState(() {
      _isRecording = true;
      _recordingSeconds = 0;
      _audioPath = null;
    });
    _recordingTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() => _recordingSeconds++);
    });
  }

  Future<void> _stopRecording() async {
    _recordingTimer?.cancel();
    final path = await _audioRecorder.stop();
    setState(() {
      _isRecording = false;
      _audioPath = path;
    });
  }

  Future<void> _deleteAudio() async {
    // Eliminar el archivo del sistema para liberar espacio
    if (_audioPath != null) {
      final file = File(_audioPath!);
      if (await file.exists()) await file.delete();
    }
    _recordingTimer?.cancel();
    setState(() {
      _isRecording = false;
      _recordingSeconds = 0;
      _audioPath = null;
    });
  }

  String _formatTimer(int seconds) {
    final mins = (seconds ~/ 60).toString().padLeft(2, '0');
    final secs = (seconds % 60).toString().padLeft(2, '0');
    return '$mins:$secs';
  }

  // ─────────────────────────── Envío ───────────────────────────────────

  Future<void> _sendReport(BuildContext context) async {
    final provider = context.read<ReportProvider>();
    // Capturar messenger y navigator ANTES del gap asíncrono
    final messenger = ScaffoldMessenger.of(context);
    final navigator = Navigator.of(context);

    final success = await provider.submitReport(
      imagePath: _imageFile?.path,
      audioPath: _audioPath,
      optionalText: _detailsController.text.trim().isEmpty
          ? null
          : _detailsController.text.trim(),
      vehicleId: widget.vehicleId,
    );

    if (!mounted) return;

    if (success) {
      messenger
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            backgroundColor: AppColors.primaryBlue,
            content: Text('Reporte enviado correctamente.'),
          ),
        );
      navigator.pushReplacement(
        MaterialPageRoute(builder: (_) => const WaitingHelpPage()),
      );
      return;
    }

    messenger
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          backgroundColor: AppColors.redDanger,
          content: Text(
            provider.errorMessage ?? 'No se pudo enviar el reporte.',
          ),
        ),
      );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(backgroundColor: AppColors.redDanger, content: Text(message)),
      );
  }

  // ─────────────────────────── UI ──────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        scrolledUnderElevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.textMain),
        ),
        title: const Text(
          'Nuevo Reporte',
          style: TextStyle(
            color: AppColors.textMain,
            fontSize: 20,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Paso 1: Cámara ──
            const _StepLabel(label: 'Paso 1: Foto del daño'),
            const SizedBox(height: 10),
            _CameraCard(
              imageFile: _imageFile,
              isLoading: _isPickingImage,
              onTap: () => _showImageSourceDialog(context),
              onDiscard: _discardImage,
              onShowFullScreen: () => _showFullScreenImage(context),
            ),

            const SizedBox(height: 24),

            // ── Paso 2: Audio ──
            const _StepLabel(label: 'Paso 2: Nota de voz'),
            const SizedBox(height: 10),
            _AudioRecorderCard(
              isRecording: _isRecording,
              recordingSeconds: _recordingSeconds,
              audioPath: _audioPath,
              formatTimer: _formatTimer,
              onStartRecording: () => _startRecording(),
              onStopRecording: () => _stopRecording(),
              onDiscard: () => _deleteAudio(),
            ),

            const SizedBox(height: 24),

            // ── Paso 3: Texto opcional ──
            const _StepLabel(label: 'Detalles adicionales (Opcional)'),
            const SizedBox(height: 10),
            CustomInput(
              controller: _detailsController,
              hintText: 'Ej. Estoy junto al portón verde...',
              keyboardType: TextInputType.multiline,
              textInputAction: TextInputAction.newline,
              maxLines: 4,
            ),

            const SizedBox(height: 8),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Consumer<ReportProvider>(
            builder: (context, reportProvider, _) {
              return CustomButton(
                text: 'Enviar Reporte al Taller',
                isLoading: reportProvider.isSubmitting,
                onPressed: reportProvider.isSubmitting
                    ? null
                    : () => _sendReport(context),
              );
            },
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Widgets privados de esta pantalla
// ═══════════════════════════════════════════════════════════════════════

/// Etiqueta de paso con tipografía estándar del proyecto.
class _StepLabel extends StatelessWidget {
  const _StepLabel({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: const TextStyle(
        color: AppColors.textMain,
        fontSize: 14,
        fontWeight: FontWeight.w700,
      ),
    );
  }
}

// ───────────────────────────────────────────────────────────────────────
// Tarjeta de Cámara
// ───────────────────────────────────────────────────────────────────────

class _CameraCard extends StatelessWidget {
  const _CameraCard({
    required this.imageFile,
    required this.isLoading,
    required this.onTap,
    required this.onDiscard,
    required this.onShowFullScreen,
  });

  final File? imageFile;
  final bool isLoading;
  final VoidCallback onTap;
  final VoidCallback onDiscard;
  final VoidCallback onShowFullScreen;

  @override
  Widget build(BuildContext context) {
    final hasImage = imageFile != null;

    return Container(
      height: 200,
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: hasImage ? AppColors.primaryBlue : AppColors.borderSide,
          width: 1.5,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: hasImage
          ? _ImagePreview(
              imageFile: imageFile!,
              onDiscard: onDiscard,
              onTap: onShowFullScreen,
            )
          : _CameraPlaceholder(isLoading: isLoading, onTap: onTap),
    );
  }
}

class _CameraPlaceholder extends StatelessWidget {
  const _CameraPlaceholder({required this.isLoading, required this.onTap});
  final bool isLoading;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: isLoading ? null : onTap,
        child: Center(
          child: isLoading
              ? const CircularProgressIndicator(color: AppColors.primaryBlue)
              : const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.camera_alt_outlined,
                      size: 44,
                      color: AppColors.primaryBlue,
                    ),
                    SizedBox(height: 10),
                    Text(
                      'Tomar foto del daño',
                      style: TextStyle(
                        color: AppColors.textMain,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Toca para abrir la cámara',
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class _ImagePreview extends StatelessWidget {
  const _ImagePreview({
    required this.imageFile,
    required this.onDiscard,
    required this.onTap,
  });
  final File imageFile;
  final VoidCallback onDiscard;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Imagen tocable — abre el visor a pantalla completa
        GestureDetector(
          onTap: onTap,
          child: Image.file(
            imageFile,
            width: double.infinity,
            height: double.infinity,
            fit: BoxFit.cover,
          ),
        ),
        // Botón ✕ de descarte — independiente del tap de la imagen
        Positioned(
          top: 8,
          right: 8,
          child: GestureDetector(
            onTap: onDiscard,
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.textMain.withValues(alpha: 0.65),
                shape: BoxShape.circle,
              ),
              padding: const EdgeInsets.all(4),
              child: const Icon(Icons.close, color: AppColors.white, size: 20),
            ),
          ),
        ),
      ],
    );
  }
}

// ───────────────────────────────────────────────────────────────────────
// Tarjeta de Grabación de Audio
// ───────────────────────────────────────────────────────────────────────

class _AudioRecorderCard extends StatelessWidget {
  const _AudioRecorderCard({
    required this.isRecording,
    required this.recordingSeconds,
    required this.audioPath,
    required this.formatTimer,
    required this.onStartRecording,
    required this.onStopRecording,
    required this.onDiscard,
  });

  final bool isRecording;
  final int recordingSeconds;
  final String? audioPath;
  final String Function(int) formatTimer;
  final VoidCallback onStartRecording;
  final VoidCallback onStopRecording;
  final VoidCallback onDiscard;

  @override
  Widget build(BuildContext context) {
    final hasAudio = audioPath != null;

    // Color del borde según estado:
    // Grabando → redDanger, Grabado → primaryBlue, Inicial → borderSide
    final borderColor = isRecording
        ? AppColors.redDanger
        : hasAudio
        ? AppColors.primaryBlue
        : AppColors.borderSide;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      height: 150,
      width: double.infinity,
      decoration: BoxDecoration(
        color: isRecording
            ? AppColors.redDanger.withValues(alpha: 0.04)
            : AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor, width: 1.5),
      ),
      child: hasAudio
          ? _AudioDoneState(
              durationSeconds: recordingSeconds,
              onDiscard: onDiscard,
            )
          : isRecording
          ? _AudioRecordingState(
              seconds: recordingSeconds,
              formatTimer: formatTimer,
              onStop: onStopRecording,
            )
          : _AudioIdleState(onStart: onStartRecording),
    );
  }
}

class _AudioIdleState extends StatelessWidget {
  const _AudioIdleState({required this.onStart});
  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onStart,
        child: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.mic_none_outlined,
                size: 44,
                color: AppColors.redDanger,
              ),
              SizedBox(height: 10),
              Text(
                'Grabar nota de voz',
                style: TextStyle(
                  color: AppColors.textMain,
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
              SizedBox(height: 4),
              Text(
                'Toca para iniciar la grabación',
                style: TextStyle(color: AppColors.textMuted, fontSize: 13),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AudioRecordingState extends StatelessWidget {
  const _AudioRecordingState({
    required this.seconds,
    required this.formatTimer,
    required this.onStop,
  });

  final int seconds;
  final String Function(int) formatTimer;
  final VoidCallback onStop;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            formatTimer(seconds),
            style: const TextStyle(
              color: AppColors.redDanger,
              fontSize: 32,
              fontWeight: FontWeight.w800,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Grabando...',
            style: TextStyle(
              color: AppColors.redDanger,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 14),
          GestureDetector(
            onTap: onStop,
            child: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.redDanger,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.stop, color: AppColors.white, size: 28),
            ),
          ),
        ],
      ),
    );
  }
}

class _AudioDoneState extends StatelessWidget {
  const _AudioDoneState({
    required this.durationSeconds,
    required this.onDiscard,
  });
  final int durationSeconds;
  final VoidCallback onDiscard;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          const Icon(
            Icons.check_circle,
            color: AppColors.primaryBlue,
            size: 32,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Audio capturado',
                  style: TextStyle(
                    color: AppColors.textMain,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '$durationSeconds seg grabados',
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: onDiscard,
            icon: const Icon(
              Icons.delete_outline,
              color: AppColors.textMuted,
              size: 22,
            ),
            tooltip: 'Eliminar audio',
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Visor de imagen a pantalla completa
// ═══════════════════════════════════════════════════════════════════════

class _FullScreenImageViewer extends StatelessWidget {
  const _FullScreenImageViewer({required this.imageFile});
  final File imageFile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // — Imagen con zoom y pan —
          Center(
            child: InteractiveViewer(
              minScale: 0.5,
              maxScale: 4.0,
              child: Image.file(imageFile, fit: BoxFit.contain),
            ),
          ),
          // — Botón de cierre —
          Positioned(
            top: MediaQuery.of(context).padding.top + 8,
            left: 8,
            child: IconButton(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.close, color: Colors.white, size: 28),
              style: IconButton.styleFrom(
                backgroundColor: Colors.black45,
                shape: const CircleBorder(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
