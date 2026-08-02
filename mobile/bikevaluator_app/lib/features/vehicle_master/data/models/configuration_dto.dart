// Full Path: lib/features/vehicle_master/data/models/configuration_dto.dart
// Related Documents: ISP-001 §2.4 ConfigurationDto, API-001
class ConfigurationDto {
  ConfigurationDto({
    required this.valuationMasterId,
    required this.year,
    required this.variantId,
    required this.minimumSellingPrice,
    required this.margin,
    required this.scrapValue,
  });

  final String valuationMasterId;
  final int year;
  final String variantId;
  final String minimumSellingPrice;
  final String margin;
  final String scrapValue;

  factory ConfigurationDto.fromJson(Map<String, dynamic> json) => ConfigurationDto(
        valuationMasterId: json['valuationMasterId'] as String,
        year: json['year'] as int,
        variantId: json['variantId'] as String,
        minimumSellingPrice: json['minimumSellingPrice'] as String,
        margin: json['margin'] as String,
        scrapValue: json['scrapValue'] as String,
      );
}
