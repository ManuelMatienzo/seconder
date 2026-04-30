class User {
  const User({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.phone,
  });

  final String id;
  final String email;
  final String name;
  final String role;
  final String? phone;
}
