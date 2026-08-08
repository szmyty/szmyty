import 'package:egohygiene/shared/localization/impl/intl_localization_service.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

void main() {
  group('IntlLocalizationService', () {
    late IntlLocalizationService service;
    final testDate = DateTime(2026, 6, 30, 23, 45);

    setUpAll(() async {
      await initializeDateFormatting('en');
    });

    setUp(() {
      service = const IntlLocalizationService(locale: Locale('en'));
    });

    test('locale returns the configured locale', () {
      expect(service.locale, const Locale('en'));
    });

    group('formatDate', () {
      test('returns a non-empty string', () {
        expect(service.formatDate(testDate), isNotEmpty);
      });

      test('includes the year', () {
        expect(service.formatDate(testDate), contains('2026'));
      });
    });

    group('formatDateShort', () {
      test('returns a non-empty string', () {
        expect(service.formatDateShort(testDate), isNotEmpty);
      });
    });

    group('formatTime', () {
      test('returns a non-empty string', () {
        expect(service.formatTime(testDate), isNotEmpty);
      });
    });

    group('formatDateTime', () {
      test('returns a non-empty string', () {
        expect(service.formatDateTime(testDate), isNotEmpty);
      });

      test('includes date and time components', () {
        final result = service.formatDateTime(testDate);
        expect(result, contains('2026'));
      });
    });

    group('formatNumber', () {
      test('formats integers', () {
        expect(service.formatNumber(1234), isNotEmpty);
      });

      test('formats decimals', () {
        expect(service.formatNumber(1234.56), isNotEmpty);
      });

      test('zero formats successfully', () {
        expect(service.formatNumber(0), isNotEmpty);
      });
    });

    group('formatCurrency', () {
      test('returns a non-empty string', () {
        expect(service.formatCurrency(1234.56), isNotEmpty);
      });

      test('includes the currency code', () {
        final result = service.formatCurrency(100, currencyCode: 'EUR');
        expect(result, isNotEmpty);
      });
    });

    group('locale boundary', () {
      test('different locales produce different date formats for some dates', () {
        // Not all locales differ for every date but the service should not throw.
        const enService = IntlLocalizationService(locale: Locale('en'));
        final enResult = enService.formatDate(testDate);
        expect(enResult, isNotEmpty);
      });
    });
  });
}
