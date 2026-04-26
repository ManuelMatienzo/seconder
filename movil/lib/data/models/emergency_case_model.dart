import 'package:movil/domain/entities/emergency_case_entity.dart';

class EmergencyCaseModel extends EmergencyCaseEntity {
  const EmergencyCaseModel({
    required super.id,
    required super.caseCode,
    required super.status,
    required super.location,
    required super.summary,
    required super.reportedAt,
    required super.gpsActive,
  });

  factory EmergencyCaseModel.fromJson(Map<String, dynamic> json) {
    return EmergencyCaseModel(
      id: json['id'] as String,
      caseCode: json['caseCode'] as String,
      status: json['status'] as String,
      location: json['location'] as String,
      summary: json['summary'] as String,
      reportedAt: DateTime.parse(json['reportedAt'] as String),
      gpsActive: json['gpsActive'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'caseCode': caseCode,
      'status': status,
      'location': location,
      'summary': summary,
      'reportedAt': reportedAt.toIso8601String(),
      'gpsActive': gpsActive,
    };
  }
}
