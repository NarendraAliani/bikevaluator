// Full Path: lib/core/api_exception.dart
// Module: bikevaluator_app / core
// Purpose: Typed exception carrying the backend's error code/message
//   (API-000 v1.1 error shape), so screens can branch on `code` (e.g. VAL003).
class ApiException implements Exception {
  ApiException({required this.code, required this.message});

  final String code;
  final String message;

  bool get isPricingUnavailable => code == 'VAL003' || code == 'E-PRICING-001';

  @override
  String toString() => 'ApiException($code: $message)';
}
