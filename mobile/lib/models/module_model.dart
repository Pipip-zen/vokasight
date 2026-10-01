class ModuleModel {
  final String id;
  final String name;
  final String description;

  ModuleModel({
    required this.id,
    required this.name,
    required this.description,
  });

  factory ModuleModel.fromJson(Map<String, dynamic> json) {
    return ModuleModel(
      id: json['id']?.toString() ?? json['module_id']?.toString() ?? '',
      name: json['name']?.toString() ?? json['module_name']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'module_id': id,
      'name': name,
      'module_name': name,
      'description': description,
    };
  }
}
