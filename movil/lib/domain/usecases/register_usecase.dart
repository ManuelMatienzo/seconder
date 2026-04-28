import 'package:movil/domain/entities/user.dart';
import 'package:movil/domain/repositories/auth_repository.dart';

class RegisterUseCase {
  const RegisterUseCase(this._authRepository);

  final AuthRepository _authRepository;

  Future<User> execute(
    String fullName,
    String email,
    String phone,
    String password,
  ) {
    return _authRepository.register(fullName, email, phone, password);
  }
}
