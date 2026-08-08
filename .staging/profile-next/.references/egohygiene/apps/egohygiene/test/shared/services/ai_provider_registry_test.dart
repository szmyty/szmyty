import 'package:dio/dio.dart';
import 'package:egohygiene/shared/environment/environment.dart';
import 'package:egohygiene/shared/environment/environment_configuration.dart';
import 'package:egohygiene/shared/environment/impl/local_environment_provider.dart';
import 'package:egohygiene/shared/flags/impl/local_feature_flag_provider.dart';
import 'package:egohygiene/shared/providers/ai_provider_registry_providers.dart';
import 'package:egohygiene/shared/providers/environment_providers.dart';
import 'package:egohygiene/shared/providers/feature_flag_providers.dart';
import 'package:egohygiene/shared/services/ai_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeProvider implements AIProvider {
  _FakeProvider({
    required this.configuration,
    required this.capabilities,
    required this.available,
  });

  @override
  final AIProviderConfiguration configuration;

  @override
  final ProviderCapabilities capabilities;

  @override
  String get name => configuration.displayName;

  final bool available;

  @override
  AIProviderStatus get status => available ? AIProviderStatus.available : AIProviderStatus.unavailable;

  @override
  Future<void> init() async {}

  @override
  Future<bool> isAvailable() async => available;
}

void main() {
  group('AIProviderRegistry', () {
    test('demo provider self-registers in constructor', () {
      final registry = AIProviderRegistry();

      DemoAIProvider(registry: registry);

      expect(registry.contains('demo'), isTrue);
      expect(registry.byId('demo')?.name, 'Demo AI Provider');
    });

    group('DemoAIProvider', () {
      test('truncates summary to maxLength with period termination', () async {
        final registry = AIProviderRegistry();
        final provider = DemoAIProvider(registry: registry);

        final summary = await provider.summarize(
          'A somewhat longer body',
          maxLength: 18,
        );

        expect(summary.length, lessThanOrEqualTo(18));
        expect(summary, startsWith('Demo'));
        expect(summary, endsWith('.'));
      });

      test('summary returns empty string for non-positive maxLength', () async {
        final registry = AIProviderRegistry();
        final provider = DemoAIProvider(registry: registry);

        final summary = await provider.summarize('Body', maxLength: 0);

        expect(summary, isEmpty);
      });

      test('embeddings are deterministic fixed-dimension vectors', () async {
        final registry = AIProviderRegistry();
        final provider = DemoAIProvider(registry: registry);

        final first = await provider.generateEmbedding('hello');
        final second = await provider.generateEmbedding('hello');

        expect(first, equals(second));
        expect(first, hasLength(8));
      });

      test('embeddings differ across different inputs', () async {
        final registry = AIProviderRegistry();
        final provider = DemoAIProvider(registry: registry);

        final hello = await provider.generateEmbedding('hello');
        final world = await provider.generateEmbedding('world');

        expect(hello, isNot(equals(world)));
      });
    });

    group('OllamaAIProvider', () {
      test('returns Ollama chat responses when the local API succeeds', () async {
        final registry = AIProviderRegistry();
        final provider = OllamaAIProvider(
          registry: registry,
          baseUrl: 'http://localhost:11434',
          model: 'llama3.2',
          timeout: const Duration(seconds: 1),
          client: Dio()
            ..interceptors.add(
              InterceptorsWrapper(
                onRequest: (options, handler) {
                  handler.resolve(
                    Response<dynamic>(
                      requestOptions: options,
                      statusCode: 200,
                      data: {
                        'message': {'content': 'Ollama reply'},
                      },
                    ),
                  );
                },
              ),
            ),
        );

        final response = await provider.sendMessage('hello');

        expect(response, 'Ollama reply');
        expect(provider.status, AIProviderStatus.available);
      });

      test('falls back to demo chat responses when Ollama is unavailable', () async {
        final registry = AIProviderRegistry();
        final fallback = DemoAIProvider(registry: registry);
        final provider = OllamaAIProvider(
          registry: registry,
          baseUrl: 'http://localhost:11434',
          model: 'llama3.2',
          timeout: const Duration(seconds: 1),
          fallbackChatProvider: fallback,
          fallbackSummarizationProvider: fallback,
          client: Dio()
            ..interceptors.add(
              InterceptorsWrapper(
                onRequest: (options, handler) {
                  handler.reject(
                    DioException(
                      requestOptions: options,
                      error: 'offline',
                    ),
                  );
                },
              ),
            ),
        );

        final response = await provider.sendMessage('hello');

        expect(response, await fallback.sendMessage('hello'));
        expect(provider.status, AIProviderStatus.error);
      });

      test('falls back to demo summaries when Ollama summarization fails', () async {
        final registry = AIProviderRegistry();
        final fallback = DemoAIProvider(registry: registry);
        final provider = OllamaAIProvider(
          registry: registry,
          baseUrl: 'http://localhost:11434',
          model: 'llama3.2',
          timeout: const Duration(seconds: 1),
          fallbackChatProvider: fallback,
          fallbackSummarizationProvider: fallback,
          client: Dio()
            ..interceptors.add(
              InterceptorsWrapper(
                onRequest: (options, handler) {
                  handler.reject(
                    DioException(
                      requestOptions: options,
                      error: 'offline',
                    ),
                  );
                },
              ),
            ),
        );

        final summary = await provider.summarize(
          'A somewhat longer body',
          maxLength: 18,
        );

        expect(
          summary,
          await fallback.summarize(
            'A somewhat longer body',
            maxLength: 18,
          ),
        );
      });
    });

    test('selects highest-priority available provider for capability', () async {
      final registry = AIProviderRegistry()
        ..registerAll([
          _FakeProvider(
            configuration: const AIProviderConfiguration(
              id: 'offline',
              displayName: 'Offline',
              priority: 1,
            ),
            capabilities: const ProviderCapabilities(chat: true),
            available: false,
          ),
          _FakeProvider(
            configuration: const AIProviderConfiguration(
              id: 'fast',
              displayName: 'Fast',
              priority: 3,
            ),
            capabilities: const ProviderCapabilities(chat: true),
            available: true,
          ),
          _FakeProvider(
            configuration: const AIProviderConfiguration(
              id: 'slow',
              displayName: 'Slow',
              priority: 2,
            ),
            capabilities: const ProviderCapabilities(chat: true),
            available: true,
          ),
        ]);

      final selected = await registry.selectProvider(AIProviderCapability.chat);

      expect(selected?.configuration.id, 'fast');
    });

    test('returns null when no provider supports requested capability', () async {
      final registry = AIProviderRegistry()
        ..register(
          _FakeProvider(
            configuration: const AIProviderConfiguration(
              id: 'summarizer',
              displayName: 'Summarizer',
            ),
            capabilities: const ProviderCapabilities(summarization: true),
            available: true,
          ),
        );

      final selected = await registry.selectProvider(
        AIProviderCapability.audio,
      );

      expect(selected, isNull);
    });
  });

  group('aiProviderRegistryProvider', () {
    test('includes demo provider by default', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final registry = container.read(aiProviderRegistryProvider);
      final provider = registry.byId('demo');

      expect(provider, isNotNull);
      expect(
        provider?.capabilities.supports(AIProviderCapability.streaming),
        isTrue,
      );
    });

    test('registers Ollama when enabled in a real-AI environment', () {
      final container = ProviderContainer(
        overrides: [
          environmentProviderProvider.overrideWithValue(
            const LocalEnvironmentProvider(
              configuration: EnvironmentConfiguration(
                environment: AppEnvironment.development,
              ),
            ),
          ),
          featureFlagProviderProvider.overrideWithValue(
            const LocalFeatureFlagProvider(
              staticValues: {'ollama_ai_provider': true},
            ),
          ),
          aiProviderSelectionProvider.overrideWith((_) => 'ollama'),
        ],
      );
      addTearDown(container.dispose);

      final registry = container.read(aiProviderRegistryProvider);
      final demo = registry.byId('demo');
      final ollama = registry.byId('ollama');

      expect(demo, isNotNull);
      expect(ollama, isA<OllamaAIProvider>());
      expect(
        ollama?.configuration.priority,
        greaterThan(demo!.configuration.priority),
      );
    });

    test('keeps Ollama disabled when the environment uses a mock AI provider', () {
      final container = ProviderContainer(
        overrides: [
          environmentProviderProvider.overrideWithValue(
            const LocalEnvironmentProvider(
              configuration: EnvironmentConfiguration(
                environment: AppEnvironment.demo,
                useMockAiProvider: true,
              ),
            ),
          ),
          featureFlagProviderProvider.overrideWithValue(
            const LocalFeatureFlagProvider(
              staticValues: {'ollama_ai_provider': true},
            ),
          ),
          aiProviderSelectionProvider.overrideWith((_) => 'ollama'),
        ],
      );
      addTearDown(container.dispose);

      final registry = container.read(aiProviderRegistryProvider);

      expect(registry.byId('demo'), isNotNull);
      expect(registry.byId('ollama'), isNull);
    });
  });
}
