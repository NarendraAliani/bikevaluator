// Full Path: lib/features/vehicle_master/presentation/controllers/vehicle_selector_controller.dart
// Purpose: Thin façade over VehicleMasterRemoteDataSource for the Vehicle
//   Selector screen. Plain class (not ChangeNotifier) - state management for
//   this build is plain StatefulWidget/setState (EP-002 Architecture
//   Observation #2), so this controller only fetches data; the screen's
//   State owns and mutates all UI state itself.
import '../../data/datasources/vehicle_master_remote_data_source.dart';
import '../../data/models/brand_dto.dart';
import '../../data/models/configuration_dto.dart';
import '../../data/models/model_dto.dart';
import '../../data/models/variant_dto.dart';

class VehicleSelectorController {
  VehicleSelectorController(this._dataSource);

  final VehicleMasterRemoteDataSource _dataSource;

  Future<List<BrandDto>> loadBrands() => _dataSource.getBrands();

  Future<List<ModelDto>> loadModels(String brandId) => _dataSource.getModels(brandId);

  Future<List<VariantDto>> loadVariants(String modelId) => _dataSource.getVariants(modelId);

  Future<ConfigurationDto> loadConfiguration({
    required int year,
    required String brandId,
    required String modelId,
    required String variantId,
  }) =>
      _dataSource.getConfiguration(
        year: year,
        brandId: brandId,
        modelId: modelId,
        variantId: variantId,
      );
}
