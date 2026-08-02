// Full Path: lib/features/valuation_engine/presentation/controllers/valuation_controller.dart
// Purpose: Thin façade over ValuationRemoteDataSource for the Repair
//   Assessment / Result screens. Plain class (not ChangeNotifier) - state
//   management for this build is plain StatefulWidget/setState
//   (EP-002 Architecture Observation #2).
import '../../data/datasources/valuation_remote_data_source.dart';
import '../../data/models/repair_component_dto.dart';
import '../../data/models/valuation_result_dto.dart';

class ValuationController {
  ValuationController(this._dataSource);

  final ValuationRemoteDataSource _dataSource;

  Future<List<RepairComponentDto>> loadRepairComponents() =>
      _dataSource.getRepairComponents();

  Future<ValuationResultDto> calculate({
    required int year,
    required String variantId,
    required List<Map<String, String>> repairAssessment,
  }) =>
      _dataSource.calculateValuation(
        year: year,
        variantId: variantId,
        repairAssessment: repairAssessment,
      );
}
