import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late Dio _dio;

  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.compileTimeBaseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Accept': 'application/json',
        },
      ),
    );
  }

  Dio get client => _dio;

  Future<void> initBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final customUrl = prefs.getString(ApiConstants.prefBaseUrlKey);
    if (customUrl != null && customUrl.trim().isNotEmpty) {
      _dio.options.baseUrl = customUrl.trim();
    }
  }

  Future<void> setBaseUrl(String newBaseUrl) async {
    _dio.options.baseUrl = newBaseUrl.trim();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(ApiConstants.prefBaseUrlKey, newBaseUrl.trim());
  }

  String get currentBaseUrl => _dio.options.baseUrl;
}
