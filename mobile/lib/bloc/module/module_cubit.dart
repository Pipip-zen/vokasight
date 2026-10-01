import 'package:flutter_bloc/flutter_bloc.dart';
import '../../models/module_model.dart';
import '../../services/api_service.dart';
import 'module_state.dart';

class ModuleCubit extends Cubit<ModuleState> {
  final ApiService _apiService;

  ModuleCubit({ApiService? apiService})
      : _apiService = apiService ?? ApiService(),
        super(ModuleInitial());

  // Default fallback modules jika server backend belum running atau offline di lab
  static final List<ModuleModel> defaultFallbackModules = [
    ModuleModel(
      id: 'mod-soldering-basic',
      name: 'Praktikum Soldering & Desoldering Dasar',
      description: 'Inspeksi kualitas sambungan solder pad, void, dan deteksi solder bridge pada board latihan.',
    ),
    ModuleModel(
      id: 'mod-pcb-defect-general',
      name: 'Praktikum Inspeksi Cacat PCB General (PCB Defect Detection)',
      description: 'Pemeriksaan cacat fisik PCB secara menyeluruh (missing component, short/open circuit, spur, pin hole, dan sisa tembaga).',
    ),
  ];

  Future<void> fetchModules() async {
    emit(ModuleLoading());
    try {
      final modules = await _apiService.getModules();
      if (modules.isNotEmpty) {
        emit(ModuleLoaded(
          modules: modules,
          selectedModule: modules.first,
        ));
      } else {
        // Fallback to defaults if list empty
        emit(ModuleLoaded(
          modules: defaultFallbackModules,
          selectedModule: defaultFallbackModules.first,
        ));
      }
    } catch (e) {
      // Use fallback modules with error notification
      emit(ModuleLoaded(
        modules: defaultFallbackModules,
        selectedModule: defaultFallbackModules.first,
      ));
    }
  }

  void selectModule(ModuleModel module) {
    if (state is ModuleLoaded) {
      final current = state as ModuleLoaded;
      emit(current.copyWith(selectedModule: module));
    }
  }
}
