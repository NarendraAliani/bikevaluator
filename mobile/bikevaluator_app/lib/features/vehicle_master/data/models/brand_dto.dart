// Full Path: lib/features/vehicle_master/data/models/brand_dto.dart
// Related Documents: ISP-001 §2.4 BrandDto, API-001
class BrandDto {
  BrandDto({required this.id, required this.brandName});

  final String id;
  final String brandName;

  factory BrandDto.fromJson(Map<String, dynamic> json) =>
      BrandDto(id: json['id'] as String, brandName: json['brandName'] as String);
}
