import 'package:flutter/material.dart';

class AppColors {
  // Primarios (Confianza y Estructura)
  static const Color primaryBlue = Color(0xFF1D4ED8); // blue-700
  static const Color darkBlue = Color(0xFF1E3A8A); // blue-900
  static const Color lightBlueBg = Color(
    0xFFEFF6FF,
  ); // blue-50 (Para bloques de IA)
  static const Color aiBg = Color(0xFFEFF6FF); // blue-50 (Alias semantico IA)

  // Alertas y Acción (Emergencias)
  static const Color amber = Color(0xFFF59E0B); // amber-500
  static const Color redDanger = Color(0xFFDC2626); // red-600 (Botón de pánico)

  // Neutros (Base del sistema)
  static const Color background = Color(0xFFF9FAFB); // gray-50
  static const Color white = Color(0xFFFFFFFF);
  static const Color borderSide = Color(0xFFE5E7EB); // border-gray-200
  static const Color textMain = Color(0xFF111827); // text-gray-900
  static const Color textMuted = Color(0xFF6B7280); // text-gray-500
}
