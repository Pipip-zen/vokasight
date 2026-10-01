import 'dart:io';
import 'package:flutter/material.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import '../core/constants/app_colors.dart';
import '../models/inspection_result_model.dart';
import '../models/module_model.dart';

class ResultScreen extends StatelessWidget {
  final InspectionResultModel result;
  final ModuleModel? module;
  final String? studentId;
  final String? localImagePath;

  const ResultScreen({
    super.key,
    required this.result,
    this.module,
    this.studentId,
    this.localImagePath,
  });

  Color _getScoreColor(double score) {
    if (score >= 80.0) return AppColors.success;
    if (score >= 60.0) return AppColors.warning;
    return AppColors.error;
  }

  String _getScoreStatus(double score) {
    if (score >= 80.0) return 'MEMENUHI STANDAR LAB';
    if (score >= 60.0) return 'PERLU PERBAIKAN MINOR';
    return 'TIDAK LOLOS / CACAT KRITIS';
  }

  @override
  Widget build(BuildContext context) {
    final scoreColor = _getScoreColor(result.score);
    final scoreStatus = _getScoreStatus(result.score);
    final normalizedScore = (result.score / 100.0).clamp(0.0, 1.0);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text(
          'Hasil Evaluasi Hardware',
          style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: AppColors.textPrimary),
        actions: [
          IconButton(
            icon: const Icon(Icons.home_outlined),
            tooltip: 'Ke Beranda',
            onPressed: () {
              Navigator.popUntil(context, (route) => route.isFirst);
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Score Indicator Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.cardBorder),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.03),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    CircularPercentIndicator(
                      radius: 75.0,
                      lineWidth: 12.0,
                      animation: true,
                      percent: normalizedScore,
                      center: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            result.score.toStringAsFixed(0),
                            style: TextStyle(
                              fontSize: 38,
                              fontWeight: FontWeight.w800,
                              color: scoreColor,
                            ),
                          ),
                          const Text(
                            '/ 100',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textMuted,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      circularStrokeCap: CircularStrokeCap.round,
                      progressColor: scoreColor,
                      backgroundColor: scoreColor.withValues(alpha: 0.15),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                      decoration: BoxDecoration(
                        color: scoreColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: scoreColor.withValues(alpha: 0.3)),
                      ),
                      child: Text(
                        scoreStatus,
                        style: TextStyle(
                          color: scoreColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 12.5,
                        ),
                      ),
                    ),
                    if (studentId != null || module != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        'Praktikan: ${studentId ?? "-"} • ${module?.name ?? result.moduleId}',
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                    ],
                  ],
                ),
              ),

              // Lighting Quality Alert (if any)
              if (result.lightingWarning != null && result.lightingWarning!.isNotEmpty) ...[
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFFFECACA)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: AppColors.error, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Peringatan Pencahayaan Citra',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                                color: AppColors.error,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              result.lightingWarning!,
                              style: const TextStyle(fontSize: 12, color: Color(0xFF991B1B)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // Inspected PCB Photo Thumbnail Preview
              if (localImagePath != null && File(localImagePath!).existsSync()) ...[
                const SizedBox(height: 20),
                const Text(
                  'Foto PCB yang Diperiksa',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  height: 180,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.cardBorder),
                    image: DecorationImage(
                      image: FileImage(File(localImagePath!)),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ],

              const SizedBox(height: 20),

              // Detected Defects Breakdown
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Cacat Terdeteksi (AI Defect)',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: result.detectedDefects.isEmpty
                          ? AppColors.success.withValues(alpha: 0.1)
                          : AppColors.error.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${result.detectedDefects.length} Cacat',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: result.detectedDefects.isEmpty ? AppColors.success : AppColors.error,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              if (result.detectedDefects.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFFBBF7D0)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.check_circle, color: AppColors.success, size: 22),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Sempurna! Tidak ada cacat soldering terdeteksi pada sambungan komponen ini.',
                          style: TextStyle(fontSize: 13, color: Color(0xFF166534), fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                )
              else
                Column(
                  children: result.detectedDefects.map((defect) {
                    final isBridge = defect.className.toLowerCase().contains('bridge') ||
                        defect.className.toLowerCase().contains('short');

                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.cardBorder),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: isBridge
                                  ? AppColors.error.withValues(alpha: 0.1)
                                  : AppColors.warning.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(
                              Icons.error_outline,
                              color: isBridge ? AppColors.error : AppColors.warning,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  defect.className.replaceAll('_', ' ').toUpperCase(),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 13.5,
                                    color: AppColors.textPrimary,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Akurasi: ${(defect.confidence * 100).toStringAsFixed(1)}% | BBox: ${defect.bbox.map((e) => e.toStringAsFixed(0)).join(', ')}',
                                  style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppColors.error.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              '-${defect.penalty.toStringAsFixed(0)} pt',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: AppColors.error,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),

              const SizedBox(height: 20),

              // Actionable Repair Recommendations
              const Text(
                '📋 Rekomendasi Perbaikan Langkah demi Langkah',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),

              if (result.recommendations.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppColors.cardBorder),
                  ),
                  child: const Text(
                    'Tidak ada rekomendasi khusus. Kualitas perakitan sudah baik.',
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                )
              else
                Column(
                  children: result.recommendations.map((rec) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF0FDF4),
                        borderRadius: BorderRadius.circular(10),
                        border: const Border(
                          left: BorderSide(color: AppColors.success, width: 4),
                          top: BorderSide(color: Color(0xFFDCFCE7)),
                          right: BorderSide(color: Color(0xFFDCFCE7)),
                          bottom: BorderSide(color: Color(0xFFDCFCE7)),
                        ),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.tips_and_updates_outlined, color: AppColors.success, size: 18),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              rec,
                              style: const TextStyle(
                                fontSize: 13,
                                color: Color(0xFF14532D),
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),

              const SizedBox(height: 32),

              // Bottom Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.primary,
                        side: const BorderSide(color: AppColors.primary),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      onPressed: () {
                        Navigator.popUntil(context, (route) => route.isFirst);
                      },
                      child: const Text('Beranda', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      onPressed: () {
                        // Pop back to UploadScreen
                        Navigator.pop(context);
                      },
                      icon: const Icon(Icons.replay),
                      label: const Text(
                        'Perbaiki & Foto Ulang',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
