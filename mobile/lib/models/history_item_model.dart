import 'inspection_result_model.dart';

class HistoryItemModel {
  final String id;
  final String taskId;
  final String studentId;
  final String moduleId;
  final String moduleName;
  final double score;
  final int defectCount;
  final String? imagePath;
  final DateTime createdAt;
  final InspectionResultModel result;

  HistoryItemModel({
    required this.id,
    required this.taskId,
    required this.studentId,
    required this.moduleId,
    required this.moduleName,
    required this.score,
    required this.defectCount,
    this.imagePath,
    required this.createdAt,
    required this.result,
  });

  factory HistoryItemModel.fromJson(Map<String, dynamic> json) {
    return HistoryItemModel(
      id: json['id']?.toString() ?? '',
      taskId: json['task_id']?.toString() ?? '',
      studentId: json['student_id']?.toString() ?? '-',
      moduleId: json['module_id']?.toString() ?? '',
      moduleName: json['module_name']?.toString() ?? '',
      score: double.tryParse(json['score']?.toString() ?? '0') ?? 0.0,
      defectCount: int.tryParse(json['defect_count']?.toString() ?? '0') ?? 0,
      imagePath: json['image_path']?.toString(),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
      result: InspectionResultModel.fromJson(
        Map<String, dynamic>.from(json['result'] ?? {}),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'task_id': taskId,
      'student_id': studentId,
      'module_id': moduleId,
      'module_name': moduleName,
      'score': score,
      'defect_count': defectCount,
      'image_path': imagePath,
      'created_at': createdAt.toIso8601String(),
      'result': result.toJson(),
    };
  }
}
