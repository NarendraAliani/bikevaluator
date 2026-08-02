// Full Path: lib/features/valuation_engine/presentation/screens/result_screen.dart
// Purpose: Journey step 3 - display the Purchase Price recommendation and
//   its Good/Excellent/Average/Scrap label (BR-0001-BR-0003, BR-0009).
// Related Documents: FS-002, ISP-002 §2.2, EP-002 §4
import 'package:flutter/material.dart';

import '../../data/models/valuation_result_dto.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key, required this.result});

  final ValuationResultDto result;

  Color _labelColor(BuildContext context) {
    switch (result.label) {
      case 'EXCELLENT':
        return Colors.green;
      case 'GOOD':
        return Colors.lightGreen;
      case 'AVERAGE':
        return Colors.orange;
      case 'SCRAP':
        return Colors.red;
      default:
        return Theme.of(context).colorScheme.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Valuation Result')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Recommended Purchase Price', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Text(
                '₹${result.roundedPrice}',
                key: const Key('rounded_price_text'),
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 24),
              Chip(
                key: const Key('recommendation_label_chip'),
                label: Text(result.label),
                backgroundColor: _labelColor(context).withValues(alpha: 0.15),
                labelStyle: TextStyle(color: _labelColor(context), fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
                child: const Text('Start New Valuation'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
