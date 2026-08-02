// Full Path: lib/core/api_client.dart
// Module: bikevaluator_app / core
// Purpose: Single HTTP client wrapper - base URL, actor headers, and
//   response-envelope parsing (API-000 v1.1), shared by every feature.
// Related Documents: API-000 v1.1, API-001, EP-002 Architecture Observation #3
import 'dart:convert';

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

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'X-Actor-Id': kDummyActorId,
        'X-Actor-Role': kDummyActorRole,
      };

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final uri = Uri.parse('$kApiBaseUrl$path').replace(queryParameters: query);
    final response = await _client.get(uri, headers: _headers);
    return _parseEnvelope(response);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body) async {
    final uri = Uri.parse('$kApiBaseUrl$path');
    final response =
        await _client.post(uri, headers: _headers, body: jsonEncode(body));
    return _parseEnvelope(response);
  }

  dynamic _parseEnvelope(http.Response response) {
    late final Map<String, dynamic> envelope;
    try {
      envelope = jsonDecode(response.body) as Map<String, dynamic>;
    } on FormatException {
      throw ApiException(
        code: 'E-NETWORK-000',
        message: 'Unexpected response from server (status ${response.statusCode}).',
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
    );
  }
}
