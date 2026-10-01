class TaskModel {
  final String taskId;
  final String status;
  final String moduleId;
  final String? studentId;
  final String createdAt;
  final String? message;

  TaskModel({
    required this.taskId,
    required this.status,
    required this.moduleId,
    this.studentId,
    required this.createdAt,
    this.message,
  });

  factory TaskModel.fromJson(Map<String, dynamic> json) {
    // Check if task is nested inside json['task'] (as in some responses) or flat
    final data = json.containsKey('task') && json['task'] is Map ? json['task'] : json;
    return TaskModel(
      taskId: data['task_id']?.toString() ?? '',
      status: data['status']?.toString() ?? 'processing',
      moduleId: data['module_id']?.toString() ?? '',
      studentId: data['student_id']?.toString(),
      createdAt: data['created_at']?.toString() ?? '',
      message: data['message']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'task_id': taskId,
      'status': status,
      'module_id': moduleId,
      if (studentId != null) 'student_id': studentId,
      'created_at': createdAt,
      if (message != null) 'message': message,
    };
  }
}
