import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/app_logo.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/core/widgets/custom_input.dart';
import 'package:movil/presentation/pages/main_wrapper.dart';
import 'package:movil/presentation/providers/auth_provider.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage>
    with SingleTickerProviderStateMixin {
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  late final AnimationController _animController;
  late final Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _fadeAnim = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _fullNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: AppColors.background,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.arrow_back_ios_new,
              color: AppColors.textMain, size: 20),
        ),
        title: const AppLogo(size: AppLogoSize.small),
      ),
      body: Stack(
        children: [
          // ── Círculos decorativos ──────────────────────────────────────
          Stack(
            children: [
              Positioned(
                top: -60,
                right: -60,
                child: Container(
                  width: 200,
                  height: 200,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.primaryBlue.withValues(alpha: 0.06),
                  ),
                ),
              ),
              Positioned(
                bottom: -80,
                left: -70,
                child: Container(
                  width: 240,
                  height: 240,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.amber.withValues(alpha: 0.05),
                  ),
                ),
              ),
            ],
          ),

          // ── Contenido ─────────────────────────────────────────────────
          Consumer<AuthProvider>(
            builder: (context, authProvider, _) {
              if (authProvider.errorMessage != null) {
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context)
                    ..hideCurrentSnackBar()
                    ..showSnackBar(SnackBar(
                      backgroundColor: AppColors.redDanger,
                      content: Text(authProvider.errorMessage!),
                    ));
                  authProvider.clearError();
                });
              }

              return FadeTransition(
                opacity: _fadeAnim,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Crea tu cuenta',
                        style: TextStyle(
                          color: AppColors.textMain,
                          fontSize: 30,
                          fontWeight: FontWeight.w800,
                          height: 1.1,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Regístrate para recibir asistencia técnica inmediata.',
                        style: TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 24),

                      // ── Tarjeta de formulario ────────────────────────
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(22),
                        decoration: BoxDecoration(
                          color: AppColors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: AppColors.borderSide,
                            width: 1.5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.05),
                              blurRadius: 18,
                              offset: const Offset(0, 6),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            CustomInput(
                              controller: _fullNameController,
                              labelText: 'Nombre Completo',
                              hintText: 'Ej. María González',
                              textInputAction: TextInputAction.next,
                              prefixIcon: const Icon(Icons.person_outline,
                                  color: AppColors.textMuted, size: 20),
                            ),
                            const SizedBox(height: 14),
                            CustomInput(
                              controller: _emailController,
                              labelText: 'Correo Electrónico',
                              hintText: 'nombre@correo.com',
                              keyboardType: TextInputType.emailAddress,
                              textInputAction: TextInputAction.next,
                              prefixIcon: const Icon(Icons.email_outlined,
                                  color: AppColors.textMuted, size: 20),
                            ),
                            const SizedBox(height: 14),
                            CustomInput(
                              controller: _phoneController,
                              labelText: 'Número de Celular',
                              hintText: 'Ej. 70000000',
                              keyboardType: TextInputType.phone,
                              textInputAction: TextInputAction.next,
                              prefixIcon: const Icon(Icons.phone_outlined,
                                  color: AppColors.textMuted, size: 20),
                            ),
                            const SizedBox(height: 14),
                            CustomInput(
                              controller: _passwordController,
                              labelText: 'Contraseña',
                              hintText: 'Mínimo 8 caracteres',
                              obscureText: _obscurePassword,
                              textInputAction: TextInputAction.next,
                              prefixIcon: const Icon(Icons.lock_outline,
                                  color: AppColors.textMuted, size: 20),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_off_outlined
                                      : Icons.visibility_outlined,
                                  color: AppColors.textMuted,
                                  size: 20,
                                ),
                                onPressed: () => setState(
                                  () => _obscurePassword = !_obscurePassword,
                                ),
                              ),
                            ),
                            const SizedBox(height: 14),
                            CustomInput(
                              controller: _confirmPasswordController,
                              labelText: 'Confirmar Contraseña',
                              hintText: 'Repite tu contraseña',
                              obscureText: _obscureConfirm,
                              textInputAction: TextInputAction.done,
                              prefixIcon: const Icon(Icons.lock_outline,
                                  color: AppColors.textMuted, size: 20),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscureConfirm
                                      ? Icons.visibility_off_outlined
                                      : Icons.visibility_outlined,
                                  color: AppColors.textMuted,
                                  size: 20,
                                ),
                                onPressed: () => setState(
                                  () => _obscureConfirm = !_obscureConfirm,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 28),

                      CustomButton(
                        text: 'Registrarse ahora',
                        isLoading: authProvider.isLoading,
                        onPressed: authProvider.isLoading
                            ? null
                            : () async {
                                final password =
                                    _passwordController.text.trim();
                                final confirm =
                                    _confirmPasswordController.text.trim();

                                if (password != confirm) {
                                  ScaffoldMessenger.of(context)
                                    ..hideCurrentSnackBar()
                                    ..showSnackBar(const SnackBar(
                                      backgroundColor: AppColors.redDanger,
                                      content: Text(
                                          'Las contraseñas no coinciden.'),
                                    ));
                                  return;
                                }

                                final success = await authProvider.register(
                                  _fullNameController.text,
                                  _emailController.text,
                                  _phoneController.text,
                                  password,
                                );

                                if (!context.mounted || !success) return;

                                Navigator.pushReplacement(
                                  context,
                                  MaterialPageRoute<void>(
                                    builder: (_) => const MainWrapper(),
                                  ),
                                );
                              },
                      ),

                      const SizedBox(height: 24),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Text(
                            '¿Ya tienes cuenta? ',
                            style: TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          GestureDetector(
                            onTap: () => Navigator.pop(context),
                            child: const Text(
                              'Inicia sesión',
                              style: TextStyle(
                                color: AppColors.primaryBlue,
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
