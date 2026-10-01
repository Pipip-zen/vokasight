import 'dart:io';
import 'dart:math' as math;
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

  void _openFullscreenViewer(BuildContext context, {int? selectedIndex}) {
    if (localImagePath == null || !File(localImagePath!).existsSync()) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => FullscreenInspectionViewer(
          imagePath: localImagePath!,
          defects: result.detectedDefects,
          initialIndex: selectedIndex,
        ),
      ),
    );
  }

  Widget _buildRecommendationStep(int stepNumber, String text) {
    String title = 'Langkah $stepNumber: Tindakan Perbaikan';
    final lower = text.toLowerCase();
    if (lower.contains('short') || lower.contains('hubungan singkat')) {
      title = 'Langkah $stepNumber: Bersihkan Hubungan Singkat (Short Circuit)';
    } else if (lower.contains('kerusakan fisik') || lower.contains('damg') || lower.contains('jumper')) {
      title = 'Langkah $stepNumber: Pemeriksaan Kontinuitas Jalur PCB';
    } else if (lower.contains('miss welding') || lower.contains('tidak tersambung') || lower.contains('dry joint')) {
      title = 'Langkah $stepNumber: Pemanasan Ulang Titik Solder (Reflow)';
    } else if (lower.contains('spillover') || lower.contains('meluber')) {
      title = 'Langkah $stepNumber: Rapikan Luberan Timah Solder';
    } else if (lower.contains('lack of part') || lower.contains('belum terpasang') || lower.contains('komponen hilang')) {
      title = 'Langkah $stepNumber: Pasang Komponen yang Kurang';
    } else if (lower.contains('slug') || lower.contains('gumpalan') || lower.contains('residu') || lower.contains('alkohol')) {
      title = 'Langkah $stepNumber: Pembersihan Residu Timah & Papan';
    } else if (lower.contains('void') || lower.contains('rongga')) {
      title = 'Langkah $stepNumber: Pengisian Ulang Rongga Solder';
    } else if (lower.contains('cold joint') || lower.contains('dingin')) {
      title = 'Langkah $stepNumber: Perbaiki Sambungan Solder Dingin';
    } else if (lower.contains('perhatian') || lower.contains('warning')) {
      title = 'Perhatian Khusus / Evaluasi';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder, width: 1.2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.primary, width: 1.5),
                ),
                alignment: Alignment.center,
                child: Text(
                  '$stepNumber',
                  style: const TextStyle(
                    color: AppColors.primary,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 13.5,
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Padding(
            padding: const EdgeInsets.only(left: 38),
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF334155),
                height: 1.45,
              ),
            ),
          ),
        ],
      ),
    );
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

              // Inspected PCB Photo with AI Bounding Box Overlays
              if (localImagePath != null && File(localImagePath!).existsSync()) ...[
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Foto PCB yang Diperiksa',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    TextButton.icon(
                      style: TextButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: EdgeInsets.zero,
                      ),
                      onPressed: () => _openFullscreenViewer(context),
                      icon: const Icon(Icons.fullscreen, size: 18, color: AppColors.primary),
                      label: const Text('Fullscreen', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                _PcbAnnotatedPhotoView(
                  imagePath: localImagePath!,
                  defects: result.detectedDefects,
                  onFullscreenTap: () => _openFullscreenViewer(context),
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
                  children: result.detectedDefects.asMap().entries.map((entry) {
                    final idx = entry.key;
                    final defect = entry.value;
                    final isBridge = defect.className.toLowerCase().contains('bridge') ||
                        defect.className.toLowerCase().contains('short');

                    return InkWell(
                      onTap: () => _openFullscreenViewer(context, selectedIndex: idx),
                      borderRadius: BorderRadius.circular(10),
                      child: Container(
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
                                  Row(
                                    children: [
                                      Text(
                                        defect.className.replaceAll('_', ' ').toUpperCase(),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13.5,
                                          color: AppColors.textPrimary,
                                        ),
                                      ),
                                      const SizedBox(width: 6),
                                      const Icon(Icons.zoom_in, size: 14, color: AppColors.textMuted),
                                    ],
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
              const SizedBox(height: 10),

              if (result.recommendations.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
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
                  children: result.recommendations.asMap().entries.map((entry) {
                    final stepNumber = entry.key + 1;
                    final recText = entry.value;
                    return _buildRecommendationStep(stepNumber, recText);
                  }).toList(),
                ),

              const SizedBox(height: 28),

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

class _PcbAnnotatedPhotoView extends StatefulWidget {
  final String imagePath;
  final List<DefectItem> defects;
  final VoidCallback onFullscreenTap;

  const _PcbAnnotatedPhotoView({
    required this.imagePath,
    required this.defects,
    required this.onFullscreenTap,
  });

  @override
  State<_PcbAnnotatedPhotoView> createState() => _PcbAnnotatedPhotoViewState();
}

class _PcbAnnotatedPhotoViewState extends State<_PcbAnnotatedPhotoView> {
  Size? _imageSize;

  @override
  void initState() {
    super.initState();
    _resolveImageDimensions();
  }

  void _resolveImageDimensions() {
    final file = File(widget.imagePath);
    if (!file.existsSync()) return;

    final image = FileImage(file);
    image.resolve(const ImageConfiguration()).addListener(
      ImageStreamListener((ImageInfo info, bool _) {
        if (mounted) {
          setState(() {
            _imageSize = Size(
              info.image.width.toDouble(),
              info.image.height.toDouble(),
            );
          });
        }
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onFullscreenTap,
      child: Container(
        width: double.infinity,
        height: 220,
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.cardBorder),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.08),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          children: [
            Positioned.fill(
              child: Center(
                child: Image.file(
                  File(widget.imagePath),
                  fit: BoxFit.contain,
                  width: double.infinity,
                  height: double.infinity,
                ),
              ),
            ),
            if (_imageSize != null && widget.defects.isNotEmpty)
              Positioned.fill(
                child: CustomPaint(
                  painter: _DefectBoundingBoxPainter(
                    defects: widget.defects,
                    imageSize: _imageSize!,
                  ),
                ),
              ),
            Positioned(
              right: 10,
              bottom: 10,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.72),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.zoom_in, color: Colors.white, size: 15),
                    SizedBox(width: 4),
                    Text(
                      'Ketuk untuk Zoom',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (widget.defects.isNotEmpty)
              Positioned(
                left: 10,
                top: 10,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.error.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${widget.defects.length} Cacat Terdeteksi',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10.5,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class FullscreenInspectionViewer extends StatefulWidget {
  final String imagePath;
  final List<DefectItem> defects;
  final int? initialIndex;

  const FullscreenInspectionViewer({
    super.key,
    required this.imagePath,
    required this.defects,
    this.initialIndex,
  });

  @override
  State<FullscreenInspectionViewer> createState() => _FullscreenInspectionViewerState();
}

class _FullscreenInspectionViewerState extends State<FullscreenInspectionViewer> {
  Size? _imageSize;
  bool _showBoxes = true;
  int? _selectedIndex;
  final TransformationController _transController = TransformationController();

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
    _resolveImageDimensions();
  }

  void _resolveImageDimensions() {
    final file = File(widget.imagePath);
    if (!file.existsSync()) return;

    final image = FileImage(file);
    image.resolve(const ImageConfiguration()).addListener(
      ImageStreamListener((ImageInfo info, bool _) {
        if (mounted) {
          setState(() {
            _imageSize = Size(
              info.image.width.toDouble(),
              info.image.height.toDouble(),
            );
          });
        }
      }),
    );
  }

  @override
  void dispose() {
    _transController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Inspeksi Detail PCB',
              style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(
              '${widget.defects.length} Cacat • Cubit untuk Zoom Detail',
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            tooltip: 'Reset Skala Zoom',
            onPressed: () {
              _transController.value = Matrix4.identity();
            },
          ),
          TextButton.icon(
            style: TextButton.styleFrom(
              foregroundColor: Colors.white,
              backgroundColor: _showBoxes ? const Color(0xFF334155) : const Color(0xFF1E293B),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () {
              setState(() {
                _showBoxes = !_showBoxes;
              });
            },
            icon: Icon(
              _showBoxes ? Icons.visibility : Icons.visibility_off,
              size: 16,
              color: _showBoxes ? const Color(0xFF38BDF8) : Colors.white70,
            ),
            label: Text(
              _showBoxes ? 'Box ON' : 'Box OFF',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: _showBoxes ? const Color(0xFF38BDF8) : Colors.white70,
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: InteractiveViewer(
              transformationController: _transController,
              minScale: 0.5,
              maxScale: 6.0,
              boundaryMargin: const EdgeInsets.all(40),
              child: Center(
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    return Stack(
                      fit: StackFit.expand,
                      children: [
                        Center(
                          child: Image.file(
                            File(widget.imagePath),
                            fit: BoxFit.contain,
                          ),
                        ),
                        if (_showBoxes && _imageSize != null && widget.defects.isNotEmpty)
                          Positioned.fill(
                            child: CustomPaint(
                              painter: _DefectBoundingBoxPainter(
                                defects: widget.defects,
                                imageSize: _imageSize!,
                                highlightedIndex: _selectedIndex,
                              ),
                            ),
                          ),
                      ],
                    );
                  },
                ),
              ),
            ),
          ),
          if (widget.defects.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              decoration: const BoxDecoration(
                color: Color(0xFF1E293B),
                border: Border(top: BorderSide(color: Color(0xFF334155), width: 1)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'PILIH DEFECT UNTUK SOROT:',
                    style: TextStyle(
                      color: Color(0xFF94A3B8),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              _selectedIndex = null;
                            });
                          },
                          child: Container(
                            margin: const EdgeInsets.only(right: 8),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: _selectedIndex == null ? AppColors.primaryLight : const Color(0xFF334155),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Text(
                              'Semua Box',
                              style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ),
                        ...widget.defects.asMap().entries.map((entry) {
                          final idx = entry.key;
                          final defect = entry.value;
                          final isSel = _selectedIndex == idx;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                _selectedIndex = idx;
                              });
                            },
                            child: Container(
                              margin: const EdgeInsets.only(right: 8),
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: isSel ? const Color(0xFFDC2626) : const Color(0xFF334155),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: isSel ? Colors.white : Colors.transparent,
                                  width: 1,
                                ),
                              ),
                              child: Row(
                                children: [
                                  Text(
                                    '#${idx + 1} ${defect.className.replaceAll('_', ' ').toUpperCase()}',
                                    style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    '(${(defect.confidence * 100).toStringAsFixed(0)}%)',
                                    style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 11),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _DefectBoundingBoxPainter extends CustomPainter {
  final List<DefectItem> defects;
  final Size imageSize;
  final int? highlightedIndex;

  _DefectBoundingBoxPainter({
    required this.defects,
    required this.imageSize,
    this.highlightedIndex,
  });

  Color _getDefectColor(String className) {
    final lower = className.toLowerCase();
    if (lower.contains('short') || lower.contains('bridge') || lower.contains('damg') || lower.contains('burn')) {
      return const Color(0xFFEF4444); // Red
    }
    if (lower.contains('miss') || lower.contains('void') || lower.contains('cold') || lower.contains('weld')) {
      return const Color(0xFFF59E0B); // Amber / Orange
    }
    if (lower.contains('spill') || lower.contains('slug') || lower.contains('redundant')) {
      return const Color(0xFF06B6D4); // Cyan
    }
    return const Color(0xFF8B5CF6); // Violet
  }

  @override
  void paint(Canvas canvas, Size size) {
    if (imageSize.width <= 0 || imageSize.height <= 0) return;

    final double scale = math.min(
      size.width / imageSize.width,
      size.height / imageSize.height,
    );
    final double renderedWidth = imageSize.width * scale;
    final double renderedHeight = imageSize.height * scale;
    final double offsetX = (size.width - renderedWidth) / 2.0;
    final double offsetY = (size.height - renderedHeight) / 2.0;

    for (int i = 0; i < defects.length; i++) {
      final defect = defects[i];
      if (defect.bbox.length < 4) continue;

      double x1 = defect.bbox[0];
      double y1 = defect.bbox[1];
      double x2 = defect.bbox[2];
      double y2 = defect.bbox[3];

      // Handle normalized coordinates if values are <= 1.0
      if (x1 <= 1.0 && x2 <= 1.0 && y1 <= 1.0 && y2 <= 1.0 && (x2 > 0 || y2 > 0)) {
        x1 *= imageSize.width;
        y1 *= imageSize.height;
        x2 *= imageSize.width;
        y2 *= imageSize.height;
      }

      final double left = offsetX + (x1 * scale);
      final double top = offsetY + (y1 * scale);
      final double width = math.max(12.0, (x2 - x1) * scale);
      final double height = math.max(12.0, (y2 - y1) * scale);

      final bool isHighlighted = (highlightedIndex == null || highlightedIndex == i);
      final Color baseColor = _getDefectColor(defect.className);
      final Color color = isHighlighted ? baseColor : baseColor.withValues(alpha: 0.35);

      final rect = Rect.fromLTWH(left, top, width, height);
      final rrect = RRect.fromRectAndRadius(rect, const Radius.circular(4));

      // 1. Semi-transparent fill highlight
      final fillPaint = Paint()
        ..color = color.withValues(alpha: isHighlighted ? 0.16 : 0.05)
        ..style = PaintingStyle.fill;
      canvas.drawRRect(rrect, fillPaint);

      // 2. Stroke outline
      final strokePaint = Paint()
        ..color = color
        ..strokeWidth = isHighlighted ? 2.5 : 1.5
        ..style = PaintingStyle.stroke;
      canvas.drawRRect(rrect, strokePaint);

      // 3. Label tag
      final label = '${defect.className.replaceAll('_', ' ').toUpperCase()} ${(defect.confidence * 100).toStringAsFixed(0)}%';
      final textSpan = TextSpan(
        text: label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 9.5,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.2,
        ),
      );
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();

      const double labelPadX = 6.0;
      const double labelPadY = 2.0;
      final double labelW = textPainter.width + (labelPadX * 2);
      final double labelH = textPainter.height + (labelPadY * 2);

      double labelTop = top - labelH - 2;
      if (labelTop < offsetY) {
        labelTop = top + 2;
      }
      double labelLeft = left;
      if (labelLeft + labelW > offsetX + renderedWidth) {
        labelLeft = math.max(offsetX, offsetX + renderedWidth - labelW);
      }

      final labelRect = RRect.fromRectAndRadius(
        Rect.fromLTWH(labelLeft, labelTop, labelW, labelH),
        const Radius.circular(4),
      );
      final labelBgPaint = Paint()
        ..color = color.withValues(alpha: 0.95)
        ..style = PaintingStyle.fill;
      canvas.drawRRect(labelRect, labelBgPaint);

      textPainter.paint(canvas, Offset(labelLeft + labelPadX, labelTop + labelPadY));
    }
  }

  @override
  bool shouldRepaint(covariant _DefectBoundingBoxPainter oldDelegate) {
    return oldDelegate.defects != defects ||
        oldDelegate.imageSize != imageSize ||
        oldDelegate.highlightedIndex != highlightedIndex;
  }
}
