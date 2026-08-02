// Full Path: lib/core/api_client.dart
// Module: bikevaluator_app / core
// Purpose: Single HTTP client wrapper - base URL, actor headers,
//   response-envelope parsing (API-000 v1.1), request timeout, and
//   failure-category classification, shared by every feature.
// Related Documents: API-000 v1.1, API-001, EP-002 Architecture
//   Observation #3, IMP-003B Task 7 (timeout, centralized instance,
//   network/server/validation/timeout differentiation)
import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'api_exception.dart';

/// Android emulator reaches the host machine's `localhost` via the
/// special address `10.0.2.2`, not `127.0.0.1` (EP-002 §4 assumption).
const String kApiBaseUrl = 'http://10.0.2.2:8000/api/v1';

/// FS-003 (Authentication) does not exist anywhere in this codebase.
/// Per EP-002 Architecture Observation #3, the app starts pre-authenticated
/// and reuses the backend's existing `DummyActorProvider` header mechanism
/// (`X-Actor-Id`/`X-Actor-Role`) rather than inventing a login screen.
const String kDummyActorId = '11111111-1111-1111-1111-111111111111';
const String kDummyActorRole = 'dealer';

/// IMP-003B Task 7: no HTTP call may hang indefinitely - a slow/dead
/// connection must reach the same error/retry UI a refused connection
/// already did, instead of leaving a screen stuck on its loading spinner.
const Duration kRequestTimeout = Duration(seconds: 15);

class ApiClient {
  ApiClient({http.Client? client, Duration? timeout})
      : _client = client ?? http.Client(),
        _timeout = timeout ?? kRequestTimeout;

  final Duration _timeout;

  /// IMP-003B Task 7 ("centralize ApiClient creation"): one shared
  /// instance for the whole app, instead of every screen constructing
  /// its own. Screens should use this; tests keep constructing their
  /// own `ApiClient(client: MockClient(...))` for isolation.
  static final ApiClient instance = ApiClient();

  final http.Client _client;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'X-Actor-Id': kDummyActorId,
        'X-Actor-Role': kDummyActorRole,
      };

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final uri = Uri.parse('$kApiBaseUrl$path').replace(queryParameters: query);
    final response = await _send(() => _client.get(uri, headers: _headers));
    return _parseEnvelope(response);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body) async {
    final uri = Uri.parse('$kApiBaseUrl$path');
    final response = await _send(
      () => _client.post(uri, headers: _headers, body: jsonEncode(body)),
    );
    return _parseEnvelope(response);
  }

  Future<http.Response> _send(Future<http.Response> Function() request) async {
    try {
      return await request().timeout(_timeout);
    } on TimeoutException {
      throw ApiException(
        code: 'E-TIMEOUT-000',
        message: 'The request took too long to complete.',
        category: ApiErrorCategory.timeout,
      );
    } on SocketException {
      throw ApiException(
        code: 'E-NETWORK-000',
        message: 'Could not reach the server - check your connection.',
        category: ApiErrorCategory.network,
      );
    } on http.ClientException {
      throw ApiException(
        code: 'E-NETWORK-000',
        message: 'Could not reach the server - check your connection.',
        category: ApiErrorCategory.network,
      );
    }
  }

  dynamic _parseEnvelope(http.Response response) {
    late final Map<String, dynamic> envelope;
    try {
      envelope = jsonDecode(response.body) as Map<String, dynamic>;
    } on FormatException {
      throw ApiException(
        code: 'E-NETWORK-000',
        message: 'Unexpected response from server (status ${response.statusCode}).',
        category: response.statusCode >= 500 ? ApiErrorCategory.server : ApiErrorCategory.unknown,
      );
    }

    if (envelope['success'] == true) {
      return envelope['data'];
    }

    final errors = envelope['errors'] as List<dynamic>? ?? const [];
    final first = errors.isNotEmpty ? errors.first as Map<String, dynamic> : null;
    throw ApiException(
      code: first?['code'] as String? ?? 'E-UNKNOWN-000',
      message: (first?['message'] as String?) ??
          envelope['message'] as String? ??
          'Request failed.',
      category: _categoryForStatus(response.statusCode),
    );
  }

  ApiErrorCategory _categoryForStatus(int statusCode) {
    if (statusCode >= 500) return ApiErrorCategory.server;
    if (statusCode >= 400) return ApiErrorCategory.validation;
    return ApiErrorCategory.unknown;
  }
}
