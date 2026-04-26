# Physical Agent Operating System: A Decoupled Protocol-Based Framework for Self-Evolving and Cross-Embodiment Agents

**Chinese version**: [Report.md](Report.md)

> **Version**: 0.1.0-Release | **Release Date**: 2026-03-20

---

## Abstract

As large language models (LLMs) achieve qualitative breakthroughs in agentic capabilities, the field of Embodied AI is facing a critical divergence in technical approaches. Traditional end-to-end Vision-Language-Action (VLA) models, while demonstrating the potential for end-to-end optimization, suffer from fundamental bottlenecks: lack of interpretability, difficulty in local debugging, and limited cross-embodiment generalization. VLA models are often criticized for relying on "visual-motor priors" rather than truly following language instructions, and they lack principled diagnostic mechanisms when failures occur.

To address these challenges, we propose **Physical Agent Operating System (PhyAgentOS)**, a self-evolving embodied AI framework based on agentic workflows. By introducing a "Cognitive-Physical Decoupling" architectural paradigm, PhyAgentOS achieves standardized mapping from high-reasoning cloud models to edge physical execution layers. Instead of pursuing end-to-end neural network optimization, the framework constructs a Language-Action Interface that completely decouples action representation from embodiment morphology.

Built on an ultra-lightweight `nanobot` runtime environment, PhyAgentOS defines structured protocol layers including `TASK`, `SKILL`, `ACTION`, `ENVIRONMENT`, and `EMBODIED`. The architecture natively supports zero-code migration across hardware platforms, sandbox-driven code tool self-generation, and safety correction mechanisms based on Multi-Agent Critic verification. Furthermore, PhyAgentOS constructs a unified Hardware Abstraction Layer (HAL) through the `BaseDriver` interface and dynamic loading mechanisms, enabling seamless support for heterogeneous robot embodiments such as manipulators, quadrupeds, and desktop pets.

Architecture analysis demonstrates that PhyAgentOS maintains LLM strong reasoning capabilities while achieving interpretability, cross-embodiment zero-shot transfer, and system-level safety guarantees that are difficult for the VLA paradigm to match.

---

## 1. Introduction

The core goal of embodied intelligence is to endow physical entities with perception, reasoning, and interaction capabilities with the real world. In recent years, VLA models trained on large-scale heterogeneous data have achieved end-to-end mapping from pixels to actions. However, the VLA paradigm exposes significant systemic risks in practical deployment:

1. **Uninterpretability and Debugging Difficulty**: Decision processes are implicitly distributed across neural network parameters. When robots exhibit unexpected behavior, operators lack controllable intervention and diagnostic interfaces.
2. **Execution Hallucination and Safety Risks**: In out-of-distribution (OOD) scenarios, the semantic gap between high-dimensional visual features and discrete control signals causes the planner to ignore physical visual evidence, leading to catastrophic physical collisions.
3. **Strong Embodiment Coupling**: Existing systems are typically deeply bound to the kinematic characteristics of specific robot embodiments. Even after multi-embodiment pre-training, deployment to novel hardware configurations still requires expensive data collection and fine-tuning.

Based on these challenges, this paper proposes: **In the era of strong-reasoning large models, the mapping of embodied control should be achieved through standardized structured protocols rather than implicit neural networks.** Inspired by recent cross-embodiment transfer research, the PhyAgentOS framework decomposes embodied tasks into hierarchical state files, with cloud agents playing the role of "cognitive core" to perceive and control the physical world by reading and writing standard protocols.

The main contributions of this paper are:
- A "Cognitive-Physical Decoupling" embodied intelligence architecture that solves cross-embodiment generalization by separating methodology (`SKILL`) from execution constraints (`ACTION`).
- An ultra-lightweight edge runtime framework based on `nanobot`, supporting efficient deployment and zero-code migration from microcontrollers (e.g., ESP32) to industrial PCs.
- A sandbox-driven code generation mechanism and Multi-Agent Critic validation pipeline, enabling tool self-evolution and real-time physical execution deviation correction.
- A unified Hardware Abstraction Layer (HAL) that enables seamless support for heterogeneous robot embodiments through the `BaseDriver` interface and dynamic loading.

---

## 2. Architecture: Cognitive-Physical Structural Decoupling

The core of the PhyAgentOS framework lies in establishing a clear boundary between cloud cognitive reasoning and edge physical execution. The system abandons direct API call chains in favor of a **Shared State Protocol Space**.

### 2.1 Dynamic Collaboration and Cognitive State Space

At runtime, the system maintains a set of structured text files representing global state. Cloud agents process these dimensionality-reduced symbolic representations, avoiding direct interference from low-level multimodal features:

- **`TASK.md` (Global Orchestration Protocol)**: Serves as the system's dynamic task blackboard (Blackboard Architecture). Used for DAG-level task decomposition of macro instructions and maintaining temporal dependencies between multiple agents or embodiments.
- **`ENVIRONMENT.md` (Environmental Perception Representation)**: Aggregation endpoint for VLM and sensor outputs. Reduces raw pixel streams to structured scene graphs containing topological relationships and 3D coordinates, solving the symbol grounding problem.
- **`EMBODIED.md` (Embodiment Declaration and Kinematic Constraints)**: Hardware abstraction layer interface exposed by edge hardware to the cloud. Statically records device degrees of freedom, communication protocols, SDK mapping relationships, and physical extremes (e.g., maximum load, workspace boundaries).

### 2.2 Logical Decoupling: `SKILL` and `ACTION`

To solve the problem of actions being tightly bound to specific hardware in embodied intelligence, PhyAgentOS splits the traditional notion of "skill" into two orthogonal dimensions:

- **`SKILL.md` (System-Level Workflow / Cognitive Methodology)**: Defines general state machines or operation pipelines for completing specific tasks, independent of specific physical parameters.
- **`ACTION.md` (Instantiated Physical Constraint Target)**: Represents specific physical execution parameters instantiated by `SKILL` under current `ENVIRONMENT` and current `EMBODIED` conditions.

### 2.3 Hardware Abstraction Layer (HAL) and Watchdog Mechanism

To support heterogeneous robot embodiments, PhyAgentOS introduces a unified Hardware Abstraction Layer (HAL). The cognitive layer (Track A, cloud LLM) and physical execution layer (Track B, edge hardware) are strictly physically isolated. The only bridge is the file-system-based state protocol space (Workspace API) and the **Hardware Watchdog Daemon**.

`hal_watchdog.py` responsibilities:
1. **Dynamic Driver Loading**: Loads the corresponding `BaseDriver` from the driver registry via CLI arguments.
2. **Physical Prior Knowledge Injection**: Copies the hardware `EMBODIED.md` into the shared workspace at startup.
3. **Asynchronous Command Polling**: Polls `ACTION.md` and executes via `driver.execute_action()`.
4. **Closed-Loop State Writeback**: Calls `driver.get_scene()` to update `ENVIRONMENT.md` and clears `ACTION.md`.

Advantages:
- **Extreme Robustness**: Cognitive and execution layer crashes do not affect each other.
- **Strict Temporal Decoupling**: File polling buffers the mismatch between LLM latency and real-time control.
- **Transparent Observability**: All state is inspectable as plain text Markdown/JSON.

---

## 3. Constraint-Based Embodied Control Paradigm

PhyAgentOS advocates a third path beyond end-to-end RL/IL and traditional trajectory planning: **Constraint-Based Embodied Control**.

### 3.1 Mapping Semantic Intent to Geometric Constraints

LLMs output semantic intent and geometric constraints rather than joint angles. For "empty the cup":
1. Semantic decomposition: "grasp cup", "move above container", "tilt cup"
2. Constraint generation: cup bottom Z > cup rim Z; cup rim within container opening; end-effector avoids table
3. Constraint dispatch: structured JSON written to `ACTION.md`

### 3.2 Edge-Side Real-Time Optimization

The constraint solver (e.g., QP optimizer) combines kinematics, dynamics limits, and sensor feedback to compute optimal joint trajectories in < 50ms.

### 3.3 Core Advantages

1. **True Cross-Embodiment Generalization**: Geometric constraints are body-agnostic.
2. **Robustness to Perturbations**: Real-time solver adapts without LLM re-reasoning.
3. **Interpretability and Safety**: Constraints are human-readable; hard constraints guarantee safety.

---

## 4. Cross-Embodiment Generalization and Ultra-Lightweight Edge Deployment

### 4.1 `nanobot` Edge Runtime

PhyAgentOS offloads heavy reasoning to cloud LLM APIs, leaving an ultra-lightweight local runtime. `nanobot` handles only network communication, protocol parsing, and hardware SDK routing — deployable from ESP32 microcontrollers to industrial PCs.

### 4.2 Zero-Code Transfer

Cross-embodiment transfer becomes a document-constraint-based reparameterization:
1. `nanobot` detects and uploads the new robot's `EMBODIED.md`
2. Cloud Agent updates physical priors
3. `SKILL.md` remains unchanged; `ACTION.md` is regenerated with new constraints

No top-level code changes are required.

---

## 5. Self-Evolution: Sandbox-Driven Tool Abstraction

### 5.1 Sandbox Evolution Pipeline

1. **Dynamic Generation**: Agent generates Python/C++ scripts in sandbox
2. **Simulation Validation**: Test in restricted environment or digital twin (e.g., PyBullet)
3. **Tool Standardization**: Verified scripts become MCP tools injected into the system
4. **Workflow Iteration**: Subsequent tasks invoke the tool directly via context

This forms a self-evolution loop: encounter anomaly -> generate test -> solidify tool -> expand capability.

---

## 6. Safety: Multi-Agent Verified Physical Correction

### 6.1 Planner-Critic Architecture

The independent **Critic Agent**:
- **State Strong Interception**: Highest read/write permissions for sensor state streams
- **Temporal Interruption**: Throws physical anomaly interrupt when Planner state mismatches sensor data
- **Action Legitimacy Validation**: Validates actions against `EMBODIED.md` before writing to `ACTION.md`

### 6.2 Long-Horizon Experience Solidification

Intercept logs and feedback are refined into semi-structured natural language and appended to `KNOWLEDGE.md` and `LESSONS.md`. In subsequent planning, the Agent is forced to retrieve these memories, eliminating repeated failures.

---

## 7. Semantic Navigation and Multimodal Perception Fusion

### 7.1 Semantic Navigation Tool

`SemanticNavigationTool` resolves high-level goals ("move to the kitchen table") into physical coordinates by reading the scene graph in `ENVIRONMENT.md`.

### 7.2 Multimodal Perception Pipeline

- **Geometry Pipeline**: Point cloud and odometry processing
- **Segmentation Pipeline**: Vision model semantic segmentation
- **Fusion Pipeline**: Combines geometry and semantics into unified scene graphs written to `ENVIRONMENT.md`

---

## 8. Conclusion

This paper proposes Physical Agent Operating System (PhyAgentOS), an innovative embodied architecture that overcomes VLA interpretability and generalization bottlenecks. By reducing complex robot control to structured document read/write operations through `nanobot` and a protocol matrix of `TASK`, `SKILL`, `ACTION`, and `ENVIRONMENT`, PhyAgentOS enables ultra-lightweight edge deployment, zero-code cross-embodiment transfer, Multi-Agent Critic safety validation, sandbox tool self-evolution, and unified HAL abstraction. PhyAgentOS offers a promising paradigm shift for building the next generation of de-embodiment, interpretable, and highly reusable general embodied intelligence foundations.
