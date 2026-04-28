import 'package:movil/data/models/user_model.dart';
import 'package:movil/domain/entities/user.dart';
import 'package:movil/domain/repositories/auth_repository.dart';

class MockAuthRepository implements AuthRepository {
  @override
  Future<User> login(String email, String password) async {
    await Future.delayed(const Duration(seconds: 2));

    if (email.trim().toLowerCase() == 'admin@test.com') {
      return const UserModel(
        id: 'u-001',
        email: 'admin@test.com',
        name: 'Operador Principal',
        role: 'ADMIN',
      );
    }

    throw Exception('Credenciales inválidas');
  }

  @override
  Future<User> register(
    String fullName,
    String email,
    String phone,
    String password,
  ) async {
    await Future.delayed(const Duration(seconds: 2));

    return UserModel(
      id: 'u-100',
      email: email.trim().toLowerCase(),
      name: fullName.trim().isEmpty ? 'Cliente Nuevo' : fullName.trim(),
      role: 'CLIENTE',
    );
  }

  @override
  Future<void> logout() async {
    await Future.delayed(const Duration(milliseconds: 500));
  }
}
