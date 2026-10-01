import 'package:flutter_test/flutter_test.dart';
import 'package:vokasight_mobile/models/module_model.dart';
import 'package:vokasight_mobile/models/inspection_result_model.dart';
import 'package:vokasight_mobile/models/history_item_model.dart';
import 'package:vokasight_mobile/models/task_model.dart';

void main() {
  group('VokaSight Mobile Unit Tests', () {
    test('ModuleModel parsing test', () {
      final json = {
        'id': 'mod-soldering-basic',
        'name': 'Praktikum Soldering Dasar',
        'description': 'Latihan menyolder PCB.',
      };

      final model = ModuleModel.fromJson(json);
      expect(model.id, 'mod-soldering-basic');
      expect(model.name, 'Praktikum Soldering Dasar');
      expect(model.description, 'Latihan menyolder PCB.');
    });

    test('TaskModel parsing test', () {
      final json = {
        'task_id': 'task-123',
        'status': 'processing',
        'module_id': 'mod-soldering-basic',
        'student_id': '5324600006',
        'created_at': '2026-10-01T14:00:00Z',
        'message': 'Foto berhasil diunggah',
      };

      final model = TaskModel.fromJson(json);
      expect(model.taskId, 'task-123');
      expect(model.status, 'processing');
      expect(model.studentId, '5324600006');
    });

    test('InspectionResultModel parsing test', () {
      final json = {
        'task_id': 'task-123',
        'module_id': 'mod-soldering-basic',
        'status': 'completed',
        'score': 85.0,
        'lighting_warning': null,
        'detected_defects': [
          {
            'class_name': 'solder_bridge',
            'confidence': 0.92,
            'penalty': 25.0,
            'bbox': [100.0, 150.0, 200.0, 250.0],
          }
        ],
        'recommendations': [
          'Gunakan solder wick untuk membersihkan timah berlebih.'
        ],
        'processed_at': '2026-10-01T14:00:05Z',
      };

      final model = InspectionResultModel.fromJson(json);
      expect(model.taskId, 'task-123');
      expect(model.score, 85.0);
      expect(model.detectedDefects.length, 1);
      expect(model.detectedDefects.first.className, 'solder_bridge');
      expect(model.recommendations.length, 1);
    });

    test('HistoryItemModel serialization test', () {
      final result = InspectionResultModel(
        taskId: 'task-123',
        moduleId: 'mod-soldering-basic',
        status: 'completed',
        score: 90.0,
        detectedDefects: [],
        recommendations: ['Hasil baik.'],
        processedAt: '2026-10-01T14:00:05Z',
      );

      final history = HistoryItemModel(
        id: 'task-123',
        taskId: 'task-123',
        studentId: '5324600006',
        moduleId: 'mod-soldering-basic',
        moduleName: 'Praktikum Soldering Dasar',
        score: 90.0,
        defectCount: 0,
        imagePath: '/tmp/test.jpg',
        createdAt: DateTime.now(),
        result: result,
      );

      final json = history.toJson();
      final parsed = HistoryItemModel.fromJson(json);
      expect(parsed.taskId, 'task-123');
      expect(parsed.score, 90.0);
      expect(parsed.studentId, '5324600006');
    });
  });
}
