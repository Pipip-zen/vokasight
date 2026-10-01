import 'dart:async';
import 'dart:io';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../models/history_item_model.dart';
import '../../services/api_service.dart';
import '../../services/local_storage_service.dart';
import 'inspection_state.dart';

class InspectionCubit extends Cubit<InspectionState> {
  final ApiService _apiService;
  final LocalStorageService _localStorageService;
  bool _isCancelled = false;

  InspectionCubit({
    ApiService? apiService,
    LocalStorageService? localStorageService,
  })  : _apiService = apiService ?? ApiService(),
        _localStorageService = localStorageService ?? LocalStorageService(),
        super(InspectionInitial());

  Future<void> startInspection({
    required File imageFile,
    required String moduleId,
    required String moduleName,
    required String studentId,
    String? roboflowKey,
  }) async {
    _isCancelled = false;
    emit(InspectionUploading());

    try {
      // 1. Submit Inspection Image
      final task = await _apiService.submitInspection(
        imageFile: imageFile,
        moduleId: moduleId,
        studentId: studentId,
        roboflowKey: roboflowKey,
      );

      // 2. Start Polling Loop (interval 2 detik, max 30 percobaan = 60 detik)
      int attempts = 0;
      const maxAttempts = 30;

      while (attempts < maxAttempts && !_isCancelled) {
        attempts++;
        emit(InspectionPolling(
          taskId: task.taskId,
          attempt: attempts,
          statusMessage: 'Memproses OpenCV & Deteksi AI (Percobaan $attempts)...',
        ));

        await Future.delayed(const Duration(seconds: 2));

        if (_isCancelled) return;

        try {
          final result = await _apiService.getInspectionResult(task.taskId);

          if (result.status.toLowerCase() == 'completed') {
            // Simpan otomatis ke riwayat offline lokal
            final historyItem = HistoryItemModel(
              id: result.taskId,
              taskId: result.taskId,
              studentId: studentId,
              moduleId: moduleId,
              moduleName: moduleName,
              score: result.score,
              defectCount: result.detectedDefects.length,
              imagePath: imageFile.path,
              createdAt: DateTime.now(),
              result: result,
            );
            await _localStorageService.saveHistoryItem(historyItem);

            emit(InspectionSuccess(
              result: result,
              localImagePath: imageFile.path,
            ));
            return;
          } else if (result.status.toLowerCase() == 'failed') {
            emit(InspectionFailure(
              result.lightingWarning ?? 'Proses inspeksi gagal dieksekusi server.',
            ));
            return;
          }
        } catch (pollErr) {
          // Jika backend masih sibuk atau network timeout sementara, teruskan polling
          if (attempts >= maxAttempts) {
            emit(InspectionFailure(
              'Waktu tunggu analisis habis (timeout). Silakan periksa koneksi atau coba lagi.',
            ));
            return;
          }
        }
      }

      if (!_isCancelled && attempts >= maxAttempts) {
        emit(InspectionFailure('Batas waktu polling tercapai. Silakan coba kembali.'));
      }
    } catch (e) {
      if (!_isCancelled) {
        emit(InspectionFailure(e.toString().replaceAll('Exception: ', '')));
      }
    }
  }

  void cancelInspection() {
    _isCancelled = true;
    emit(InspectionInitial());
  }

  void reset() {
    _isCancelled = false;
    emit(InspectionInitial());
  }
}
