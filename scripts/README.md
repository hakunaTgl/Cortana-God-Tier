# Scripts Directory

This directory contains automation scripts used by GitHub Actions workflows for the Cortana-God-Tier project.

## Scripts Overview

### Model Optimization Scripts

#### `auto_quantize_models.py`
Automatically quantizes AI models to reduce memory usage.
- **Used by**: `model-optimization.yml` workflow
- **Purpose**: Analyzes and reports on model quantization methods (INT8, INT4, FP16)
- **Features**:
  - Supports multiple quantization methods
  - Estimates size reduction for models
  - Leverages `cortana.core.quantization.ModelQuantizer`

#### `prune_models.py`
Prunes AI models to reduce size and improve performance.
- **Used by**: `model-optimization.yml` workflow
- **Purpose**: Analyzes model pruning strategies
- **Features**:
  - Magnitude-based pruning
  - Structured pruning
  - Unstructured pruning

### Performance Monitoring Scripts

#### `detect_performance_anomalies.py`
Detects performance anomalies in the system.
- **Used by**: `performance-monitor.yml` workflow
- **Purpose**: Monitors system resources and detects anomalies
- **Monitors**:
  - CPU usage (warns if > 80%)
  - Memory usage (warns if > 80%)
  - Disk usage (warns if > 90%)

#### `analyze_memory_usage.py`
Analyzes memory usage of the system and applications.
- **Used by**: `performance-monitor.yml`, `daily-health-check.yml` workflows
- **Purpose**: Provides detailed memory usage analysis
- **Reports**:
  - System memory statistics
  - Swap memory statistics
  - Top memory-consuming processes

### Learning & Synchronization Scripts

#### `process_feedback_logs.py`
Processes user feedback and learning logs to improve the system.
- **Used by**: `learning-update.yml` workflow
- **Purpose**: Analyzes feedback logs and updates learning models
- **Features**:
  - Processes feedback from multiple sources
  - Analyzes feedback patterns
  - Updates learning models

#### `sync_shared_code.py`
Synchronizes shared code across multiple repositories.
- **Used by**: `sync-all-repos.yml` workflow
- **Purpose**: Keeps shared code modules in sync
- **Features**:
  - Checks shared modules
  - Synchronizes code
  - Validates synchronization

## Usage

All scripts can be run directly from the repository root:

```bash
# Example: Run auto-quantization
python scripts/auto_quantize_models.py

# Example: Check performance anomalies
python scripts/detect_performance_anomalies.py
```

## Dependencies

Scripts use the following dependencies:
- `torch` - For model quantization
- `psutil` - For system resource monitoring
- Custom modules from `cortana.core` and `cortana.utils`

All dependencies are listed in `requirements.txt`.

## Exit Codes

All scripts follow standard exit code conventions:
- `0` - Success
- `1` - Error occurred

## Logging

Scripts use Python's `logging` module with the following format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Logs are output to stdout and can be captured by workflow runners.
