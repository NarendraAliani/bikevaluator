// Full Path: test/core/api_client_test.dart
// Purpose: Unit tests for ApiClient's envelope parsing - success unwraps
//   `data`; failure throws ApiException carrying the backend's error code.
import 'dart:convert';
import 'dart:io';

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

  // IMP-003B Task 7/9: timeout, network-failure, and server-failure
  // differentiation, each with a distinct user-friendly message.

  test('get() throws a timeout ApiException when the server never responds in time', () async {
    final client = ApiClient(
      timeout: const Duration(milliseconds: 50),
      client: MockClient((request) async {
        await Future.delayed(const Duration(milliseconds: 500));
        return http.Response(jsonEncode({'success': true, 'data': {}}), 200);
      }),
    );
    await expectLater(
      client.get('/vehicles/brands'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.category, 'category', ApiErrorCategory.timeout)
            .having((e) => e.userFriendlyMessage, 'userFriendlyMessage', contains('took too long')),
      ),
    );
  });

  test('get() throws a network ApiException on SocketException', () async {
    final client = ApiClient(
      client: MockClient((request) async {
        throw const SocketException('Connection refused');
      }),
    );
    await expectLater(
      client.get('/vehicles/brands'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.category, 'category', ApiErrorCategory.network)
            .having((e) => e.userFriendlyMessage, 'userFriendlyMessage', contains('No connection')),
      ),
    );
  });

  test('get() categorizes a 500 response as a server failure', () async {
    final client = ApiClient(
      client: MockClient((request) async {
        return http.Response(
          jsonEncode({
            'success': false,
            'message': 'Internal error',
            'errors': [
              {'code': 'E-INTERNAL-000', 'message': 'Internal error', 'field': null}
            ],
          }),
          500,
        );
      }),
    );
    await expectLater(
      client.get('/vehicles/brands'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.category, 'category', ApiErrorCategory.server)
            .having((e) => e.userFriendlyMessage, 'userFriendlyMessage', contains('our side')),
      ),
    );
  });

  test('get() categorizes a 400 response as a validation failure', () async {
    final client = ApiClient(
      client: MockClient((request) async {
        return http.Response(
          jsonEncode({
            'success': false,
            'message': 'Bad request',
            'errors': [
              {'code': 'E-VALIDATION-000', 'message': 'year is required', 'field': 'year'}
            ],
          }),
          400,
        );
      }),
    );
    await expectLater(
      client.get('/vehicles/brands'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.category, 'category', ApiErrorCategory.validation)
            .having((e) => e.userFriendlyMessage, 'userFriendlyMessage', 'year is required'),
      ),
    );
  });

  test('a request succeeds again after a prior failure (recovery/retry)', () async {
    var callCount = 0;
    final client = ApiClient(
      client: MockClient((request) async {
        callCount += 1;
        if (callCount == 1) {
          throw const SocketException('Connection refused');
        }
        return http.Response(
          jsonEncode({'success': true, 'message': 'Success', 'data': {'brands': []}}),
          200,
        );
      }),
    );

    await expectLater(
      client.get('/vehicles/brands'),
      throwsA(isA<ApiException>().having((e) => e.category, 'category', ApiErrorCategory.network)),
    );

    final data = await client.get('/vehicles/brands');
    expect(data['brands'], isEmpty);
    expect(callCount, 2);
  });
}
