# Case Study: OpenAI-Retro-SuperMarioWorld-SNES

**Repository:** [szmyty/OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES)
**Maturity:** Experiment — documented and reproducible
**Evidence ID:** `repo-openai-retro`

---

## Problem

Understanding how reinforcement learning agents learn from raw game-state input
requires a concrete, observable experiment. Training an agent on a well-known
game with a clear reward signal makes it possible to reason about emergent
behaviour, training stability, and the relationship between network architecture
and performance — without proprietary data or cloud compute requirements.

## Architectural Approach

The project uses the **NEAT-Python** library to evolve recurrent neural networks
that control a Super Mario World agent via **OpenAI gym-retro**:

- **gym-retro** provides the SNES game emulator and a Gym-compatible
  observation and action interface;
- **NEAT** (NeuroEvolution of Augmenting Topologies) evolves both the topology
  and weights of the network, avoiding gradient-based training;
- a **configuration file** controls population size, fitness thresholds, and
  mutation rates — making experiments reproducible and comparable.

The experiment is self-contained: a single Python entry point starts training,
periodically checkpoints the best genome, and can resume from a checkpoint.

Key architectural boundaries:

| Boundary | Decision |
|----------|----------|
| Algorithm choice | NEAT chosen to study emergent topology, not just weight optimisation |
| Reproducibility | Fixed random seed and configuration file enable identical reruns |
| Observability | Fitness scores and genome visualisations are logged per generation |

## Alan's Role and Key Decisions

- Configured the NEAT hyperparameters (population, elitism, mutation rates) to
  balance exploration and convergence for the Mario environment.
- Wrote the fitness function translating game progress to a scalar reward
  signal that incentivises forward movement without trivial solutions.
- Documented the training loop and results to make the experiment inspectable
  by other researchers.

## Current Usable Artifact

The repository contains the full training pipeline, NEAT configuration, and
result documentation. Anyone with Python and gym-retro installed can reproduce
the experiment.

**Evidence:** [github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES)

## Maturity and Next Direction

| Attribute | Status |
|-----------|--------|
| Maturity | Documented experiment; not intended for production use |
| Test coverage | Experiment is its own validation; results documented |
| Documentation | README with setup, training, and result sections |
| Next direction | Apply similar NEAT approach to a custom environment; explore parallelised training |
