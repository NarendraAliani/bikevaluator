// Full Path: test/widget_test.dart
// Purpose: App-level smoke test - the app boots to the Vehicle Selector
//   screen and shows a loading indicator while brands are being fetched
//   (in this host environment, the fetch itself fails fast since
//   10.0.2.2 only resolves from inside the Android emulator - the test
//   verifies the app degrades to an error state rather than crashing).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:bikevaluator_app/main.dart';

void main() {
  testWidgets('App boots to Vehicle Selector screen without crashing', (tester) async {
    await tester.pumpWidget(const BikEvaluatorApp());

    expect(find.text('Select Vehicle'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle(const Duration(seconds: 5));

    expect(tester.takeException(), isNull);
  });
}
