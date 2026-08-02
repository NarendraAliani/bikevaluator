// Full Path: lib/features/valuation_engine/data/models/valuation_result_dto.dart
// Related Documents: ISP-002 §2.2 ValuationResultDto, API-001, NS-001 §7 (camelCase JSON)
class ValuationResultDto {
  ValuationResultDto({
    required this.recommendedPrice,
    required this.roundedPrice,
    required this.label,
  });

  final String recommendedPrice;
  final String roundedPrice;
  final String label;

  factory ValuationResultDto.fromJson(Map<String, dynamic> json) => ValuationResultDto(
        recommendedPrice: json['recommendedPrice'] as String,
        roundedPrice: json['roundedPrice'] as String,
        label: json['label'] as String,
      );
}
