// Full Path: lib/features/valuation_engine/presentation/widgets/repair_component_tile.dart
// Purpose: One Repair Component's card - name + a radio group of its
//   RepairOptions (OK/PARTIAL/FULL), plus an implicit "no selection" state.
import 'package:flutter/material.dart';

import '../../data/models/repair_component_dto.dart';

class RepairComponentTile extends StatelessWidget {
  const RepairComponentTile({
    super.key,
    required this.component,
    required this.selectedOptionId,
    required this.onOptionSelected,
  });

  final RepairComponentDto component;
  final String? selectedOptionId;
  final ValueChanged<String?> onOptionSelected;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(component.name, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 4),
            RadioGroup<String>(
              groupValue: selectedOptionId,
              onChanged: onOptionSelected,
              child: Column(
                children: [
                  for (final option in component.options)
                    RadioListTile<String>(
                      key: Key('repair_option_${option.id}'),
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: Text('${option.optionName} (-${option.deductionAmount})'),
                      value: option.id,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
