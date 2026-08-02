// Full Path: lib/features/vehicle_master/data/models/variant_dto.dart
// Related Documents: ISP-001 §2.4 VariantDto, API-001
class VariantDto {
  VariantDto({required this.id, required this.modelId, required this.variantName});

  final String id;
  final String modelId;
  final String variantName;

  factory VariantDto.fromJson(Map<String, dynamic> json) => VariantDto(
        id: json['id'] as String,
        modelId: json['modelId'] as String,
        variantName: json['variantName'] as String,
      );
}
