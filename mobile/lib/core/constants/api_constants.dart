class ApiConstants {
  // Can be configured at build time using:
  // flutter run --dart-define=BASE_URL=http://192.168.1.10:8000/api/v1
  // Default to 10.0.2.2 for Android Emulator, or localhost for Windows/Web
  static const String compileTimeBaseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  static const String prefBaseUrlKey = 'vokasight_custom_base_url';
  static const String prefStudentIdKey = 'vokasight_last_student_id';
  static const String prefHistoryKey = 'vokasight_inspection_history';

  // Endpoints
  static const String modulesEndpoint = '/modules';
  static const String submitInspectionEndpoint = '/inspections';
  static String inspectionDetailEndpoint(String taskId) => '/inspections/$taskId';
}
