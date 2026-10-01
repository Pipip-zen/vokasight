import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../core/constants/app_colors.dart';
import '../models/module_model.dart';
import '../bloc/inspection/inspection_cubit.dart';
import '../bloc/inspection/inspection_state.dart';
import 'result_screen.dart';

class ScanningScreen extends StatefulWidget {
  final File imageFile;
  final ModuleModel module;
  final String studentId;
  final String? roboflowKey;

  const ScanningScreen({
    super.key,
    required this.imageFile,
    required this.module,
    required this.studentId,
    this.roboflowKey,
  });

  @override
  State<ScanningScreen> createState() => _ScanningScreenState();
}

class _ScanningScreenState extends State<ScanningScreen> {
  @override
  void initState() {
    super.initState();
    // Jalankan pipeline inspeksi
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<InspectionCubit>().startInspection(
            imageFile: widget.imageFile,
            moduleId: widget.module.id,
            moduleName: widget.module.name,
            studentId: widget.studentId,
            roboflowKey: widget.roboflowKey,
          );
    });
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: true,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) {
          context.read<InspectionCubit>().cancelInspection();
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          title: const Text(
            'Analisis AI Berjalan',
            style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary),
          ),
          backgroundColor: Colors.white,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.close, color: AppColors.textPrimary),
            onPressed: () {
              context.read<InspectionCubit>().cancelInspection();
              Navigator.pop(context);
            },
          ),
        ),
        body: SafeArea(
          child: BlocConsumer<InspectionCubit, InspectionState>(
            listener: (context, state) {
              if (state is InspectionSuccess) {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ResultScreen(
                      result: state.result,
                      module: widget.module,
                      studentId: widget.studentId,
                      localImagePath: state.localImagePath ?? widget.imageFile.path,
                    ),
                  ),
                );
              }
            },
            builder: (context, state) {
              if (state is InspectionFailure) {
                return _buildFailureView(state.errorMessage);
              }

              String statusText = 'Menginisialisasi analisis AI...';
              int attempt = 1;

              if (state is InspectionUploading) {
                statusText = state.message;
              } else if (state is InspectionPolling) {
                statusText = state.statusMessage;
                attempt = state.attempt;
              }

              return _buildScanningAnimation(statusText, attempt, state);
            },
          ),
        ),
      ),
    );
  }

  Widget _buildScanningAnimation(String statusText, int attempt, InspectionState state) {

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Pulse Circle Animation
          Stack(
            alignment: Alignment.center,
            children: [
              const SpinKitPulse(
                color: AppColors.primaryLight,
                size: 160.0,
              ),
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.memory,
                  size: 45,
                  color: Colors.white,
                ),
              ),
            ],
          ),

          const SizedBox(height: 36),

          const Text(
            'Sedang Memeriksa PCB',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),

          const SizedBox(height: 8),

          Text(
            statusText,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
          ),

          const SizedBox(height: 24),

          // Steps Progress Box
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Column(
              children: [
                _buildPipelineStep(
                  '1. Upload Citra PCB',
                  state is! InspectionUploading,
                  isCurrent: state is InspectionUploading,
                ),
                const Divider(height: 16),
                _buildPipelineStep(
                  '2. OpenCV CLAHE & Glare Filter',
                  attempt > 1,
                  isCurrent: attempt == 1 && state is InspectionPolling,
                ),
                const Divider(height: 16),
                _buildPipelineStep(
                  '3. AI YOLOv8 Defect Detection',
                  attempt > 2,
                  isCurrent: attempt >= 2 && state is InspectionPolling,
                ),
                const Divider(height: 16),
                _buildPipelineStep(
                  '4. Kalkulasi Skor & Rekomendasi',
                  false,
                  isCurrent: false,
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          OutlinedButton(
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.error,
              side: const BorderSide(color: AppColors.error),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            onPressed: () {
              context.read<InspectionCubit>().cancelInspection();
              Navigator.pop(context);
            },
            child: const Text('Batalkan Pemeriksaan'),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineStep(String label, bool isDone, {bool isCurrent = false}) {
    return Row(
      children: [
        if (isDone)
          const Icon(Icons.check_circle, color: AppColors.success, size: 18)
        else if (isCurrent)
          const SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
          )
        else
          const Icon(Icons.radio_button_unchecked, color: AppColors.textMuted, size: 18),
        const SizedBox(width: 10),
        Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
            color: isCurrent
                ? AppColors.primary
                : isDone
                    ? AppColors.textPrimary
                    : AppColors.textMuted,
          ),
        ),
      ],
    );
  }

  Widget _buildFailureView(String errorMessage) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.error.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.error_outline, size: 50, color: AppColors.error),
            ),
            const SizedBox(height: 16),
            const Text(
              'Pemeriksaan Gagal',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              errorMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Kembali'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () {
                    context.read<InspectionCubit>().startInspection(
                          imageFile: widget.imageFile,
                          moduleId: widget.module.id,
                          moduleName: widget.module.name,
                          studentId: widget.studentId,
                          roboflowKey: widget.roboflowKey,
                        );
                  },
                  child: const Text('Coba Lagi'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
