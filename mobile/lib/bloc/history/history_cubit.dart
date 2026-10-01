import 'package:flutter_bloc/flutter_bloc.dart';
import '../../services/local_storage_service.dart';
import 'history_state.dart';

class HistoryCubit extends Cubit<HistoryState> {
  final LocalStorageService _localStorageService;

  HistoryCubit({LocalStorageService? localStorageService})
      : _localStorageService = localStorageService ?? LocalStorageService(),
        super(HistoryInitial());

  Future<void> loadHistory() async {
    emit(HistoryLoading());
    try {
      final items = await _localStorageService.getHistoryList();
      emit(HistoryLoaded(items));
    } catch (e) {
      emit(HistoryError('Gagal memuat riwayat inspeksi lokal: $e'));
    }
  }

  Future<void> deleteHistoryItem(String id) async {
    try {
      await _localStorageService.deleteHistoryItem(id);
      await loadHistory();
    } catch (e) {
      emit(HistoryError('Gagal menghapus riwayat: $e'));
    }
  }

  Future<void> clearAllHistory() async {
    try {
      await _localStorageService.clearHistory();
      emit(HistoryLoaded([]));
    } catch (e) {
      emit(HistoryError('Gagal membersihkan riwayat: $e'));
    }
  }
}
