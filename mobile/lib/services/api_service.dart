import 'dart:io';
import 'package:dio/dio.dart';
import '../core/constants/api_constants.dart';
import '../core/network/api_client.dart';
import '../models/module_model.dart';
import '../models/task_model.dart';
import '../models/inspection_result_model.dart';

class ApiService {
  final ApiClient _apiClient = ApiClient();

  /// Mengambil daftar modul praktikum (Zero-Auth)
  Future<List<ModuleModel>> getModules() async {
    try {
      final response = await _apiClient.client.get(ApiConstants.modulesEndpoint);
      if (response.statusCode == 200 && response.data is List) {
        return (response.data as List)
            .map((item) => ModuleModel.fromJson(Map<String, dynamic>.from(item)))
            .toList();
      }
      return [];
    } on DioException catch (e) {
      throw Exception(
        'Gagal memuat modul praktikum: ${e.response?.statusMessage ?? e.message}',
      );
    } catch (e) {
      throw Exception('Terjadi kesalahan jaringan: $e');
    }
  }

  /// Mengunggah foto PCB untuk inspeksi hardware AI (Async Submit)
  Future<TaskModel> submitInspection({
    required File imageFile,
    required String moduleId,
    String? studentId,
    String? roboflowKey,
  }) async {
    try {
      final fileName = imageFile.path.split(Platform.pathSeparator).last;
      
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          imageFile.path,
          filename: fileName,
        ),
        'module_id': moduleId,
        if (studentId != null && studentId.trim().isNotEmpty)
          'student_id': studentId.trim(),
        if (roboflowKey != null && roboflowKey.trim().isNotEmpty)
          'roboflow_key': roboflowKey.trim(),
      });

      final response = await _apiClient.client.post(
        ApiConstants.submitInspectionEndpoint,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );

      if (response.statusCode == 200 || response.statusCode == 202) {
        return TaskModel.fromJson(Map<String, dynamic>.from(response.data));
      } else {
        throw Exception('Server mengembalikan kode status: ${response.statusCode}');
      }
    } on DioException catch (e) {
      final errorDetail = e.response?.data?['detail'] ?? e.message;
      throw Exception('Gagal mengirim gambar untuk inspeksi: $errorDetail');
    } catch (e) {
      throw Exception('Gagal mengunggah foto: $e');
    }
  }

  /// Polling hasil inspeksi AI berdasarkan task_id
  Future<InspectionResultModel> getInspectionResult(String taskId) async {
    try {
      final endpoint = ApiConstants.inspectionDetailEndpoint(taskId);
      final response = await _apiClient.client.get(endpoint);

      if (response.statusCode == 200 && response.data != null) {
        return InspectionResultModel.fromJson(
          Map<String, dynamic>.from(response.data),
        );
      } else {
        throw Exception('Gagal mendapatkan hasil pemeriksaan: status ${response.statusCode}');
      }
    } on DioException catch (e) {
      final errorDetail = e.response?.data?['detail'] ?? e.message;
      throw Exception('Gagal polling status inspeksi: $errorDetail');
    } catch (e) {
      throw Exception('Gagal memproses hasil inspeksi: $e');
    }
  }
}
