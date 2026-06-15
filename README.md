# Cortana-God-Tier

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Phase 1: Complete](https://img.shields.io/badge/Phase%201-Complete-brightgreen.svg)](#roadmap)
[![Architecture: Modular](https://img.shields.io/badge/Architecture-Modular%20Skills-blueviolet.svg)](#architecture)
[![Privacy: First Class](https://img.shields.io/badge/Privacy-First%20Class-blue.svg)](#privacy)

> Advanced AI Personal Assistant with Automated Intelligence Pipeline. Memory-optimized, privacy-first, multi-platform system with automatic research, security monitoring, and continuous optimization. Built on a modular, event-driven skills architecture.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Core Skills](#core-skills)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Privacy Design](#privacy-design)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Modular Skills System** | Hot-reloadable, self-contained skill modules with standardized interfaces |
| **Event Bus Architecture** | Async pub/sub event system for fully decoupled skill communication |
| **Automatic Research** | Web research skill with multi-source aggregation and summarization |
| **Code Assistance** | Code generation, review, debugging, and explanation capabilities |
| **Persistent Memory** | Long-term memory storage with semantic search (strictly local) |
| **System Monitoring** | Security scanning, performance metrics, and health checks |
| **Privacy-First Design** | Skills declare privacy levels; sensitive operations never leave local machine |
| **Backward Compatible** | Original CLI interface preserved through all architectural upgrades |
| **27-Test Suite** | Comprehensive tests covering all components and skill lifecycle states |
| **Docker Support** | Production-ready Dockerfile for containerized deployment |

---

## Architecture

Cortana-God-Tier uses a **modular, event-driven architecture** built around a central Skills Manager:

```
+--------------------------------------------------+
|              Cortana Assistant (CLI)             |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|              Skills Manager                      |
|  (Orchestration, Hot-Reload, Capability Routing) |
+------+----------+------------+---------+---------+
       |          |            |         |
+------+--+  +---+-----+  +---+---+  +--+-----+
|Research |  |  Code   |  |Memory |  | System |
| Skill   |  |  Skill  |  | Skill |  |  Skill |
+---------+  +---------+  +-------+  +--------+
                        |
+--------------------------------------------------+
|              Async Event Bus                     |
|        (Pub/Sub, Priority Levels)                |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|          External APIs / Local Storage           |
+--------------------------------------------------+
```

### Skill Lifecycle
```
UNINITIALIZED -> INITIALIZING -> READY <-> BUSY -> ERROR/DISABLED
```

---

## Core Skills

### Research Skill
- Multi-source web research with automatic summarization
- Caches results to minimize redundant API calls
- Privacy level: **cloud** (uses external APIs)

### Code Skill
- Code generation, explanation, review, and debugging
- Supports multiple programming languages
- Privacy level: **cloud** (LLM-assisted)

### Memory Skill
- Persistent long-term memory with semantic search
- Stores user preferences, facts, and interaction history
- Privacy level: **local** (never leaves your machine)

### System Skill
- System health monitoring and diagnostics
- Security scanning and performance metrics
- Process and resource management
- Privacy level: **local** (operates entirely offline)

---

## Quick Start

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)
- API keys for cloud features (OpenAI, search providers)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/hakunaTgl/Cortana-God-Tier.git
cd Cortana-God-Tier

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run the assistant
python -m cortana
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t cortana-god-tier .
docker run -it --env-file .env cortana-god-tier
```

### Running Tests

```bash
# Run all 27 tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=cortana --cov-report=html
```

---

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
assistant:
  name: Cortana
  memory_limit: 1000
  research_cache_ttl: 3600

skills:
  research:
    enabled: true
    privacy_level: cloud
  code:
    enabled: true
    privacy_level: cloud
  memory:
    enabled: true
    privacy_level: local
  system:
    enabled: true
    privacy_level: local

privacy:
  default_level: local
  allow_cloud: true   # Set to false to disable all cloud features
```

---

## Project Structure

```
Cortana-God-Tier/
|-- cortana/
|   |-- __init__.py         # Package init
|   |-- api/                # External API integrations
|   |-- core/               # Core assistant logic & event bus
|   |-- skills/             # Modular skills (research, code, memory, system)
|   `-- utils/              # Input validation & sanitization utilities
|-- scripts/                # Automation and utility scripts
|-- tests/                  # 27-test suite covering all components
|-- public/                 # Web demo UI
|-- Dockerfile              # Production container definition
|-- config.yaml             # Main configuration file
|-- PHASE1_FINAL_SUMMARY.md # Phase 1 implementation summary
|-- PHASE1_IMPLEMENTATION.md# Technical implementation details
|-- PHASE1_SUCCESS.md       # Phase 1 verification & success criteria
`-- LICENSE
```

---

## Privacy Design

Privacy is enforced at the skill level:

| Skill | Privacy Level | Description |
|---|---|---|
| Memory | **local** | All data stored locally, never transmitted |
| System | **local** | Operates entirely offline |
| Research | **cloud** | Uses external APIs (opt-in) |
| Code | **cloud** | LLM-assisted (opt-in) |

- Skills explicitly declare their privacy level in their manifest
- Users can disable all cloud features with a single config flag
- No telemetry, no analytics, no data collection

---

## Roadmap

- [x] Phase 1: Modular Foundation - Skills-Based Architecture (COMPLETE)
  - [x] Event Bus System (async pub/sub)
  - [x] Base Skill Framework & Skills Manager
  - [x] Four Core Skills (Research, Code, Memory, System)
  - [x] 27-test comprehensive test suite
- [ ] Phase 2: Intelligence Pipeline
  - [ ] Automated research scheduling
  - [ ] Cross-skill memory integration
  - [ ] Natural language command parsing upgrade
- [ ] Phase 3: Multi-Platform Support
  - [ ] Telegram integration
  - [ ] Web dashboard
  - [ ] Voice interface
- [ ] Phase 4: Continuous Optimization
  - [ ] Self-benchmarking and performance tuning
  - [ ] Automated security audits

---

## Contributing

Contributions are welcome! To add a new skill:

1. Fork the repository
2. Create a new skill class extending `BaseSkill` in `cortana/skills/`
3. Register your skill in `config.yaml`
4. Add tests in `tests/`
5. Submit a Pull Request

See the [CONTRIBUTING guide](.github/CONTRIBUTING.md) and `PHASE1_IMPLEMENTATION.md` for architecture guidance.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Built with passion by <a href="https://github.com/hakunaTgl">hakunaTgl (Tylor Fenwick)</a> - <a href="https://hakunatgl.github.io">Portfolio</a></p>
