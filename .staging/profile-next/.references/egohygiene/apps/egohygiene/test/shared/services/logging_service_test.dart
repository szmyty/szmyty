import 'package:egohygiene/shared/services/impl/app_logging_service.dart';
import 'package:egohygiene/shared/services/impl/noop_logging_service.dart';
import 'package:egohygiene/shared/services/logging_service.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Fake appender that captures records for assertion
// ---------------------------------------------------------------------------

class _CapturingAppender implements LogAppender {
  final List<LogRecord> records = [];
  bool disposed = false;

  @override
  void append(LogRecord record) => records.add(record);

  @override
  Future<void> dispose() async => disposed = true;
}

/// Appender that throws on every [append] call.
class _ThrowingAppender implements LogAppender {
  @override
  void append(LogRecord record) => throw Exception('appender failure');

  @override
  Future<void> dispose() async {}
}

// ---------------------------------------------------------------------------
// LogRecord tests
// ---------------------------------------------------------------------------

void main() {
  group('LogRecord', () {
    test('now() captures a timestamp', () {
      final before = DateTime.now();
      final record = LogRecord.now(
        level: LogLevel.info,
        message: 'hello',
      );
      final after = DateTime.now();

      expect(
        record.timestamp.isAfter(before) || record.timestamp.isAtSameMomentAs(before),
        isTrue,
      );
      expect(
        record.timestamp.isBefore(after) || record.timestamp.isAtSameMomentAs(after),
        isTrue,
      );
    });

    test('toString includes level and message', () {
      final record = LogRecord.now(
        level: LogLevel.warning,
        message: 'something fishy',
      );
      final s = record.toString();
      expect(s, contains('WARNING'));
      expect(s, contains('something fishy'));
    });

    test('toString includes tag when set', () {
      final record = LogRecord.now(
        level: LogLevel.debug,
        message: 'msg',
        tag: 'AuthService',
      );
      expect(record.toString(), contains('AuthService'));
    });

    test('toString includes error and stackTrace', () {
      final st = StackTrace.current;
      final record = LogRecord.now(
        level: LogLevel.error,
        message: 'oops',
        error: Exception('bad'),
        stackTrace: st,
      );
      final s = record.toString();
      expect(s, contains('bad'));
      expect(s, contains(st.toString()));
    });

    test('toString includes metadata', () {
      final record = LogRecord.now(
        level: LogLevel.info,
        message: 'structured',
        metadata: {'userId': '42', 'action': 'login'},
      );
      expect(record.toString(), contains('userId'));
    });

    test('const constructor preserves all fields', () {
      final record = LogRecord(
        level: LogLevel.fatal,
        message: 'boom',
        timestamp: DateTime(2024, 1, 15, 10, 30),
      );
      expect(record.level, LogLevel.fatal);
      expect(record.message, 'boom');
    });
  });

  // -------------------------------------------------------------------------
  // LogLevel ordering
  // -------------------------------------------------------------------------

  group('LogLevel ordering', () {
    test('levels have correct relative indices', () {
      expect(LogLevel.verbose.index, lessThan(LogLevel.debug.index));
      expect(LogLevel.debug.index, lessThan(LogLevel.info.index));
      expect(LogLevel.info.index, lessThan(LogLevel.warning.index));
      expect(LogLevel.warning.index, lessThan(LogLevel.error.index));
      expect(LogLevel.error.index, lessThan(LogLevel.fatal.index));
    });
  });

  // -------------------------------------------------------------------------
  // AppLoggingService
  // -------------------------------------------------------------------------

  group('AppLoggingService', () {
    late _CapturingAppender appender;
    late AppLoggingService service;

    setUp(() {
      appender = _CapturingAppender();
      service = AppLoggingService(
        appenders: [appender],
        minimumLevel: LogLevel.verbose,
      );
    });

    tearDown(() async => service.dispose());

    test('verbose() emits a record at verbose level', () {
      service.verbose('trace this');
      expect(appender.records, hasLength(1));
      expect(appender.records.first.level, LogLevel.verbose);
      expect(appender.records.first.message, 'trace this');
    });

    test('debug() emits a record at debug level', () {
      service.debug('debug info');
      expect(appender.records.first.level, LogLevel.debug);
    });

    test('info() emits a record at info level', () {
      service.info('app started');
      expect(appender.records.first.level, LogLevel.info);
    });

    test('warning() emits a record at warning level', () {
      service.warning('slow network');
      expect(appender.records.first.level, LogLevel.warning);
    });

    test('error() emits a record at error level', () {
      service.error('database failure');
      expect(appender.records.first.level, LogLevel.error);
    });

    test('fatal() emits a record at fatal level', () {
      service.fatal('unrecoverable crash');
      expect(appender.records.first.level, LogLevel.fatal);
    });

    test('forwards tag to record', () {
      service.info('tagged', tag: 'SomeModule');
      expect(appender.records.first.tag, 'SomeModule');
    });

    test('forwards error and stackTrace to record', () {
      final err = Exception('kaboom');
      final st = StackTrace.current;
      service.error('failed', error: err, stackTrace: st);
      expect(appender.records.first.error, err);
      expect(appender.records.first.stackTrace, st);
    });

    test('forwards metadata to record', () {
      service.info('structured', metadata: {'key': 'value'});
      expect(appender.records.first.metadata, {'key': 'value'});
    });

    test('records below minimumLevel are discarded', () {
      final filtered = AppLoggingService(
        appenders: [appender],
        minimumLevel: LogLevel.warning,
      );

      filtered.verbose('nope');
      filtered.debug('nope');
      filtered.info('nope');
      filtered.warning('this one');

      expect(appender.records, hasLength(1));
      expect(appender.records.first.level, LogLevel.warning);

      filtered.dispose();
    });

    test('records at exactly minimumLevel are emitted', () {
      final exact = AppLoggingService(
        appenders: [appender],
        minimumLevel: LogLevel.error,
      );

      exact.error('exact level');

      expect(appender.records, hasLength(1));
      exact.dispose();
    });

    test('multiple appenders all receive the same record', () {
      final second = _CapturingAppender();
      final multi = AppLoggingService(
        appenders: [appender, second],
        minimumLevel: LogLevel.verbose,
      );

      multi.info('broadcast');

      expect(appender.records, hasLength(1));
      expect(second.records, hasLength(1));
      expect(appender.records.first.message, 'broadcast');
      expect(second.records.first.message, 'broadcast');

      multi.dispose();
    });

    test('a throwing appender does not affect subsequent appenders', () {
      final throwing = _ThrowingAppender();
      final safe = _CapturingAppender();
      final fallbackMessages = <String>[];
      final multi = AppLoggingService(
        appenders: [throwing, safe],
        minimumLevel: LogLevel.verbose,
        appenderFailureReporter: fallbackMessages.add,
      );

      expect(() => multi.info('resilient'), returnsNormally);
      expect(safe.records, hasLength(1));
      expect(fallbackMessages.single, contains('_ThrowingAppender'));
      expect(fallbackMessages.single, contains('appender failure'));

      multi.dispose();
    });

    test('dispose() calls dispose on all appenders', () async {
      final second = _CapturingAppender();
      final multi = AppLoggingService(
        appenders: [appender, second],
        minimumLevel: LogLevel.verbose,
      );

      await multi.dispose();

      expect(appender.disposed, isTrue);
      expect(second.disposed, isTrue);
    });

    // ── Performance logging ──────────────────────────────────────────────

    test('performance measurement emits a debug record when within threshold', () {
      final token = service.startPerformance('loadData', tag: 'Repository');
      service.endPerformance(
        token,
        warnThreshold: const Duration(seconds: 60),
      );

      expect(appender.records, hasLength(1));
      final rec = appender.records.first;
      expect(rec.level, LogLevel.debug);
      expect(rec.message, contains('loadData'));
      expect(rec.tag, 'Repository');
      expect(rec.metadata, containsPair('elapsed_ms', isA<int>()));
    });

    test('performance measurement emits a warning when threshold exceeded', () {
      final token = PerformanceToken(
        operationName: 'heavyQuery',
        startedAt: DateTime.now().subtract(const Duration(seconds: 2)),
        tag: 'Database',
      );

      service.endPerformance(
        token,
        warnThreshold: const Duration(milliseconds: 100),
      );

      expect(appender.records.first.level, LogLevel.warning);
      expect(appender.records.first.message, contains('heavyQuery'));
    });

    test('startPerformance token captures operation name and tag', () {
      final token = service.startPerformance('myOp', tag: 'MyTag');
      expect(token.operationName, 'myOp');
      expect(token.tag, 'MyTag');
    });

    test('minimumLevel getter returns configured level', () {
      expect(service.minimumLevel, LogLevel.verbose);
    });
  });

  // -------------------------------------------------------------------------
  // NoopLoggingService
  // -------------------------------------------------------------------------

  group('NoopLoggingService', () {
    const noop = NoopLoggingService();

    test('minimumLevel is fatal', () {
      expect(noop.minimumLevel, LogLevel.fatal);
    });

    test('all log methods execute without throwing', () {
      expect(() => noop.verbose('v'), returnsNormally);
      expect(() => noop.debug('d'), returnsNormally);
      expect(() => noop.info('i'), returnsNormally);
      expect(() => noop.warning('w'), returnsNormally);
      expect(() => noop.error('e'), returnsNormally);
      expect(() => noop.fatal('f'), returnsNormally);
    });

    test('startPerformance returns a valid token', () {
      final token = noop.startPerformance('op', tag: 'T');
      expect(token.operationName, 'op');
      expect(token.tag, 'T');
    });

    test('endPerformance executes without throwing', () {
      final token = noop.startPerformance('op');
      expect(() => noop.endPerformance(token), returnsNormally);
    });

    test('dispose completes without error', () async {
      await expectLater(noop.dispose(), completes);
    });
  });
}
