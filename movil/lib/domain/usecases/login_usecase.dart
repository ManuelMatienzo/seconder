import 'package:movil/domain/entities/user.dart';
import 'package:movil/domain/repositories/auth_repository.dart';

class LoginUseCase {
  const LoginUseCase(this._authRepository);

  final AuthRepository _authRepository;

  Future<User> execute(String email, String password) {
    return _authRepository.login(email, password);
  }
}
