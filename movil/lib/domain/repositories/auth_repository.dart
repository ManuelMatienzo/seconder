import 'package:movil/domain/entities/user.dart';

abstract class AuthRepository {
  Future<User> login(String email, String password);

  Future<User> register(
    String fullName,
    String email,
    String phone,
    String password,
  );

  Future<void> logout();
}
