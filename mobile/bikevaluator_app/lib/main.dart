// Full Path: lib/main.dart
// Purpose: App entry point - Dealer journey starts at the Vehicle Selector
//   screen. No login screen: FS-003 (Authentication) has no specification
//   or implementation anywhere in the repository (EP-002 Architecture
//   Observation #3), so the app starts pre-authenticated.
import 'package:flutter/material.dart';

import 'features/vehicle_master/presentation/screens/vehicle_selector_screen.dart';

void main() {
  runApp(const BikEvaluatorApp());
}

class BikEvaluatorApp extends StatelessWidget {
  const BikEvaluatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BikEvaluator',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple)),
      home: const VehicleSelectorScreen(),
    );
  }
}
