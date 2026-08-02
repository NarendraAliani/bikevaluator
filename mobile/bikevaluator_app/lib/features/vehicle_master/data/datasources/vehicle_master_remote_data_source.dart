// Full Path: lib/features/vehicle_master/data/datasources/vehicle_master_remote_data_source.dart
// Purpose: HTTP calls for the Vehicle Selector step of the Dealer journey -
//   thin transport only, no business logic (mirrors backend view layer's role).
// Related Documents: API-001, ISP-001, EP-002
import '../../../../core/api_client.dart';
import '../models/brand_dto.dart';
import '../models/configuration_dto.dart';
import '../models/model_dto.dart';
import '../models/variant_dto.dart';

class VehicleMasterRemoteDataSource {
  VehicleMasterRemoteDataSource(this._client);

  final ApiClient _client;

  Future<List<BrandDto>> getBrands() async {
    final data = await _client.get('/vehicles/brands');
    return (data['brands'] as List)
        .map((json) => BrandDto.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<List<ModelDto>> getModels(String brandId) async {
    final data = await _client.get('/vehicles/models', query: {'brand_id': brandId});
    return (data['models'] as List)
        .map((json) => ModelDto.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<List<VariantDto>> getVariants(String modelId) async {
    final data = await _client.get('/vehicles/variants', query: {'model_id': modelId});
    return (data['variants'] as List)
        .map((json) => VariantDto.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<ConfigurationDto> getConfiguration({
    required int year,
    required String brandId,
    required String modelId,
    required String variantId,
  }) async {
    final data = await _client.get('/vehicles/configuration', query: {
      'year': year.toString(),
      'brand_id': brandId,
      'model_id': modelId,
      'variant_id': variantId,
    });
    return ConfigurationDto.fromJson(data as Map<String, dynamic>);
  }
}
