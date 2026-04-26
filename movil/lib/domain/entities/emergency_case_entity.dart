class EmergencyCaseEntity {
  const EmergencyCaseEntity({
    required this.id,
    required this.caseCode,
    required this.status,
    required this.location,
    required this.summary,
    required this.reportedAt,
    required this.gpsActive,
  });

  final String id;
  final String caseCode;
  final String status;
  final String location;
  final String summary;
  final DateTime reportedAt;
  final bool gpsActive;
}
