# LLM Integration Guide

This document describes the config-driven LLM integration system for the scraper platform.

## Overview

The platform supports **optional LLM integration** that allows scrapers to:
- Use LLM for complex tasks (PDF table extraction, normalization, QC)
- Stay LLM-free for simple scrapers (no cost, no latency)
- Use hybrid mode (classic first, LLM fallback)

## Architecture

```
SCRAPER → BASIC_PARSE → (optional) PDF_FETCH → (optional) PDF_PARSE_CLASSIC 
         → (optional) LLM_TABLE_EXTRACT → (optional) LLM_NORMALIZE 
         → (optional) LLM_QC → QC → EXPORT
```

**Key Principle**: LLM is just another processor, not the default.

## Configuration

### Source Config Structure

Each source config (`config/sources/<source>.yaml`) can include:

```yaml
source: alfabeta

mode:
  extract_engine: "classic"      # classic | llm | hybrid
  pdf_to_table: "none"           # none | classic | llm | hybrid

llm:
  enabled: true                  # Master switch
  provider: "openai"             # openai | deepseek | anthropic
  model: "gpt-4o-mini"
  max_tokens: 2048
  temperature: 0.0
  base_url: null                 # Optional custom API base URL
  
  pdf:
    chunk_size_chars: 6000
    overlap_chars: 500
  
  normalize_fields: []           # Fields to normalize with LLM
  field_types:                   # Field type hints
    manufacturer: "company_name"
    drug_name: "drug_name"
  
  qc_enabled: false              # Enable LLM-based QC

table_type: "price_list"         # Type of table to extract
table_schema:
  price_list:
    - drug_name
    - strength
    - pack
    - mrp
    - manufacturer
```

### Example Configs

**Simple Site (No LLM):**
```yaml
source: simple_site
mode:
  extract_engine: "classic"
  pdf_to_table: "none"
llm:
  enabled: false
```

**PDF-Heavy Site (LLM for PDFs):**
```yaml
source: complex_pdf_site
mode:
  extract_engine: "classic"
  pdf_to_table: "llm"
llm:
  enabled: true
  provider: "openai"
  model: "gpt-4o-mini"
  pdf:
    chunk_size_chars: 6000
    overlap_chars: 500
```

**Hybrid Mode (Classic First, LLM Fallback):**
```yaml
source: hybrid_site
mode:
  extract_engine: "classic"
  pdf_to_table: "hybrid"
llm:
  enabled: true
  provider: "deepseek"
  model: "deepseek-chat"
```

## Components

### 1. LLM Client (`src/processors/llm/llm_client.py`)

Unified client supporting multiple providers:
- OpenAI (GPT-4, GPT-4o-mini)
- DeepSeek (OpenAI-compatible)
- Groq (Llama 3.x, Mixtral, Compound models — no OpenAI account required)
- Anthropic (Claude) - planned

**Usage:**
```python
from src.processors.llm.llm_client import get_llm_client_from_config

llm_client = get_llm_client_from_config(source_config)
if llm_client:
    result = llm_client.complete("Extract product name from: ...")
```

### 2. PDF Processors

**PDF Fetcher** (`src/processors/pdf/pdf_fetcher.py`):
- Downloads PDFs from URLs
- Stores locally with unique IDs
- Handles caching

**PDF Text Extractor** (`src/processors/pdf/pdf_text_extractor.py`):
- Extracts text using PyMuPDF or pdfplumber
- Detects basic tables
- Chunks text for LLM processing

**PDF Table LLM** (`src/processors/pdf/pdf_table_llm.py`):
- Uses LLM to extract structured tables from PDF text
- Supports chunking for large PDFs
- Returns structured JSON

### 3. LLM Normalizer (`src/processors/llm/llm_normalizer.py`)

Normalizes ambiguous fields:
- Product names
- Manufacturer names
- Pack sizes
- Dosage information

### 4. LLM QC (`src/processors/qc/llm_qc.py`)

AI-powered quality control:
- Validates record completeness
- Detects anomalies
- Scores record quality

### 5. Hybrid Mode (`src/processors/hybrid_mode.py`)

Implements classic-first, LLM-fallback strategy:
- Tries classic extraction first
- Scores quality
- Falls back to LLM if quality < threshold

## Usage in Pipelines

### DSL Pipeline Example

```yaml
pipeline:
  name: alfabeta_llm
  steps:
    - component: alfabeta.fetch_pdf_links
    
    # PDF processing (conditional)
    - component: pdf.fetcher
      condition: "${config.mode.pdf_to_table != 'none'}"
    
    - component: pdf.text_extractor
      condition: "${config.mode.pdf_to_table != 'none'}"
    
    # LLM extraction (conditional)
    - component: pdf.table_llm
      condition: "${config.mode.pdf_to_table in ['llm', 'hybrid']}"
    
    # LLM normalization (conditional)
    - component: llm.normalizer
      condition: "${config.llm.enabled && config.llm.normalize_fields}"
    
    # Standard QC (always runs)
    - component: processors.qc_rules
```

### Programmatic Usage

```python
from src.processors.pdf.pdf_fetcher import process_pdf_urls
from src.processors.pdf.pdf_table_llm import process_pdf_table_llm
from src.processors.llm.llm_normalizer import process_llm_normalization
from src.common.config_loader import load_source_config

# Load config
source_config = load_source_config("alfabeta")

# Process PDFs
records = process_pdf_urls(records_with_pdf_urls)

# Extract text
from src.processors.pdf.pdf_text_extractor import process_pdf_extraction
records = process_pdf_extraction(records)

# Extract tables with LLM (if enabled)
if source_config.get("mode", {}).get("pdf_to_table") in ("llm", "hybrid"):
    records = process_pdf_table_llm(
        records,
        source_config,
        table_schema=source_config.get("table_schema", {}),
    )

# Normalize with LLM (if enabled)
if source_config.get("llm", {}).get("normalize_fields"):
    records = process_llm_normalization(records, source_config)
```

## Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# Groq
GROQ_API_KEY=gsk-your-key-here

# Anthropic (future)
ANTHROPIC_API_KEY=sk-...
```

## Cost Management

### Strategies

1. **Disable LLM for simple scrapers**: Set `llm.enabled: false`
2. **Use hybrid mode**: Try classic first, only use LLM when needed
3. **Chunk PDFs**: Process large PDFs in chunks to control token usage
4. **Cache results**: Cache LLM normalization results for repeated values
5. **Batch processing**: Process multiple records in single LLM call when possible

### Monitoring

Track LLM usage:
- Token counts per run
- Cost per record
- LLM vs classic success rates

## Best Practices

1. **Start with classic**: Always try regex/XPath first
2. **Use hybrid mode**: Best of both worlds
3. **Configure carefully**: Only enable LLM where it adds value
4. **Monitor costs**: Track LLM usage and costs
5. **Test thoroughly**: Validate LLM output quality
6. **Fallback gracefully**: Always have classic fallback

## Troubleshooting

### LLM Not Working

- Check `llm.enabled: true` in config
- Verify API key in environment
- Check provider/model name
- Review logs for errors

### High Costs

- Disable LLM for simple scrapers
- Use hybrid mode instead of LLM-only
- Reduce chunk sizes
- Cache normalization results

### Poor Quality

- Adjust temperature (lower = more deterministic)
- Improve prompts
- Add examples to prompts
- Use better models (GPT-4 vs GPT-4o-mini)

## Future Enhancements

- [ ] Batch processing for normalization
- [ ] Caching layer for LLM results
- [ ] Cost tracking and alerts
- [ ] Automatic prompt optimization
- [ ] Multi-model fallback (try cheaper model first)
- [ ] Fine-tuned models for specific domains

