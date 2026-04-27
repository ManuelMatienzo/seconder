import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/core/widgets/app_logo.dart';
import 'package:movil/core/widgets/custom_button.dart';
import 'package:movil/core/widgets/custom_input.dart';
import 'package:movil/presentation/pages/main_wrapper.dart';
import 'package:movil/presentation/pages/register/register_page.dart';
import 'package:movil/presentation/providers/auth_provider.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage>
    with SingleTickerProviderStateMixin {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  late final AnimationController _animController;
  late final Animation<double> _fadeAnim;
  late final Animation<Offset> _slideLogoAnim;
  late final Animation<Offset> _slideCardAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );

    final curved = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
    final curvedDelayed = CurvedAnimation(
      parent: _animController,
      curve: const Interval(0.18, 1.0, curve: Curves.easeOut),
    );

    _fadeAnim = Tween<double>(begin: 0, end: 1).animate(curved);
    _slideLogoAnim = Tween<Offset>(
      begin: const Offset(0, -0.18),
      end: Offset.zero,
    ).animate(curved);
    _slideCardAnim = Tween<Offset>(
      begin: const Offset(0, 0.18),
      end: Offset.zero,
    ).animate(curvedDelayed);

    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, _) {
          // Mostrar errores del provider
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

          return Stack(
            children: [
              // ── Círculos decorativos de fondo ──────────────────────────
              const _DecorativeCircles(),

              // ── Contenido principal ────────────────────────────────────
              SafeArea(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      const SizedBox(height: 56),

                      // Logo animado
                      FadeTransition(
                        opacity: _fadeAnim,
                        child: SlideTransition(
                          position: _slideLogoAnim,
                          child: const AppLogo(size: AppLogoSize.large),
                        ),
                      ),

                      const SizedBox(height: 40),

                      // Tarjeta de formulario animada
                      FadeTransition(
                        opacity: _fadeAnim,
                        child: SlideTransition(
                          position: _slideCardAnim,
                          child: Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(24),
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
                                  blurRadius: 20,
                                  offset: const Offset(0, 6),
                                ),
                              ],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Bienvenido de vuelta',
                                  style: TextStyle(
                                    color: AppColors.textMain,
                                    fontSize: 22,
                                    fontWeight: FontWeight.w800,
                                    height: 1.1,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'Accede de forma segura al panel móvil de emergencias.',
                                  style: TextStyle(
                                    color: AppColors.textMuted,
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 22),

                                // Email
                                CustomInput(
                                  controller: _emailController,
                                  labelText: 'Correo electrónico',
                                  hintText: 'admin@test.com',
                                  keyboardType: TextInputType.emailAddress,
                                  textInputAction: TextInputAction.next,
                                  prefixIcon: const Icon(
                                    Icons.email_outlined,
                                    color: AppColors.textMuted,
                                    size: 20,
                                  ),
                                ),
                                const SizedBox(height: 14),

                                // Contraseña con toggle
                                CustomInput(
                                  controller: _passwordController,
                                  labelText: 'Contraseña',
                                  hintText: 'Ingresa tu clave',
                                  obscureText: _obscurePassword,
                                  textInputAction: TextInputAction.done,
                                  prefixIcon: const Icon(
                                    Icons.lock_outline,
                                    color: AppColors.textMuted,
                                    size: 20,
                                  ),
                                  suffixIcon: IconButton(
                                    icon: Icon(
                                      _obscurePassword
                                          ? Icons.visibility_off_outlined
                                          : Icons.visibility_outlined,
                                      color: AppColors.textMuted,
                                      size: 20,
                                    ),
                                    onPressed: () => setState(
                                      () => _obscurePassword =
                                          !_obscurePassword,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 24),

                                // Botón de ingreso
                                CustomButton(
                                  text: 'Ingresar',
                                  isLoading: authProvider.isLoading,
                                  onPressed: authProvider.isLoading
                                      ? null
                                      : () async {
                                          final success =
                                              await authProvider.login(
                                            _emailController.text,
                                            _passwordController.text,
                                          );
                                          if (!context.mounted || !success) {
                                            return;
                                          }
                                          Navigator.pushReplacement(
                                            context,
                                            MaterialPageRoute<void>(
                                              builder: (_) =>
                                                  const MainWrapper(),
                                            ),
                                          );
                                        },
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 28),

                      // Link a registro
                      FadeTransition(
                        opacity: _fadeAnim,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              '¿No tienes cuenta? ',
                              style: TextStyle(
                                color: AppColors.textMuted,
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            GestureDetector(
                              onTap: () => Navigator.push(
                                context,
                                MaterialPageRoute<void>(
                                  builder: (_) => const RegisterPage(),
                                ),
                              ),
                              child: const Text(
                                'Regístrate',
                                style: TextStyle(
                                  color: AppColors.primaryBlue,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Círculos decorativos de fondo
// ═══════════════════════════════════════════════════════════════════════

class _DecorativeCircles extends StatelessWidget {
  const _DecorativeCircles();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned(
          top: -70,
          right: -70,
          child: Container(
            width: 220,
            height: 220,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.primaryBlue.withValues(alpha: 0.07),
            ),
          ),
        ),
        Positioned(
          top: 60,
          right: -30,
          child: Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.amber.withValues(alpha: 0.06),
            ),
          ),
        ),
        Positioned(
          bottom: -90,
          left: -80,
          child: Container(
            width: 260,
            height: 260,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.primaryBlue.withValues(alpha: 0.05),
            ),
          ),
        ),
      ],
    );
  }
}
