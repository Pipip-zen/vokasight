import '../../models/history_item_model.dart';

abstract class HistoryState {}

class HistoryInitial extends HistoryState {}

class HistoryLoading extends HistoryState {}

class HistoryLoaded extends HistoryState {
  final List<HistoryItemModel> items;
  HistoryLoaded(this.items);
}

class HistoryError extends HistoryState {
  final String message;
  HistoryError(this.message);
}
