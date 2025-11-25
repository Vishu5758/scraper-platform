# CI Integration for DeepAgent Auto-Repair

This document describes how to integrate DeepAgent auto-repair testing into CI/CD pipelines.

## Overview

DeepAgent features (auto-selector, auto-repair, LLM patch generation) should be tested in CI to ensure:
1. LLM features work correctly
2. Patch generation produces valid patches
3. Auto-repair doesn't break existing functionality

## Test Coverage

Tests are located in `tests/test_deepagent_llm.py`:
- ✅ LLM selector engine tests
- ✅ LLM patch generator tests
- ✅ DeepAgent repair engine integration tests
- ✅ Auto-extract integration tests

## CI Configuration

### GitHub Actions Example

```yaml
name: DeepAgent Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-deepagent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-mock
      
      - name: Run DeepAgent tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          pytest tests/test_deepagent_llm.py -v
      
      - name: Test auto-patch application (optional)
        run: |
          # Run repair session on test snapshots
          python -m src.agents.deepagent_repair_engine test_source
```

### GitLab CI Example

```yaml
test-deepagent:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-mock
  script:
    - pytest tests/test_deepagent_llm.py -v
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
```

## Auto-Patch Application in CI

To automatically apply and test patches in CI:

1. **Enable patch generation** in config:
   ```yaml
   llm:
     enabled: true
     auto_repair: true
   ```

2. **Run repair session**:
   ```bash
   python -m src.agents.deepagent_repair_engine <source>
   ```

3. **Validate patches**:
   - Check that patches are valid JSON/YAML
   - Run replay tests with new selectors
   - Verify no regressions

4. **Commit patches** (optional):
   ```bash
   git add src/scrapers/<source>/selectors.json
   git commit -m "Auto-repair: Updated selectors for <source>"
   ```

## Mock Testing

For CI environments without LLM API access, tests use mocks:
- `Mock(spec=LLMClient)` for LLM client
- Mock responses for selector extraction
- Mock patch generation

Real LLM tests should run in staging/production environments.

## Continuous Monitoring

Set up monitoring for:
- Patch generation success rate
- Selector repair accuracy
- Auto-repair triggered runs
- Cost of LLM calls for repair

## Next Steps

1. ✅ Tests created (`tests/test_deepagent_llm.py`)
2. ⚠️ Add to CI pipeline (environment-specific)
3. ⚠️ Set up monitoring/alerting
4. ⚠️ Document patch approval workflow

