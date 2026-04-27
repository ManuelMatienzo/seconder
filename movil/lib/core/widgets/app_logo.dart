import 'package:flutter/material.dart';
import 'package:movil/core/theme/app_colors.dart';

/// Tamaños disponibles del logo de marca MechSmart AI.
enum AppLogoSize { small, normal, large }

/// Widget de identidad visual de MechSmart AI.
/// Compuesto íntegramente por widgets Flutter — sin assets de imagen.
class AppLogo extends StatelessWidget {
  const AppLogo({super.key, this.size = AppLogoSize.normal});

  final AppLogoSize size;

  @override
  Widget build(BuildContext context) {
    final config = _LogoConfig.fromSize(size);

    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // ── Ícono circular ──────────────────────────────────────────────
        Container(
          width: config.circleSize,
          height: config.circleSize,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF2563EB), AppColors.primaryBlue],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppColors.primaryBlue.withValues(alpha: 0.30),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              Positioned(
                left: config.circleSize * 0.12,
                bottom: config.circleSize * 0.14,
                child: Icon(
                  Icons.build_rounded,
                  color: AppColors.white.withValues(alpha: 0.75),
                  size: config.iconSizePrimary,
                ),
              ),
              Positioned(
                right: config.circleSize * 0.10,
                top: config.circleSize * 0.12,
                child: Icon(
                  Icons.auto_awesome,
                  color: AppColors.amber,
                  size: config.iconSizeAccent,
                ),
              ),
            ],
          ),
        ),

        SizedBox(width: config.gap),

        // ── Texto de marca ──────────────────────────────────────────────
        Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'MECHSMART',
              style: TextStyle(
                color: AppColors.textMain,
                fontSize: config.titleSize,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.2,
                height: 1.0,
              ),
            ),
            Text(
              'AI',
              style: TextStyle(
                color: AppColors.primaryBlue,
                fontSize: config.subtitleSize,
                fontWeight: FontWeight.w600,
                letterSpacing: 3.0,
                height: 1.1,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// ── Configuración escalable ──────────────────────────────────────────────

class _LogoConfig {
  const _LogoConfig({
    required this.circleSize,
    required this.iconSizePrimary,
    required this.iconSizeAccent,
    required this.gap,
    required this.titleSize,
    required this.subtitleSize,
  });

  final double circleSize;
  final double iconSizePrimary;
  final double iconSizeAccent;
  final double gap;
  final double titleSize;
  final double subtitleSize;

  factory _LogoConfig.fromSize(AppLogoSize size) {
    switch (size) {
      case AppLogoSize.small:
        return const _LogoConfig(
          circleSize: 36,
          iconSizePrimary: 14,
          iconSizeAccent: 11,
          gap: 8,
          titleSize: 13,
          subtitleSize: 9,
        );
      case AppLogoSize.normal:
        return const _LogoConfig(
          circleSize: 48,
          iconSizePrimary: 19,
          iconSizeAccent: 14,
          gap: 10,
          titleSize: 17,
          subtitleSize: 11,
        );
      case AppLogoSize.large:
        return const _LogoConfig(
          circleSize: 68,
          iconSizePrimary: 27,
          iconSizeAccent: 20,
          gap: 14,
          titleSize: 24,
          subtitleSize: 15,
        );
    }
  }
}
