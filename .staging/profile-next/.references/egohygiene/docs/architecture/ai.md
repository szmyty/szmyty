# AI Architecture

This document covers the AI capability layer, provider abstractions, context assembly engine, memory engine, and knowledge graph engine.

---

## AI Capability Layer

### Overview

The AI Capability Layer is the application's stable interface to all AI
functionality.  It decouples application logic from provider implementations,
model versions, and inference engines.

The application never names a model or a provider.  Instead, it requests a
**capability** — a named, stable identifier representing what it needs — and
the runtime resolves the most appropriate implementation.

### Architecture

```
Application
  ↓
  AiCapabilityRequest        (what is needed: capability + prompt + context)
  ↓
  AiCapabilityRouter         (selects the best available provider)
  ↓
  AIProviderRegistry         (registry of registered providers)
  ↓
  AIProvider                 (ChatProvider / SummarizationProvider / …)
  ↓
  Model                      (Gemma, Phi, Llama, GPT, Claude, …)
```

The application is never aware of which model performs inference.

### Capability Ontology (`lib/shared/ai/ai_capability.dart`)

All AI interactions must request one or more values from the `AiCapability`
enum rather than referencing a provider or model directly.

| Category | Capability | Description |
|---|---|---|
| Reflective | `reflection` | Guided reflective questioning and journaling support |
| Reflective | `dreamInterpretation` | Exploring symbolic content from dream experiences |
| Conversational | `conversation` | General-purpose conversational AI |
| Analytic | `sentimentAnalysis` | Detecting emotional tone and valence in text |
| Analytic | `entityExtraction` | Identifying named entities and concepts in text |
| Analytic | `classification` | Assigning content to predefined categories |
| Synthesis | `summarization` | Condensing content into concise summaries |
| Synthesis | `researchSynthesis` | Synthesizing research into coherent narratives |
| Structural | `knowledgeGraphConstruction` | Building structured knowledge from unstructured content |
| Structural | `artifactGeneration` | Generating structured artifacts from natural-language prompts |
| Representational | `embeddingGeneration` | Converting text into vector representations |
| Linguistic | `translation` | Translating text between natural languages |

### Core Types

#### `AiCapabilityRequest` (`lib/shared/ai/ai_capability_request.dart`)

Immutable value object carrying what the application needs.

```dart
final request = AiCapabilityRequest(
  capability: AiCapability.reflection,
  prompt: 'I feel overwhelmed by work lately.',
  context: {'source': 'journal'},
);
```

#### `AiCapabilityResult` (`lib/shared/ai/ai_capability_result.dart`)

Immutable value object returned by the router after a capability is fulfilled.

- `capability` — the capability that was requested
- `content` — the primary textual output
- `providerName` — the provider that handled the request (for observability only)
- `isPlaceholder` — whether the result came from a stub implementation
- `metadata` — optional diagnostic information

Application logic must never branch on `providerName`.

#### `AiCapabilityRouter` (`lib/shared/ai/ai_capability_router.dart`)

The single point of dispatch between the application and the provider layer.

```
AiCapabilityRouter
  route(AiCapabilityRequest) → AiCapabilityResult
  canRoute(AiCapability) → bool
  availableCapabilities() → Set<AiCapability>
```

**`DefaultAiCapabilityRouter`** is the default implementation.  It maps each
`AiCapability` to a technical `AIProviderCapability`, selects the best
available provider from `AIProviderRegistry`, and invokes the most specific
provider interface available:

| AiCapability group | Technical capability | Provider interface |
|---|---|---|
| `reflection`, `conversation`, `dreamInterpretation`, `artifactGeneration`, `translation` | `chat` | `ChatProvider` |
| `summarization`, `researchSynthesis` | `summarization` | `SummarizationProvider` |
| `sentimentAnalysis`, `entityExtraction`, `knowledgeGraphConstruction`, `classification` | `insightGeneration` | `InsightProvider` |
| `embeddingGeneration` | `embeddings` | `EmbeddingProvider` |

### Riverpod Providers (`lib/shared/providers/ai_capability_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `aiCapabilityRouterProvider` | `AiCapabilityRouter` | App-wide capability router |

### Barrel Export (`lib/shared/ai/ai_engine.dart`)

```dart
import 'package:egohygiene/shared/ai/ai_engine.dart';
```

### Future Provider Support

The capability layer supports any provider implementation without modifying
application logic.

| Category | Examples |
|---|---|
| Local | Gemma, Phi, Llama, Whisper, on-device embedding models |
| Cloud | OpenAI, Anthropic, Google, Ollama Remote, OpenRouter |
| Hybrid | Automatic local/cloud routing based on device capability and connectivity |

Register new providers via `AIProviderRegistry` and declare their capabilities
via `ProviderCapabilities`.  The router selects the highest-priority available
provider that satisfies the requested capability.

### Relationship to Other Systems

The AI Capability Layer is the foundation for:

- **AI Provider Settings** — exposing available providers and their capabilities to users
- **Local Model Manager** — registering on-device models as `AIProvider` implementations
- **Device Capability Detection** — informing provider selection with hardware limits
- **Task Routing** — routing specific capabilities to specialized backends
- **Guard Rails** — intercepting requests before/after provider invocation
- **Offline Mode** — falling back to local providers when connectivity is absent
- **Hybrid Routing** — choosing between local and cloud execution dynamically

---

## AI Providers

### Service Abstractions
- `AIProvider` — Base AI interface
- `ChatProvider` — Conversational AI
- `InsightProvider` — Insight generation
- `SummarizationProvider` — Content summarization
- `EmbeddingProvider` — Text embeddings

AI provider selection is controlled by `aiProviderSelectionProvider`.
`DemoAIProvider` is the default fallback.  Optional Ollama dart-defines can
activate a local provider.  See [README.md](../../README.md) and
[developer-setup.md](../developer-setup.md) for configuration.

---

## Context Assembly Engine

### Overview

The Context Assembly Engine is the canonical source of context supplied to AI
providers and other downstream consumers.  It gathers information from across
Ego Hygiene and assembles it into a structured, immutable [ContextSnapshot].

Design principle:
- **Context Engine** — knows *what* information is relevant.
- **AI Provider** — knows *how to consume* the assembled context.

These two concerns are deliberately kept separate.

### Architecture

```
ContextManager                   — orchestrator; single entry point for features
  └── ContextSource (0..*)       — contribution provider interface (pluggable)
        └── ReflectionContextSource — reflection history

ContextBuilder                   — fluent builder for assembling a ContextSnapshot
ContextSnapshot                  — immutable point-in-time view of assembled context
```

All files live in `lib/shared/context/`.

### Core Types

#### `ContextSource` (`lib/shared/context/context_source.dart`)

Abstraction for modules that contribute to the assembled context.  Any
component that can supply relevant application state implements this interface.

Lifecycle:
```
Application
  → ContextManager.initialize()
    → ContextSource.initialize()

Caller (AI pipeline, feature module)
  → ContextManager.assemble()
    → ContextSource.buildContext()
      → Map<String, Object?>
        → merged into ContextSnapshot
```

Keys returned by `buildContext()` should be namespaced by source to avoid
collisions (e.g. `'reflection.history'`, `'goals.active'`).

#### `ContextSnapshot` (`lib/shared/context/context_snapshot.dart`)

An immutable point-in-time view of all assembled context.  Safe to pass to AI
providers, serialization pipelines, or downstream systems without risk of the
underlying sources mutating the data.

Utility accessors:
- `get<T>(key)` — typed value lookup
- `entriesWithPrefix(prefix)` — filter entries by namespace prefix
- `hasSource(sourceId)` — check if a source contributed

#### `ContextBuilder` (`lib/shared/context/context_builder.dart`)

Fluent builder for assembling a [ContextSnapshot] from multiple sources.
[ContextManager] is the primary caller.

#### `ContextManager` (`lib/shared/context/context_manager.dart`)

The single entry point for feature modules and AI pipelines.  Coordinates
between zero or more [ContextSource] instances and produces a [ContextSnapshot].

Key operations:
- `initialize()` — initialise all registered sources
- `registerSource(source)` — add a context contributor at runtime
- `assemble()` — collect contributions from all sources and return a snapshot
- `dispose()` — release resources held by registered sources

### Context Sources

#### `ReflectionContextSource` (`lib/shared/context/impl/reflection_context_source.dart`)

Contributes reflection history to the context under the `'reflection.*'`
namespace:
- `'reflection.history'` — all reflections as JSON maps
- `'reflection.count'` — total reflection count
- `'reflection.recentTags'` — top five tags from the ten most-recent entries

### Future Context Sources

Future modules can contribute context by implementing [ContextSource] without
modifying [ContextManager] or existing sources:

| Future Source | Namespace |
|---|---|
| Health integrations | `'health.*'` |
| Calendar | `'calendar.*'` |
| Wearables | `'wearables.*'` |
| Therapist sync | `'therapist.*'` |
| Research summaries | `'research.*'` |
| Knowledge Graph | `'graph.*'` |
| Goals | `'goals.*'` |
| Domains | `'domains.*'` |
| Practices | `'practices.*'` |
| User Profile | `'profile.*'` |

### Riverpod Providers (`lib/shared/providers/context_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `contextManagerProvider` | `ContextManager` | Feature-facing orchestrator |

### Barrel Export (`lib/shared/context/context_engine.dart`)

Import the barrel for convenient access to the full Context Assembly Engine API:

```dart
import 'package:egohygiene/shared/context/context_engine.dart';
```

---

## Context Capture Engine

### Overview

The Context Capture Engine acquires, normalises, timestamps, stores, and
exposes environmental context signals that can be attached to meaningful user
experiences.

Design principle: **capture context** without interpreting it.  The engine
creates a clean, consistent foundation for acquiring signals from external
sources (weather, device state, time, location, health data) and exposing them
as an immutable [ContextCaptureSnapshot].  Causation is never inferred from
context alone.

The engine respects user consent: providers that require permissions expose
`isAvailable` and are silently skipped when not available.

### Architecture

```
ContextCaptureEngine           — orchestrator; single entry point for features
  └── ContextProvider (0..*)  — signal provider interface (pluggable)
        ├── NoopContextProvider  — safe no-op default
        └── TimeContextProvider  — built-in temporal context provider

ContextCategory                — domain category enum (weather / environment /
                                  location / health / calendar / device / time /
                                  custom)
ContextSignal                  — fundamental unit of captured context
ContextCaptureResult           — per-provider success/failure outcome
ContextCaptureSnapshot         — immutable point-in-time view of all signals
```

All files live in `lib/shared/capture/`.

### Core Capture Flow

```
Acquire    → ContextProvider.capture() called for each available provider
Normalize  → signals normalised (keys namespaced, format consistent)
Timestamp  → assembly timestamp added to the snapshot
Store      → latest snapshot cached in ContextCaptureEngine.latestSnapshot
Expose     → snapshot returned to caller; also available synchronously
```

### Core Types

#### `ContextCategory` (`lib/shared/capture/context_category.dart`)

Enum that classifies the domain of a [ContextSignal]:

| Value | Signals |
|---|---|
| `weather` | temperature, humidity, precipitation, UV index |
| `environment` | ambient noise, brightness, air quality |
| `location` | timezone, city, coordinates |
| `health` | heart rate, activity level, sleep quality |
| `calendar` | upcoming events, busy/free status |
| `device` | battery level, network type, orientation |
| `time` | hour of day, weekday, season |
| `custom` | future or domain-specific providers |

#### `ContextSignal` (`lib/shared/capture/context_signal.dart`)

The fundamental unit of the Context Capture Engine.  Carries a namespaced
key-value pair together with provenance metadata (category, providerId,
capturedAt).  Signals are raw observations only — they never interpret
causation or prescribe behaviour.

#### `ContextCaptureResult` (`lib/shared/capture/context_capture_result.dart`)

The outcome of a single [ContextProvider] capture operation.  Either a
`success` carrying a list of [ContextSignal] instances, or a `failure`
carrying an error description.

#### `ContextCaptureSnapshot` (`lib/shared/capture/context_capture_snapshot.dart`)

Immutable point-in-time view of all captured signals.  Safe to pass across
async boundaries or include in downstream systems.  Provides helpers for
filtering by category and looking up signals by key.

#### `ContextProvider` (`lib/shared/capture/context_provider.dart`)

Pluggable provider contract.  Each provider is responsible for exactly one
[ContextCategory] of signals and must not throw — it returns an empty list
when data is unavailable.

#### `ContextCaptureEngine` (`lib/shared/capture/context_capture_manager.dart`)

Central orchestrator.  Maintains a registry of [ContextProvider] instances,
drives the capture cycle, and stores the latest [ContextCaptureSnapshot].

Key operations:
- `initialize()` — initialise all registered providers
- `registerProvider(provider)` — add a provider to the registry at runtime
- `capture()` — run a full capture cycle; returns and caches the snapshot
- `latestSnapshot` — synchronous access to the most recent snapshot
- `dispose()` — release all provider resources

### Built-in Providers

#### `TimeContextProvider` (`lib/shared/capture/impl/time_context_provider.dart`)

Requires no permissions and is always available.  Captures:
`time.iso8601`, `time.hour_of_day`, `time.minute`, `time.weekday`,
`time.day_of_month`, `time.month`, `time.year`, `time.is_weekend`.

#### `NoopContextProvider` (`lib/shared/capture/impl/noop_context_provider.dart`)

Safe placeholder for development, tests, or unimplemented provider slots.
Always available; always returns an empty signal list.

### Planned Providers

| Provider | Category | Notes |
|---|---|---|
| `WeatherContextProvider` | `weather` | Requires location permission |
| `DeviceContextProvider` | `device` | Battery, network, orientation |
| `LocationContextProvider` | `location` | Wraps Location Engine; requires consent |
| `HealthContextProvider` | `health` | Heart rate, steps; requires health permission |
| `CalendarContextProvider` | `calendar` | Next event; requires calendar permission |

### Riverpod Providers (`lib/shared/providers/capture_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `contextCaptureEngineProvider` | `ContextCaptureEngine` | App-wide engine instance |

### Barrel Export (`lib/shared/capture/context_capture_engine.dart`)

Import the barrel for convenient access to the full Context Capture Engine API:

```dart
import 'package:egohygiene/shared/capture/context_capture_engine.dart';
```

---

## Memory Engine

### Overview

The Memory Engine provides long-term memory architecture for Ego Hygiene.
Conversation history is **transient**; memory represents **durable understanding**
accumulated over the user's journey.

The Memory Engine is a primary consumer of the Context Assembly Engine and is
designed to feed into the Knowledge Graph.

### Architecture

```
MemoryManager                    — orchestrator; single entry point for features
  ├── MemoryStore                — persistence abstraction (pluggable)
  │     └── InMemoryMemoryStore — default transient implementation
  └── MemorySource (0..*)       — extraction provider interface (pluggable)
        └── (future: LLM, reflection, therapist, Knowledge Graph)
```

All files live in `lib/shared/memory/`.

### Core Types

#### `MemoryType` (`lib/shared/memory/memory_type.dart`)

Enum that classifies memories into five cognitive categories:

| Type | Description |
|---|---|
| `episodic` | Records of specific past events or experiences |
| `semantic` | General facts, beliefs, or knowledge about the world or self |
| `preference` | Stated or inferred user preferences |
| `journey` | Milestones, phases, or narrative arcs in the user's personal journey |
| `relationship` | Information about persons, groups, or entities significant to the user |

#### `Memory` (`lib/shared/memory/memory.dart`)

The core domain entity. Immutable value object — use `copyWith` to produce
updated versions.

Key fields:
- `id` — stable opaque identifier (UUID recommended)
- `type` — [MemoryType] classification
- `content` — textual body of the memory
- `source` — origin label (e.g. `'reflection'`, `'conversation'`)
- `tags` — arbitrary labels for filtering and retrieval
- `confidence` — normalized weight in `[0.0, 1.0]`
- `metadata` — extensible key-value bag for future integrations

#### `MemoryStore` (`lib/shared/memory/memory_store.dart`)

Persistence contract for [Memory] entities. Abstracts the underlying storage
backend so [MemoryManager] stays decoupled from platform specifics.

Methods:
- `findById(id)` — look up a single memory
- `findAll()` — return all memories (ordered by `createdAt` ascending)
- `findByType(type)` — filter by [MemoryType]
- `findByTag(tag)` — filter by tag
- `findBySource(source)` — filter by origin
- `save(memory)` — upsert a memory
- `saveAll(memories)` — batch upsert
- `deleteById(id)` — remove a memory
- `clear()` — remove all memories
- `count()` — total count

#### `MemorySource` (`lib/shared/memory/memory_source.dart`)

Abstraction for external providers that contribute memories. Any component
that can extract durable understanding from a context map implements this
interface.

Lifecycle:
```
Application
  → MemoryManager.initialize()
    → MemorySource.initialize()

Trigger (e.g. session end, user request)
  → MemoryManager.consolidate(context)
    → MemorySource.extractMemories(context)
      → [Memory, ...]
        → MemoryStore.save(memory)
```

#### `MemorySnapshot` (`lib/shared/memory/memory_snapshot.dart`)

An immutable point-in-time view of a set of memories. Safe to pass to AI
context assembly, therapist portals, or serialization pipelines without risk
of the underlying store mutating.

Utility accessors:
- `ofType(type)` — filter by MemoryType
- `withTag(tag)` — filter by tag
- `fromSource(source)` — filter by origin
- `byConfidence` — sorted highest-confidence first
- `byRecency` — sorted most-recently-updated first

#### `MemoryManager` (`lib/shared/memory/memory_manager.dart`)

The single entry point for feature modules. Coordinates between [MemoryStore]
(persistence) and zero or more [MemorySource] instances (extraction).

Key operations:
- `remember(memory)` — persist a known memory
- `rememberAll(memories)` — batch persist
- `forget(id)` — remove a memory
- `forgetAll()` — remove all memories
- `consolidate(context)` — extract memories from all registered sources
- `recall()` — retrieve all memories
- `recallByType(type)` — filtered retrieval
- `recallByTag(tag)` — filtered retrieval
- `recallBySource(source)` — filtered retrieval
- `recallById(id)` — single lookup
- `snapshot()` — immutable point-in-time view
- `registerSource(source)` — add an extraction provider at runtime

### Separation from Conversation History

| Concern | Owner | Lifetime |
|---|---|---|
| Conversation turns | `ConversationScreen` / conversation feature | Session |
| Long-term memory | `MemoryManager` | Permanent (user journey) |

Feature modules must never store durable memories directly in conversation
state. Invoke `MemoryManager.consolidate` or `MemoryManager.remember` at
the appropriate lifecycle boundary (e.g. session end, reflection saved).

### Riverpod Providers (`lib/shared/providers/memory_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `memoryStoreProvider` | `MemoryStore` | Active persistence backend |
| `memoryManagerProvider` | `MemoryManager` | Feature-facing orchestrator |

### Barrel Export (`lib/shared/memory/memory_engine.dart`)

Import the barrel for convenient access to the full Memory Engine API:

```dart
import 'package:egohygiene/shared/memory/memory_engine.dart';
```

### Future Compatibility

The Memory Engine is designed to support:

- **Vector databases** — swap `memoryStoreProvider` with a vector-backed store
- **Embeddings** — generate and attach embeddings via a `MemorySource` adapter
- **Semantic retrieval** — implement `MemoryStore.findSimilar` in a vector store
- **Knowledge Graph integration** — wire a KG source via `MemorySource`
- **Therapist synchronization** — wire a therapist portal via `MemorySource`
- **Local-first AI memory** — on-device LLM extraction via `MemorySource`
- **Snapshot diffing** — compare two `MemorySnapshot` instances for changes
- **Confidence decay** — schedule background jobs to reduce confidence on stale memories

---

## Knowledge Graph Engine

### Overview

The Knowledge Graph Engine is the canonical relationship engine for the
application.  It is **not** a visualization: it is the graph itself — a typed,
directed network of entities and the semantic edges that connect them.

The engine models the web of meaning that underlies the user's journey:
practices that strengthen domains, reflections that generate insights, goals
that belong to domains, memories that inform research, and more.

### Architecture

```
GraphManager               — orchestrator; single entry point for feature modules
  └── GraphStore           — persistence abstraction (pluggable backend)
        └── InMemoryGraphStore  — default transient implementation

GraphNode                  — core vertex entity (domain, practice, reflection, …)
GraphNodeType              — domain role enum (7 types)
GraphRelationship          — core directed-edge entity
GraphRelationshipType      — semantic edge type enum (10 types)
GraphSnapshot              — immutable point-in-time view
```

All files live in `lib/shared/graph/`.

### Core Types

#### `GraphNodeType` (`lib/shared/graph/graph_node_type.dart`)

Enumerates the domain roles a node can represent:

| Value | Description |
|---|---|
| `domain` | A life domain (e.g. physical health, mental health) |
| `practice` | A repeatable behaviour or ritual |
| `reflection` | A free-form journal or reflection entry |
| `insight` | An observation or pattern surfaced by the Insight Engine |
| `goal` | A declared intention or desired outcome |
| `research` | A piece of external or curated knowledge |
| `memory` | A durable unit of understanding from the Memory Engine |

#### `GraphNode` (`lib/shared/graph/graph_node.dart`)

The core vertex entity.  Each node carries:
- `id` — stable opaque identifier matching the underlying entity's own ID.
- `type` — the [GraphNodeType] role.
- `label` — a short human-readable display name.
- `tags` — arbitrary labels for filtering and retrieval.
- `properties` — extensible key-value bag (future: embeddings, annotations).
- `createdAt`, `updatedAt` — temporal metadata.

#### `GraphRelationshipType` (`lib/shared/graph/graph_relationship_type.dart`)

Enumerates the semantic nature of directed edges:

| Value | Direction semantics |
|---|---|
| `relatesTo` | Generic association |
| `supports` | Source provides evidence/reinforcement for target |
| `contradicts` | Source is at tension with target |
| `derivesFrom` | Source is built upon target |
| `influences` | Source exerts an effect on target over time |
| `achieves` | Source practice/goal is directed toward target goal |
| `tracks` | Source monitors or measures target domain |
| `belongsTo` | Source is categorised under target domain |
| `generated` | Source triggered or produced target entity |
| `informs` | Source is cited in or referenced by target |

#### `GraphRelationship` (`lib/shared/graph/graph_relationship.dart`)

The core directed-edge entity.  Each relationship carries:
- `id` — stable opaque identifier (UUID recommended).
- `sourceId` — the node from which the edge originates.
- `targetId` — the node the edge points to.
- `type` — the semantic nature of the connection.
- `weight` — optional normalized strength `[0.0, 1.0]`.
- `properties` — extensible key-value bag (future: AI confidence, annotations).
- `createdAt` — when this relationship was recorded.

Many-to-many relationships are expressed by creating multiple
`GraphRelationship` entries sharing any combination of source and target nodes.

#### `GraphStore` (`lib/shared/graph/graph_store.dart`)

Persistence contract for both nodes and relationships.

Key operations:
- `saveNode(node)` / `findNodeById(id)` / `findNodesByType(type)` / `deleteNode(id)` — node CRUD
- `saveRelationship(rel)` / `findRelationshipById(id)` / `deleteRelationship(id)` — relationship CRUD
- `findRelationshipsBySource(id)` / `findRelationshipsByTarget(id)` — directed adjacency
- `findRelationshipsByNode(id)` — full adjacency (both directions)
- `clearNodes()` / `clearRelationships()` — bulk removal

Calling `deleteNode(id)` cascades to remove all relationships where that node
appears as source or target.

#### `InMemoryGraphStore` (`lib/shared/graph/impl/in_memory_graph_store.dart`)

Transient implementation backed by in-process maps.  Intended for tests and
initial development.  Swap in a persistent backend via `graphStoreProvider`.

#### `GraphManager` (`lib/shared/graph/graph_manager.dart`)

The single entry point for feature modules.  Coordinates the `GraphStore` and
exposes the full lifecycle of nodes and relationships.

Key operations:
- `addNode(node)` — register or replace a vertex
- `connect(id, sourceId, targetId, type, …)` — create a directed edge
- `neighborsOf(nodeId)` — adjacent nodes in either direction
- `relationshipsOf(nodeId)` — all edges touching a node
- `outgoing(sourceId)` / `incoming(targetId)` — directed adjacency queries
- `nodesByType(type)` / `nodesByTag(tag)` — filtered node queries
- `relationshipsByType(type)` — filtered relationship queries
- `snapshot()` — immutable `GraphSnapshot`

#### `GraphSnapshot` (`lib/shared/graph/graph_manager.dart`)

Immutable point-in-time view of the entire graph.  Safe to pass to AI context
assembly, visualization layers, or serialization pipelines.

- `nodesOfType(type)` — filter nodes by `GraphNodeType`
- `relationshipsOfType(type)` — filter relationships by `GraphRelationshipType`
- `nodeCount` / `relationshipCount` — size metrics
- `isEmpty` / `isNotEmpty`

### Riverpod Providers (`lib/shared/providers/graph_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `graphStoreProvider` | `GraphStore` | Active persistence backend |
| `graphManagerProvider` | `GraphManager` | Feature-facing orchestrator |

### Barrel Export (`lib/shared/graph/graph_engine.dart`)

Import the barrel for convenient access to the full Knowledge Graph Engine API:

```dart
import 'package:egohygiene/shared/graph/graph_engine.dart';
```

### Future Compatibility

The Knowledge Graph Engine is designed to support:

- **Visualization** — consume `GraphSnapshot` nodes and relationships to render
  force-directed or radial graph views.
- **AI reasoning** — traverse the graph using `neighborsOf` and
  `relationshipsOf` to build rich context for LLM prompts.
- **Therapist dashboard** — surface named relationships between entities to
  guide clinical review.
- **Semantic search** — index `GraphNode.properties` with embedding vectors for
  similarity-based graph traversal.
- **Persistent backends** — swap `graphStoreProvider` for a local database or
  graph database implementation without changing any manager or feature code.
- **Context Assembly integration** — wire a `GraphContextSource` that feeds
  relevant graph neighborhoods into the Context Assembly Engine via the
  `'graph.*'` namespace.
