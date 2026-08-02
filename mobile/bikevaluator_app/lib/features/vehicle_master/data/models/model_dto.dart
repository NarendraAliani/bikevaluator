// Full Path: lib/features/vehicle_master/data/models/model_dto.dart
// Related Documents: ISP-001 §2.4 ModelDto, API-001
class ModelDto {
  ModelDto({required this.id, required this.brandId, required this.modelName});

  final String id;
  final String brandId;
  final String modelName;

  factory ModelDto.fromJson(Map<String, dynamic> json) => ModelDto(
        id: json['id'] as String,
        brandId: json['brandId'] as String,
        modelName: json['modelName'] as String,
      );
}
