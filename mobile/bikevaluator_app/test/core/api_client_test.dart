// Full Path: test/core/api_client_test.dart
// Purpose: Unit tests for ApiClient's envelope parsing - success unwraps
//   `data`; failure throws ApiException carrying the backend's error code.
import 'dart:convert';

import 'package:bikevaluator_app/core/api_client.dart';
import 'package:bikevaluator_app/core/api_exception.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('get() unwraps the data field on success envelope', () async {
    final client = ApiClient(
      client: MockClient((request) async {
        expect(request.headers['X-Actor-Id'], kDummyActorId);
        expect(request.headers['X-Actor-Role'], kDummyActorRole);
        return http.Response(
          jsonEncode({
            'success': true,
            'message': 'Success',
            'data': {'brands': []}
          }),
          200,
        );
      }),
    );
    final data = await client.get('/vehicles/brands');
    expect(data['brands'], isEmpty);
  });

  test('get() throws ApiException with the backend error code on failure', () async {
    final client = ApiClient(
      client: MockClient((request) async {
        return http.Response(
          jsonEncode({
            'success': false,
            'message': 'Pricing not available',
            'errors': [
              {'code': 'VAL003', 'message': 'Pricing not available', 'field': null}
            ],
          }),
          404,
        );
      }),
    );
    expect(
      () => client.get('/valuation/calculate'),
      throwsA(isA<ApiException>().having((e) => e.code, 'code', 'VAL003')),
    );
  });

  test('ApiException.isPricingUnavailable recognizes VAL003 and E-PRICING-001', () {
    expect(ApiException(code: 'VAL003', message: '').isPricingUnavailable, isTrue);
    expect(ApiException(code: 'E-PRICING-001', message: '').isPricingUnavailable, isTrue);
    expect(ApiException(code: 'E-CATALOG-002', message: '').isPricingUnavailable, isFalse);
  });
}
