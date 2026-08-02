// Full Path: test/features/valuation_engine/dto_test.dart
// Purpose: Unit tests for Valuation Engine DTO JSON parsing (camelCase
//   field mapping per NS-001 §7).
import 'package:bikevaluator_app/features/valuation_engine/data/models/repair_component_dto.dart';
import 'package:bikevaluator_app/features/valuation_engine/data/models/valuation_result_dto.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('RepairComponentDto.fromJson parses nested options', () {
    final component = RepairComponentDto.fromJson({
      'id': 'c1',
      'name': 'Engine',
      'options': [
        {'id': 'o1', 'optionName': 'PARTIAL', 'deductionAmount': '3000.00'},
      ],
    });
    expect(component.name, 'Engine');
    expect(component.options, hasLength(1));
    expect(component.options.first.optionName, 'PARTIAL');
  });

  test('ValuationResultDto.fromJson parses recommendedPrice/roundedPrice/label', () {
    final result = ValuationResultDto.fromJson({
      'recommendedPrice': '42000.00',
      'roundedPrice': '42000',
      'label': 'GOOD',
    });
    expect(result.recommendedPrice, '42000.00');
    expect(result.roundedPrice, '42000');
    expect(result.label, 'GOOD');
  });
}
