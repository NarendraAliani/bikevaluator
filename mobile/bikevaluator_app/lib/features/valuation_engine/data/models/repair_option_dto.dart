// Full Path: lib/features/valuation_engine/data/models/repair_option_dto.dart
// Related Documents: ISP-002 §2.1, API-001
class RepairOptionDto {
  RepairOptionDto({
    required this.id,
    required this.optionName,
    required this.deductionAmount,
  });

  final String id;
  final String optionName;
  final String deductionAmount;

  factory RepairOptionDto.fromJson(Map<String, dynamic> json) => RepairOptionDto(
        id: json['id'] as String,
        optionName: json['optionName'] as String,
        deductionAmount: json['deductionAmount'] as String,
      );
}
