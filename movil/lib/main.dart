import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:movil/core/theme/app_colors.dart';
import 'package:movil/data/repositories/api_auth_repository.dart';
import 'package:movil/data/repositories/api_emergency_repository.dart';
import 'package:movil/data/repositories/api_vehicle_repository.dart';
import 'package:movil/domain/repositories/auth_repository.dart';
import 'package:movil/domain/repositories/emergency_repository.dart';
import 'package:movil/domain/usecases/login_usecase.dart';
import 'package:movil/domain/usecases/register_usecase.dart';
import 'package:movil/domain/usecases/submit_report_usecase.dart';
import 'package:movil/presentation/pages/login/login_page.dart';
import 'package:movil/presentation/providers/auth_provider.dart';
import 'package:movil/presentation/providers/report_provider.dart';
import 'package:movil/presentation/providers/vehicle_provider.dart';

void main() {
  runApp(const EmergencyClientApp());
}

class EmergencyClientApp extends StatelessWidget {
  const EmergencyClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    final authRepository = ApiAuthRepository();
    final emergencyRepository = ApiEmergencyRepository();
    final vehicleRepository = ApiVehicleRepository();

    return MultiProvider(
      providers: [
        Provider<AuthRepository>.value(value: authRepository),
        Provider<EmergencyRepository>.value(value: emergencyRepository),
        ChangeNotifierProvider<AuthProvider>(
          create: (context) => AuthProvider(
            loginUseCase: LoginUseCase(context.read<AuthRepository>()),
            registerUseCase: RegisterUseCase(context.read<AuthRepository>()),
            authRepository: context.read<AuthRepository>(),
          ),
        ),
        ChangeNotifierProvider<ReportProvider>(
          create: (context) => ReportProvider(
            submitReportUseCase: SubmitReportUseCase(
              context.read<EmergencyRepository>(),
            ),
          ),
        ),
        ChangeNotifierProvider<VehicleProvider>(
          create: (_) => VehicleProvider(vehicleRepository),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Plataforma de Emergencias',
        theme: ThemeData(
          useMaterial3: true,
          fontFamily: 'Roboto',
          scaffoldBackgroundColor: AppColors.background,
          colorScheme: const ColorScheme.light(
            primary: AppColors.primaryBlue,
            secondary: AppColors.amber,
            surface: AppColors.white,
            error: AppColors.redDanger,
          ),
        ),
        home: LoginPage(),
      ),
    );
  }
}

class MyApp extends EmergencyClientApp {
  const MyApp({super.key});
}
