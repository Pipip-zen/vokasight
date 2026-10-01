import '../../models/module_model.dart';

abstract class ModuleState {}

class ModuleInitial extends ModuleState {}

class ModuleLoading extends ModuleState {}

class ModuleLoaded extends ModuleState {
  final List<ModuleModel> modules;
  final ModuleModel? selectedModule;

  ModuleLoaded({
    required this.modules,
    this.selectedModule,
  });

  ModuleLoaded copyWith({
    List<ModuleModel>? modules,
    ModuleModel? selectedModule,
  }) {
    return ModuleLoaded(
      modules: modules ?? this.modules,
      selectedModule: selectedModule ?? this.selectedModule,
    );
  }
}

class ModuleError extends ModuleState {
  final String message;
  final List<ModuleModel> fallbackModules;

  ModuleError(this.message, {this.fallbackModules = const []});
}
