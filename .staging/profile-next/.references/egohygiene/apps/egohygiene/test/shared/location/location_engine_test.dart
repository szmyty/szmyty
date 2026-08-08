import 'package:egohygiene/shared/location/app_location.dart';
import 'package:egohygiene/shared/location/geocoded_address.dart';
import 'package:egohygiene/shared/location/geocoding_provider.dart';
import 'package:egohygiene/shared/location/impl/disabled_location_provider.dart';
import 'package:egohygiene/shared/location/impl/location_context_source.dart';
import 'package:egohygiene/shared/location/impl/manual_location_provider.dart';
import 'package:egohygiene/shared/location/impl/noop_geocoding_provider.dart';
import 'package:egohygiene/shared/location/impl/noop_timezone_resolver.dart';
import 'package:egohygiene/shared/location/location_accuracy.dart';
import 'package:egohygiene/shared/location/location_coordinate.dart';
import 'package:egohygiene/shared/location/location_manager.dart';
import 'package:egohygiene/shared/location/location_mode.dart';
import 'package:egohygiene/shared/location/location_permission_status.dart';
import 'package:egohygiene/shared/location/location_provider.dart';
import 'package:egohygiene/shared/location/location_snapshot.dart';
import 'package:egohygiene/shared/location/timezone_resolver.dart';
import 'package:egohygiene/shared/providers/location_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Fakes
// ---------------------------------------------------------------------------

class _FakeLocationProvider implements LocationProvider {
  _FakeLocationProvider({
    this.mode = LocationMode.precise,
    this._permStatus = LocationPermissionStatus.granted,
    this._location,
  }) : _available = true;

  @override
  String get providerId => 'fake';

  @override
  final LocationMode mode;

  final bool _available;
  LocationPermissionStatus _permStatus;
  AppLocation? _location;

  int initializeCount = 0;
  int disposeCount = 0;
  LocationCoordinate? lastManualCoordinate;

  @override
  Future<bool> get isAvailable async => _available;

  @override
  Future<LocationPermissionStatus> get permissionStatus async => _permStatus;

  @override
  Future<void> initialize() async => initializeCount++;

  @override
  Future<LocationPermissionStatus> requestPermission() async {
    _permStatus = LocationPermissionStatus.granted;
    return _permStatus;
  }

  @override
  Future<AppLocation?> getCurrentLocation() async => _location;

  @override
  Future<AppLocation?> getLastKnownLocation() async => _location;

  @override
  Future<void> setManualCoordinate(LocationCoordinate coordinate) async {
    lastManualCoordinate = coordinate;
  }

  @override
  Future<void> clearManualCoordinate() async {
    lastManualCoordinate = null;
  }

  @override
  Future<void> dispose() async => disposeCount++;
}

class _FakeGeocodingProvider implements GeocodingProvider {
  _FakeGeocodingProvider({
    this.address,
  });

  final GeocodedAddress? address;

  int reverseGeocodeCount = 0;
  int geocodeCount = 0;

  @override
  String get providerId => 'fake';

  @override
  Future<LocationCoordinate?> geocode(String query) async {
    geocodeCount++;
    return null;
  }

  @override
  Future<GeocodedAddress?> reverseGeocode(LocationCoordinate coordinate) async {
    reverseGeocodeCount++;
    return address;
  }
}

class _FakeTimezoneResolver implements TimezoneResolver {
  _FakeTimezoneResolver({this.timezone, this.locale});

  final String? timezone;
  final String? locale;

  @override
  String get resolverId => 'fake';

  @override
  Future<String?> resolveTimezone(LocationCoordinate coordinate) async => timezone;

  @override
  Future<String?> resolveLocale(LocationCoordinate coordinate) async => locale;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const _coordinate = LocationCoordinate(latitude: 37.7749, longitude: -122.4194);

AppLocation _location({
  LocationCoordinate? coordinate,
  LocationAccuracy accuracy = LocationAccuracy.precise,
  LocationMode mode = LocationMode.precise,
  DateTime? capturedAt,
  GeocodedAddress? address,
  String? timezoneId,
  String? localeTag,
}) {
  return AppLocation(
    coordinate: coordinate ?? _coordinate,
    accuracy: accuracy,
    mode: mode,
    capturedAt: capturedAt ?? DateTime.utc(2026, 7, 1, 12),
    address: address,
    timezoneId: timezoneId,
    localeTag: localeTag,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('LocationCoordinate', () {
    test('stores latitude and longitude', () {
      const coord = LocationCoordinate(latitude: 51.5, longitude: -0.1);
      expect(coord.latitude, 51.5);
      expect(coord.longitude, -0.1);
    });

    test('equality is value-based', () {
      const a = LocationCoordinate(latitude: 10, longitude: 20);
      const b = LocationCoordinate(latitude: 10, longitude: 20);
      expect(a, equals(b));
      expect(a.hashCode, b.hashCode);
    });

    test('copyWith updates individual fields', () {
      const original = LocationCoordinate(latitude: 1, longitude: 2);
      final updated = original.copyWith(latitude: 9);
      expect(updated.latitude, 9.0);
      expect(updated.longitude, 2.0);
    });

    test('toString includes coordinates', () {
      const coord = LocationCoordinate(latitude: 40, longitude: -74);
      expect(coord.toString(), contains('40.0'));
      expect(coord.toString(), contains('-74.0'));
    });
  });

  group('GeocodedAddress', () {
    test('displayName prefers formattedAddress', () {
      const address = GeocodedAddress(
        city: 'Portland',
        region: 'Oregon',
        formattedAddress: '123 Main St, Portland, OR',
      );
      expect(address.displayName, '123 Main St, Portland, OR');
    });

    test('displayName falls back to city + region', () {
      const address = GeocodedAddress(city: 'Portland', region: 'Oregon');
      expect(address.displayName, 'Portland, Oregon');
    });

    test('displayName falls back to city only', () {
      const address = GeocodedAddress(city: 'Portland');
      expect(address.displayName, 'Portland');
    });

    test('displayName falls back to region only', () {
      const address = GeocodedAddress(region: 'Oregon');
      expect(address.displayName, 'Oregon');
    });

    test('displayName returns empty string when no data', () {
      const address = GeocodedAddress();
      expect(address.displayName, '');
    });

    test('equality is value-based', () {
      const a = GeocodedAddress(city: 'NYC', country: 'US');
      const b = GeocodedAddress(city: 'NYC', country: 'US');
      expect(a, equals(b));
    });

    test('copyWith updates individual fields', () {
      const original = GeocodedAddress(city: 'San Francisco', country: 'US');
      final updated = original.copyWith(city: 'Oakland');
      expect(updated.city, 'Oakland');
      expect(updated.country, 'US');
    });
  });

  group('LocationSnapshot', () {
    test('empty snapshot has disabled mode and unavailable permission', () {
      final snapshot = LocationSnapshot.empty(capturedAt: DateTime.utc(2026));
      expect(snapshot.mode, LocationMode.disabled);
      expect(snapshot.permissionStatus, LocationPermissionStatus.unavailable);
      expect(snapshot.hasLocation, isFalse);
      expect(snapshot.isLocationUnavailable, isTrue);
    });

    test('hasLocation is true when location is set', () {
      final snapshot = LocationSnapshot(
        mode: LocationMode.precise,
        permissionStatus: LocationPermissionStatus.granted,
        capturedAt: DateTime.utc(2026),
        location: _location(),
      );
      expect(snapshot.hasLocation, isTrue);
      expect(snapshot.isLocationUnavailable, isFalse);
    });

    test('isLocationUnavailable is true when permanently denied', () {
      final snapshot = LocationSnapshot(
        mode: LocationMode.precise,
        permissionStatus: LocationPermissionStatus.permanentlyDenied,
        capturedAt: DateTime.utc(2026),
      );
      expect(snapshot.isLocationUnavailable, isTrue);
    });

    test('equality is value-based', () {
      final capturedAt = DateTime.utc(2026, 7);
      final a = LocationSnapshot(
        mode: LocationMode.manual,
        permissionStatus: LocationPermissionStatus.granted,
        capturedAt: capturedAt,
      );
      final b = LocationSnapshot(
        mode: LocationMode.manual,
        permissionStatus: LocationPermissionStatus.granted,
        capturedAt: capturedAt,
      );
      expect(a, equals(b));
      expect(a.hashCode, b.hashCode);
    });

    test('copyWith updates individual fields', () {
      final snapshot = LocationSnapshot.empty(capturedAt: DateTime.utc(2026));
      final updated = snapshot.copyWith(mode: LocationMode.manual);
      expect(updated.mode, LocationMode.manual);
      expect(updated.permissionStatus, snapshot.permissionStatus);
    });
  });

  group('DisabledLocationProvider', () {
    const provider = DisabledLocationProvider();

    test('has disabled mode', () {
      expect(provider.mode, LocationMode.disabled);
    });

    test('is not available', () async {
      expect(await provider.isAvailable, isFalse);
    });

    test('permission status is unavailable', () async {
      expect(
        await provider.permissionStatus,
        LocationPermissionStatus.unavailable,
      );
    });

    test('requestPermission returns unavailable', () async {
      expect(
        await provider.requestPermission(),
        LocationPermissionStatus.unavailable,
      );
    });

    test('getCurrentLocation returns null', () async {
      expect(await provider.getCurrentLocation(), isNull);
    });

    test('getLastKnownLocation returns null', () async {
      expect(await provider.getLastKnownLocation(), isNull);
    });

    test('lifecycle methods are no-ops', () async {
      await expectLater(provider.initialize(), completes);
      await expectLater(provider.dispose(), completes);
      await expectLater(
        provider.setManualCoordinate(_coordinate),
        completes,
      );
      await expectLater(provider.clearManualCoordinate(), completes);
    });
  });

  group('ManualLocationProvider', () {
    test('mode is manual', () {
      expect(ManualLocationProvider().mode, LocationMode.manual);
    });

    test('is not available without a coordinate', () async {
      expect(await ManualLocationProvider().isAvailable, isFalse);
    });

    test('is available when a coordinate is set', () async {
      final provider = ManualLocationProvider(initialCoordinate: _coordinate);
      expect(await provider.isAvailable, isTrue);
    });

    test('getCurrentLocation returns location for set coordinate', () async {
      final provider = ManualLocationProvider(initialCoordinate: _coordinate);
      final location = await provider.getCurrentLocation();
      expect(location, isNotNull);
      expect(location!.coordinate, _coordinate);
      expect(location.mode, LocationMode.manual);
      expect(location.accuracy, LocationAccuracy.approximate);
    });

    test('getCurrentLocation returns null when no coordinate', () async {
      expect(await ManualLocationProvider().getCurrentLocation(), isNull);
    });

    test('setManualCoordinate updates location', () async {
      final provider = ManualLocationProvider();
      await provider.setManualCoordinate(_coordinate);
      final location = await provider.getCurrentLocation();
      expect(location!.coordinate, _coordinate);
    });

    test('clearManualCoordinate removes location', () async {
      final provider = ManualLocationProvider(initialCoordinate: _coordinate);
      await provider.clearManualCoordinate();
      expect(await provider.getCurrentLocation(), isNull);
    });

    test('permission status is always granted', () async {
      expect(
        await ManualLocationProvider().permissionStatus,
        LocationPermissionStatus.granted,
      );
    });

    test('dispose clears coordinate', () async {
      final provider = ManualLocationProvider(initialCoordinate: _coordinate);
      await provider.dispose();
      expect(await provider.getCurrentLocation(), isNull);
    });
  });

  group('NoopGeocodingProvider', () {
    const provider = NoopGeocodingProvider();

    test('geocode returns null', () async {
      expect(await provider.geocode('San Francisco'), isNull);
    });

    test('reverseGeocode returns null', () async {
      expect(await provider.reverseGeocode(_coordinate), isNull);
    });
  });

  group('NoopTimezoneResolver', () {
    const resolver = NoopTimezoneResolver();

    test('resolveTimezone returns null', () async {
      expect(await resolver.resolveTimezone(_coordinate), isNull);
    });

    test('resolveLocale returns null', () async {
      expect(await resolver.resolveLocale(_coordinate), isNull);
    });
  });

  group('LocationManager', () {
    test('initialize calls provider.initialize once', () async {
      final provider = _FakeLocationProvider();
      final manager = LocationManager(provider: provider);

      await manager.initialize();
      await manager.initialize(); // idempotent

      expect(provider.initializeCount, 1);
    });

    test('mode delegates to provider', () {
      final provider = _FakeLocationProvider(mode: LocationMode.approximate);
      final manager = LocationManager(provider: provider);
      expect(manager.mode, LocationMode.approximate);
    });

    test('fetchLocation returns null when provider returns null', () async {
      final provider = _FakeLocationProvider();
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      expect(await manager.fetchLocation(), isNull);
    });

    test('fetchLocation returns location from provider', () async {
      final loc = _location();
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      final result = await manager.fetchLocation(enrich: false);
      expect(result, isNotNull);
      expect(result!.coordinate, _coordinate);
    });

    test('fetchLocation caches last known location', () async {
      final loc = _location();
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      await manager.fetchLocation(enrich: false);
      // Now remove the location from provider
      provider._location = null;
      // Last known should still be cached
      final last = await manager.lastKnownLocation();
      expect(last, isNotNull);
      expect(last!.coordinate, _coordinate);
    });

    test('fetchLocation enriches with geocoding and timezone', () async {
      final loc = _location();
      const address = GeocodedAddress(city: 'San Francisco', country: 'US');
      final geocoding = _FakeGeocodingProvider(address: address);
      final timezone = _FakeTimezoneResolver(timezone: 'America/Los_Angeles', locale: 'en_US');
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(
        provider: provider,
        geocodingProvider: geocoding,
        timezoneResolver: timezone,
      );
      await manager.initialize();
      final result = await manager.fetchLocation();
      expect(result, isNotNull);
      expect(result!.address, isNotNull);
      expect(result.address!.city, 'San Francisco');
      expect(result.timezoneId, 'America/Los_Angeles');
      expect(result.localeTag, 'en_US');
      expect(geocoding.reverseGeocodeCount, 1);
    });

    test('fetchLocation with enrich=false skips geocoding', () async {
      final loc = _location();
      final geocoding = _FakeGeocodingProvider(
        address: const GeocodedAddress(city: 'San Francisco'),
      );
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(
        provider: provider,
        geocodingProvider: geocoding,
      );
      await manager.initialize();
      await manager.fetchLocation(enrich: false);
      expect(geocoding.reverseGeocodeCount, 0);
    });

    test('lastKnownLocation falls back to provider', () async {
      final loc = _location();
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      final result = await manager.lastKnownLocation();
      expect(result, isNotNull);
      expect(result!.coordinate, _coordinate);
    });

    test('setManualLocation forwards to provider', () async {
      final provider = _FakeLocationProvider();
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      await manager.setManualLocation(_coordinate);
      expect(provider.lastManualCoordinate, _coordinate);
    });

    test('setManualLocation(null) clears coordinate', () async {
      final provider = _FakeLocationProvider();
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      await manager.setManualLocation(null);
      expect(provider.lastManualCoordinate, isNull);
    });

    test('snapshot returns empty snapshot when location unavailable', () async {
      final provider = _FakeLocationProvider(
        permStatus: LocationPermissionStatus.denied,
      );
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      final snapshot = await manager.snapshot();
      expect(snapshot.hasLocation, isFalse);
      expect(snapshot.permissionStatus, LocationPermissionStatus.denied);
    });

    test('snapshot includes last known location', () async {
      final loc = _location();
      final provider = _FakeLocationProvider(location: loc);
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      await manager.fetchLocation(enrich: false);
      final snapshot = await manager.snapshot();
      expect(snapshot.hasLocation, isTrue);
      expect(snapshot.location!.coordinate, _coordinate);
    });

    test('dispose calls provider.dispose and resets state', () async {
      final provider = _FakeLocationProvider(location: _location());
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      await manager.fetchLocation(enrich: false);
      await manager.dispose();
      expect(provider.disposeCount, 1);
      // fetchLocation returns null after dispose
      expect(await manager.fetchLocation(), isNull);
    });

    test('requestPermission delegates to provider', () async {
      final provider = _FakeLocationProvider(
        permStatus: LocationPermissionStatus.undetermined,
      );
      final manager = LocationManager(provider: provider);
      await manager.initialize();
      final status = await manager.requestPermission();
      expect(status, LocationPermissionStatus.granted);
    });
  });

  group('LocationContextSource', () {
    test('sourceId and displayName are correct', () {
      final manager = LocationManager(
        provider: const DisabledLocationProvider(),
      );
      final source = LocationContextSource(manager: manager);
      expect(source.sourceId, 'location');
      expect(source.displayName, isNotEmpty);
    });

    test('buildContext returns empty map when location is disabled', () async {
      final manager = LocationManager(
        provider: const DisabledLocationProvider(),
      );
      final source = LocationContextSource(manager: manager);
      await source.initialize();
      final context = await source.buildContext();
      expect(context, isEmpty);
    });

    test('buildContext returns empty map when permission unavailable', () async {
      final provider = _FakeLocationProvider(
        permStatus: LocationPermissionStatus.permanentlyDenied,
      );
      final manager = LocationManager(provider: provider);
      final source = LocationContextSource(manager: manager);
      await source.initialize();
      final context = await source.buildContext();
      expect(context, isEmpty);
    });

    test('buildContext includes mode and permission when no location', () async {
      final provider = _FakeLocationProvider();
      final manager = LocationManager(provider: provider);
      final source = LocationContextSource(manager: manager);
      await source.initialize();
      final context = await source.buildContext();
      expect(context['location.mode'], 'precise');
      expect(context['location.permission'], 'granted');
      expect(context.containsKey('location.latitude'), isFalse);
    });

    test('buildContext includes coordinates when location is available', () async {
      final loc = _location(
        coordinate: _coordinate,
        accuracy: LocationAccuracy.approximate,
      );
      final provider = _FakeLocationProvider(
        mode: LocationMode.approximate,
        location: loc,
      );
      final manager = LocationManager(provider: provider);
      final source = LocationContextSource(manager: manager);
      await source.initialize();
      await manager.fetchLocation(enrich: false);
      final context = await source.buildContext();
      expect(context['location.latitude'], 37.7749);
      expect(context['location.longitude'], -122.4194);
      expect(context['location.accuracy'], 'approximate');
    });

    test('buildContext includes timezone and address when enriched', () async {
      const address = GeocodedAddress(
        city: 'San Francisco',
        region: 'California',
        country: 'United States',
        countryCode: 'US',
      );
      final loc = _location(
        address: address,
        timezoneId: 'America/Los_Angeles',
        localeTag: 'en_US',
      );
      final provider = _FakeLocationProvider(
        location: loc,
      );
      final manager = LocationManager(provider: provider);
      final source = LocationContextSource(manager: manager);
      await source.initialize();
      await manager.fetchLocation(enrich: false);
      final context = await source.buildContext();
      expect(context['location.timezone'], 'America/Los_Angeles');
      expect(context['location.locale'], 'en_US');
      expect(context['location.city'], 'San Francisco');
      expect(context['location.region'], 'California');
      expect(context['location.country'], 'United States');
      expect(context['location.country_code'], 'US');
    });

    test('dispose completes without error', () async {
      final manager = LocationManager(
        provider: const DisabledLocationProvider(),
      );
      final source = LocationContextSource(manager: manager);
      await expectLater(source.dispose(), completes);
    });
  });

  group('location providers', () {
    test('default locationProviderProvider is DisabledLocationProvider', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final provider = container.read(locationProviderProvider);
      expect(provider, isA<DisabledLocationProvider>());
    });

    test('default geocodingProviderProvider is NoopGeocodingProvider', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final provider = container.read(geocodingProviderProvider);
      expect(provider, isA<NoopGeocodingProvider>());
    });

    test('default timezoneResolverProvider is NoopTimezoneResolver', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final resolver = container.read(timezoneResolverProvider);
      expect(resolver, isA<NoopTimezoneResolver>());
    });

    test('locationManagerProvider builds a LocationManager', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final manager = container.read(locationManagerProvider);
      expect(manager, isA<LocationManager>());
    });

    test('provider overrides are respected', () async {
      final fakeProvider = ManualLocationProvider(initialCoordinate: _coordinate);
      final container = ProviderContainer(
        overrides: [
          locationProviderProvider.overrideWithValue(fakeProvider),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(locationManagerProvider);
      await manager.initialize();
      final snapshot = await manager.snapshot();
      expect(snapshot.mode, LocationMode.manual);
    });
  });
}
