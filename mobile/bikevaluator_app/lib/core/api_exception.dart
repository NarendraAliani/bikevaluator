// Full Path: lib/core/api_exception.dart
// Module: bikevaluator_app / core
// Purpose: Typed exception carrying the backend's error code/message
//   (API-000 v1.1 error shape) plus a coarse category, so screens can
//   show a distinct, user-friendly message per failure kind instead of
//   one generic string (IMP-003B Task 7).
enum ApiErrorCategory {
  /// Could not reach the server at all (DNS/connection refused/etc.).
  network,

  /// The request was sent but took too long to complete.
  timeout,

  /// The server responded but with a 5xx-style failure it couldn't recover from.
  server,

  /// The server rejected the request as invalid (4xx) - a fixable input problem.
  validation,

  /// Anything that doesn't cleanly fall into the above.
  unknown,
}

class ApiException implements Exception {
  ApiException({
    required this.code,
    required this.message,
    this.category = ApiErrorCategory.unknown,
  });

  final String code;
  final String message;
  final ApiErrorCategory category;

  bool get isPricingUnavailable => code == 'VAL003' || code == 'E-PRICING-001';

  /// A short, user-facing message appropriate for the failure category -
  /// screens should prefer this over raw [message] for end users.
  String get userFriendlyMessage {
    switch (category) {
      case ApiErrorCategory.network:
        return 'No connection to the server. Check your network and try again.';
      case ApiErrorCategory.timeout:
        return 'The request took too long. Check your connection and try again.';
      case ApiErrorCategory.server:
        return 'Something went wrong on our side. Please try again shortly.';
      case ApiErrorCategory.validation:
        return message;
      case ApiErrorCategory.unknown:
        return message;
    }
  }

  @override
  String toString() => 'ApiException($code: $message, category: $category)';
}
