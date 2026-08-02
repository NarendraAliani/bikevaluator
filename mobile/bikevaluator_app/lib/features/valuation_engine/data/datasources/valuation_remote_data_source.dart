// Full Path: lib/features/valuation_engine/data/datasources/valuation_remote_data_source.dart
// Purpose: HTTP calls for the Repair Assessment + Calculate steps of the
//   Dealer journey - thin transport only, no business logic.
// Related Documents: API-001, ISP-002, EP-002
import '../../../../core/api_client.dart';
import '../models/repair_component_dto.dart';
import '../models/valuation_result_dto.dart';

class ValuationRemoteDataSource {
  ValuationRemoteDataSource(this._client);

  final ApiClient _client;

  Future<List<RepairComponentDto>> getRepairComponents() async {
    final data = await _client.get('/repairs/components');
    return (data['components'] as List)
        .map((json) => RepairComponentDto.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// [repairAssessment] is a list of `{repairComponentId, repairOptionId}` maps.
  Future<ValuationResultDto> calculateValuation({
    required int year,
    required String variantId,
    required List<Map<String, String>> repairAssessment,
  }) async {
    final data = await _client.post('/valuation/calculate', {
      'year': year,
      'variantId': variantId,
      'repairAssessment': repairAssessment,
    });
    return ValuationResultDto.fromJson(data as Map<String, dynamic>);
  }
}
