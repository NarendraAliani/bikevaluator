// Full Path: lib/features/valuation_engine/data/models/repair_component_dto.dart
// Related Documents: ISP-002 §2.1, API-001
import 'repair_option_dto.dart';

class RepairComponentDto {
  RepairComponentDto({
    required this.id,
    required this.name,
    required this.options,
  });

  final String id;
  final String name;
  final List<RepairOptionDto> options;

  factory RepairComponentDto.fromJson(Map<String, dynamic> json) => RepairComponentDto(
        id: json['id'] as String,
        name: json['name'] as String,
        options: (json['options'] as List)
            .map((o) => RepairOptionDto.fromJson(o as Map<String, dynamic>))
            .toList(),
      );
}
