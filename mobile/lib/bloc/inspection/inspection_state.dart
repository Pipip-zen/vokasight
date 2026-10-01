import '../../models/inspection_result_model.dart';

abstract class InspectionState {}

class InspectionInitial extends InspectionState {}

class InspectionUploading extends InspectionState {
  final String message;
  InspectionUploading({this.message = 'Mengunggah foto PCB...'});
}

class InspectionPolling extends InspectionState {
  final String taskId;
  final int attempt;
  final String statusMessage;

  InspectionPolling({
    required this.taskId,
    required this.attempt,
    this.statusMessage = 'Memindai sambungan solder & menganalisis cacat...',
  });
}

class InspectionSuccess extends InspectionState {
  final InspectionResultModel result;
  final String? localImagePath;

  InspectionSuccess({
    required this.result,
    this.localImagePath,
  });
}

class InspectionFailure extends InspectionState {
  final String errorMessage;
  InspectionFailure(this.errorMessage);
}
