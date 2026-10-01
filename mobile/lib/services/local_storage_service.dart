import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants/api_constants.dart';
import '../models/history_item_model.dart';

class LocalStorageService {
  static final LocalStorageService _instance = LocalStorageService._internal();
  factory LocalStorageService() => _instance;
  LocalStorageService._internal();

  /// Menyimpan NIM mahasiswa terakhir
  Future<void> saveStudentId(String studentId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(ApiConstants.prefStudentIdKey, studentId.trim());
  }

  /// Mengambil NIM mahasiswa terakhir
  Future<String?> getStudentId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(ApiConstants.prefStudentIdKey);
  }

  /// Menyimpan item riwayat inspeksi baru ke local cache
  Future<void> saveHistoryItem(HistoryItemModel item) async {
    final prefs = await SharedPreferences.getInstance();
    List<HistoryItemModel> currentList = await getHistoryList();

    // Hapus jika sudah ada id yang sama (avoid duplicate)
    currentList.removeWhere((h) => h.taskId == item.taskId || h.id == item.id);
    
    // Masukkan ke posisi paling atas (terbaru)
    currentList.insert(0, item);

    // Batasi maksimum 50 item riwayat offline
    if (currentList.length > 50) {
      currentList = currentList.sublist(0, 50);
    }

    final rawJsonList = currentList.map((h) => h.toJson()).toList();
    await prefs.setString(ApiConstants.prefHistoryKey, jsonEncode(rawJsonList));
  }

  /// Mengambil seluruh riwayat inspeksi offline
  Future<List<HistoryItemModel>> getHistoryList() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = prefs.getString(ApiConstants.prefHistoryKey);
    if (jsonString == null || jsonString.isEmpty) {
      return [];
    }

    try {
      final List decoded = jsonDecode(jsonString);
      return decoded
          .map((item) => HistoryItemModel.fromJson(Map<String, dynamic>.from(item)))
          .toList();
    } catch (_) {
      return [];
    }
  }

  /// Menghapus item riwayat tertentu
  Future<void> deleteHistoryItem(String id) async {
    final prefs = await SharedPreferences.getInstance();
    List<HistoryItemModel> currentList = await getHistoryList();
    currentList.removeWhere((item) => item.id == id || item.taskId == id);

    final rawJsonList = currentList.map((h) => h.toJson()).toList();
    await prefs.setString(ApiConstants.prefHistoryKey, jsonEncode(rawJsonList));
  }

  /// Menghapus seluruh riwayat inspeksi
  Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(ApiConstants.prefHistoryKey);
  }
}
