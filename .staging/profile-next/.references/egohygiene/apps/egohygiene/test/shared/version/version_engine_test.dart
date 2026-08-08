import 'package:egohygiene/shared/providers/version_providers.dart';
import 'package:egohygiene/shared/version/app_version.dart';
import 'package:egohygiene/shared/version/release_metadata.dart';
import 'package:egohygiene/shared/version/update_install_mode.dart';
import 'package:egohygiene/shared/version/update_provider.dart';
import 'package:egohygiene/shared/version/update_status.dart';
import 'package:egohygiene/shared/version/version_comparator.dart';
import 'package:egohygiene/shared/version/version_manager.dart';
import 'package:egohygiene/shared/version/version_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeVersionService implements VersionService {
  _FakeVersionService(this.version);

  final String version;

  @override
  Future<String> currentVersion() async => version;
}

class _FakeUpdateProvider implements UpdateProvider {
  _FakeUpdateProvider({
    required this.providerId,
    this.available = true,
    this.release,
    this.shouldThrow = false,
  });

  @override
  final String providerId;

  bool available;
  ReleaseMetadata? release;
  bool shouldThrow;

  @override
  Future<bool> get isAvailable async => available;

  @override
  Future<ReleaseMetadata?> fetchLatestRelease({
    String channel = 'stable',
  }) async {
    if (shouldThrow) {
      throw StateError('provider failed');
    }
    return release;
  }
}

void main() {
  group('AppVersion', () {
    test('parses semantic versions with v-prefix and pre-release', () {
      final parsed = AppVersion.parse('v1.2.3-beta.1+42');

      expect(parsed.major, 1);
      expect(parsed.minor, 2);
      expect(parsed.patch, 3);
      expect(parsed.preRelease, ['beta', '1']);
      expect(parsed.buildMetadata, '42');
      expect(parsed.normalized, '1.2.3-beta.1+42');
    });

    test('normalizes missing parts to zero', () {
      final parsed = AppVersion.parse('2');

      expect(parsed.normalized, '2.0.0');
    });
  });

  group('VersionComparator', () {
    const comparator = VersionComparator();

    test('compares stable releases numerically', () {
      expect(comparator.compare('1.10.0', '1.9.9'), greaterThan(0));
      expect(comparator.compare('2.0.0', '2.0.0'), 0);
      expect(comparator.compare('1.9.0', '1.10.0'), lessThan(0));
    });

    test('treats stable as newer than matching pre-release', () {
      expect(comparator.compare('1.2.3', '1.2.3-beta.1'), greaterThan(0));
      expect(comparator.compare('1.2.3-beta.1', '1.2.3'), lessThan(0));
    });

    test('compares pre-release identifiers correctly', () {
      expect(comparator.compare('1.2.3-beta.2', '1.2.3-beta.1'), greaterThan(0));
      expect(comparator.compare('1.2.3-alpha', '1.2.3-beta'), lessThan(0));
    });
  });

  group('VersionManager', () {
    test('release metadata defaults to a store-based update experience', () {
      final release = ReleaseMetadata(
        providerId: 'app-store',
        version: AppVersion.parse('1.0.1'),
        publishedAt: DateTime.utc(2026, 7, 1, 12),
      );

      expect(release.availableModes, {UpdateInstallMode.store});
      expect(release.highlights, isEmpty);
      expect(release.migrationNotes, isEmpty);
    });

    test('reports unavailable when provider cannot check updates', () async {
      final provider = _FakeUpdateProvider(
        providerId: 'github',
        available: false,
      );
      final manager = VersionManager(
        versionService: _FakeVersionService('1.0.0'),
        updateProvider: provider,
      );

      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.unavailable);
      expect(status.currentVersion, '1.0.0');
      expect(status.message, 'provider_unavailable:github');
    });

    test('reports update available when release is newer', () async {
      final release = ReleaseMetadata(
        providerId: 'github',
        version: AppVersion.parse('1.3.0'),
        publishedAt: DateTime.utc(2026, 7, 1, 12),
      );
      final manager = VersionManager(
        versionService: _FakeVersionService('1.2.9'),
        updateProvider: _FakeUpdateProvider(
          providerId: 'github',
          release: release,
        ),
      );

      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.updateAvailable);
      expect(status.isUpdateAvailable, isTrue);
      expect(status.release, same(release));
      expect(status.isRequiredUpdate, isFalse);
    });

    test('reports up-to-date when release is not newer', () async {
      final manager = VersionManager(
        versionService: _FakeVersionService('1.2.3'),
        updateProvider: _FakeUpdateProvider(
          providerId: 'github',
          release: ReleaseMetadata(
            providerId: 'github',
            version: AppVersion.parse('1.2.3'),
            publishedAt: DateTime.utc(2026, 7, 1, 12),
          ),
        ),
      );

      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.upToDate);
      expect(status.isUpToDate, isTrue);
    });

    test('marks update as required when current version is below minimum supported', () async {
      final manager = VersionManager(
        versionService: _FakeVersionService('1.0.0'),
        updateProvider: _FakeUpdateProvider(
          providerId: 'play',
          release: ReleaseMetadata(
            providerId: 'play',
            version: AppVersion.parse('1.4.0'),
            publishedAt: DateTime.utc(2026, 7, 1, 12),
            minimumSupportedVersion: AppVersion.parse('1.2.0'),
            availableModes: const {UpdateInstallMode.immediate},
          ),
        ),
      );

      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.updateAvailable);
      expect(status.isRequiredUpdate, isTrue);
      expect(status.isFlexibleUpdate, isFalse);
    });

    test('captures provider errors in status', () async {
      final manager = VersionManager(
        versionService: _FakeVersionService('1.0.0'),
        updateProvider: _FakeUpdateProvider(
          providerId: 'github',
          shouldThrow: true,
        ),
      );

      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.error);
      expect(status.message, contains('provider failed'));
    });
  });

  group('version providers', () {
    test('supports overriding service and provider implementations', () async {
      final release = ReleaseMetadata(
        providerId: 'enterprise',
        version: AppVersion.parse('3.0.0'),
        publishedAt: DateTime.utc(2026, 7, 1, 12),
      );
      final container = ProviderContainer(
        overrides: [
          versionServiceProvider.overrideWithValue(_FakeVersionService('2.0.0')),
          updateProviderProvider.overrideWithValue(
            _FakeUpdateProvider(providerId: 'enterprise', release: release),
          ),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(versionManagerProvider);
      final status = await manager.checkForUpdates();

      expect(status.state, UpdateState.updateAvailable);
      expect(status.release, same(release));
    });
  });
}
