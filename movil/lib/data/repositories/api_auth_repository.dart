import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:movil/data/models/user_model.dart';
import 'package:movil/domain/entities/user.dart';
import 'package:movil/domain/repositories/auth_repository.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

String getBaseUrl() {
  if (kIsWeb) return 'http://localhost:8000';
  
  // URL de producción en Render
  const String prodUrl = 'https://mechsmart-g45.onrender.com';
  
  // Si estamos en desarrollo físico usamos la IP, si no, la de producción
  bool isProduction = bool.fromEnvironment('dart.vm.product');
  if (isProduction) return prodUrl;

  return 'http://192.168.0.11:8000';
}

class ApiAuthRepository implements AuthRepository {
  static String? accessToken;
  final String baseUrl = getBaseUrl();

  @override
  Future<User> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      accessToken = data['access_token'];
      final userJson = data['user'];
      return UserModel(
        id: userJson['id_user'].toString(),
        email: userJson['email'],
        name: userJson['name'],
        role: userJson['role'] != null ? userJson['role']['name'] : 'CLIENTE',
        phone: userJson['phone'],
      );
    } else {
      throw Exception('Credenciales inválidas');
    }
  }

  @override
  Future<User> register(String fullName, String email, String phone, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/clients'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': fullName,
        'email': email,
        'phone': phone,
        'password': password,
      }),
    );

    if (response.statusCode == 201) {
      // Auto-login
      return await login(email, password);
    } else {
      throw Exception('Error al registrar usuario');
    }
  }

  @override
  Future<void> logout() async {
    accessToken = null;
  }
}
