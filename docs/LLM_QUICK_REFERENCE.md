# LLM Integration Quick Reference

## Config-Driven LLM Usage

### Simple Scraper (No LLM)

```yaml
source: simple_site
mode:
  extract_engine: "classic"
  pdf_to_table: "none"
llm:
  enabled: false
```

**Result**: Zero LLM calls, zero cost, zero latency.

---

### PDF-Heavy Scraper (LLM for PDFs Only)

```yaml
source: pdf_site
mode:
  extract_engine: "classic"      # HTML parsing stays classic
  pdf_to_table: "llm"           # PDFs use LLM
llm:
  enabled: true
  provider: "openai"
  model: "gpt-4o-mini"
  pdf:
    chunk_size_chars: 6000
    overlap_chars: 500
table_schema:
  price_list:
    - drug_name
    - strength
    - pack
    - mrp
    - manufacturer
```

**Result**: Classic HTML parsing, LLM for PDF table extraction.

---

### Hybrid Mode (Classic First, LLM Fallback)

```yaml
source: hybrid_site
mode:
  extract_engine: "classic"
  pdf_to_table: "hybrid"        # Try classic, fallback to LLM
llm:
  enabled: true
  provider: "deepseek"
  model: "deepseek-chat"
```

**Result**: Classic extraction first, LLM only if quality < threshold.

---

### Full LLM Pipeline (Normalization + QC)

```yaml
source: complex_site
mode:
  extract_engine: "classic"
  pdf_to_table: "llm"
llm:
  enabled: true
  provider: "openai"
  model: "gpt-4o-mini"
  normalize_fields:
    - manufacturer
    - drug_name
    - pack_size
  field_types:
    manufacturer: "company_name"
    drug_name: "drug_name"
  qc_enabled: true
```

**Result**: Classic extraction, LLM normalization, LLM QC.

---

## Code Usage

### Check if LLM Should Be Used

```python
from src.processors.llm.utils import should_use_llm_for_stage
from src.common.config_loader import load_source_config

config = load_source_config("alfabeta")

if should_use_llm_for_stage(config, "pdf_to_table"):
    # Use LLM for PDF table extraction
    pass
```

### Process PDFs with LLM

```python
from src.processors.pdf.pdf_fetcher import process_pdf_urls
from src.processors.pdf.pdf_text_extractor import process_pdf_extraction
from src.processors.pdf.pdf_table_llm import process_pdf_table_llm

# Fetch PDFs
records = list(process_pdf_urls(records_with_pdf_urls))

# Extract text
records = list(process_pdf_extraction(records))

# Extract tables with LLM
if should_use_llm_for_stage(config, "pdf_to_table"):
    records = list(process_pdf_table_llm(
        records,
        config,
        table_schema=config.get("table_schema", {}),
    ))
```

### Normalize with LLM

```python
from src.processors.llm.llm_normalizer import process_llm_normalization

if should_use_llm_for_stage(config, "normalize"):
    records = list(process_llm_normalization(
        records,
        config,
        fields_to_normalize=config.get("llm", {}).get("normalize_fields"),
    ))
```

### QC with LLM

```python
from src.processors.qc.llm_qc import process_llm_qc

if should_use_llm_for_stage(config, "qc"):
    records = list(process_llm_qc(
        records,
        config,
        required_fields=config.get("quality", {}).get("required_fields"),
    ))
```

---

## Cost Optimization Tips

1. **Disable LLM for simple scrapers**: `llm.enabled: false`
2. **Use hybrid mode**: `pdf_to_table: "hybrid"` - only pay when needed
3. **Reduce chunk sizes**: Lower `chunk_size_chars` = fewer tokens
4. **Use cheaper models**: `gpt-4o-mini` vs `gpt-4`
5. **Cache results**: Normalize same values once, reuse

---

## Environment Variables

```bash
# Required for LLM
OPENAI_API_KEY=sk-...
# OR
DEEPSEEK_API_KEY=sk-...
```

---

## Decision Tree

```
Is LLM enabled? → NO → Use classic only
                ↓ YES
What mode?
  - "none" → Classic only
  - "classic" → Classic only
  - "llm" → LLM only
  - "hybrid" → Try classic, fallback to LLM
```

