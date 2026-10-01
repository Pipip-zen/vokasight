class DefectItem {
  final String className;
  final double confidence;
  final double penalty;
  final List<double> bbox;

  DefectItem({
    required this.className,
    required this.confidence,
    required this.penalty,
    required this.bbox,
  });

  factory DefectItem.fromJson(Map<String, dynamic> json) {
    List<double> parsedBbox = [];
    if (json['bbox'] is List) {
      parsedBbox = (json['bbox'] as List)
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList();
    }

    return DefectItem(
      className: json['class_name']?.toString() ??
          json['defect_type']?.toString() ??
          'Defect',
      confidence: double.tryParse(json['confidence']?.toString() ?? '0') ?? 0.0,
      penalty: double.tryParse(json['penalty']?.toString() ?? '15') ?? 15.0,
      bbox: parsedBbox,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'class_name': className,
      'confidence': confidence,
      'penalty': penalty,
      'bbox': bbox,
    };
  }
}

class InspectionResultModel {
  final String taskId;
  final String moduleId;
  final String status;
  final double score;
  final String? studentId;
  final String? lightingWarning;
  final List<DefectItem> detectedDefects;
  final List<String> recommendations;
  final String? recommendationsText;
  final String processedAt;

  InspectionResultModel({
    required this.taskId,
    required this.moduleId,
    required this.status,
    required this.score,
    this.studentId,
    this.lightingWarning,
    required this.detectedDefects,
    required this.recommendations,
    this.recommendationsText,
    required this.processedAt,
  });

  factory InspectionResultModel.fromJson(Map<String, dynamic> json) {
    // If the response wraps under 'result', extract it
    Map<String, dynamic> data = json;
    if (json.containsKey('result') && json['result'] is Map) {
      data = Map<String, dynamic>.from(json['result']);
      // Fallback taskId if not in result
      if (!data.containsKey('task_id') && json.containsKey('task')) {
        data['task_id'] = json['task']?['task_id'];
        data['module_id'] = json['task']?['module_id'];
        data['student_id'] = json['task']?['student_id'];
      }
    }

    List<DefectItem> defects = [];
    if (data['detected_defects'] is List) {
      defects = (data['detected_defects'] as List)
          .map((e) => DefectItem.fromJson(Map<String, dynamic>.from(e)))
          .toList();
    }

    List<String> recs = [];
    if (data['recommendations'] is List) {
      recs = (data['recommendations'] as List)
          .map((e) => e.toString())
          .toList();
    } else if (data['recommendations_text'] is String) {
      recs = [data['recommendations_text'].toString()];
    }

    return InspectionResultModel(
      taskId: data['task_id']?.toString() ?? '',
      moduleId: data['module_id']?.toString() ?? '',
      status: data['status']?.toString() ?? 'completed',
      score: double.tryParse(data['score']?.toString() ?? '0') ?? 0.0,
      studentId: data['student_id']?.toString(),
      lightingWarning: data['lighting_warning']?.toString(),
      detectedDefects: defects,
      recommendations: recs,
      recommendationsText: data['recommendations_text']?.toString(),
      processedAt: data['processed_at']?.toString() ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'task_id': taskId,
      'module_id': moduleId,
      'status': status,
      'score': score,
      if (studentId != null) 'student_id': studentId,
      if (lightingWarning != null) 'lighting_warning': lightingWarning,
      'detected_defects': detectedDefects.map((e) => e.toJson()).toList(),
      'recommendations': recommendations,
      if (recommendationsText != null) 'recommendations_text': recommendationsText,
      'processed_at': processedAt,
    };
  }
}
