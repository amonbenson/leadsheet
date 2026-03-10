# Leadsheet Architecture

## Overview

Leadsheet is a Python library that wraps LaTeX compilation for creating musical leadsheets. It ships a custom LaTeX document class (`leadsheet.cls`) and provides a Python CLI and API for compiling `.tex` files to PDF.

## Repository Layout

```
leadsheet/
├── leadsheet/                  # Python package
│   ├── __init__.py             # Public API exports
│   ├── __main__.py             # CLI entry point (python -m leadsheet)
│   ├── compiler.py             # Compilation engine
│   ├── converter.py            # PDF-to-PNG conversion (pymupdf)
│   └── latex/                  # LaTeX class files (bundled as package data)
│       ├── leadsheet.cls
│       ├── leadsheet-core.sty
│       ├── leadsheet-chords.sty
│       └── leadsheet-sections.sty
├── examples/                   # Example leadsheets
│   ├── maniac.tex
│   ├── maniac.pdf              # Built by `just build-examples`
│   └── maniac.png              # Built by `just build-examples`
├── tests/                      # Test suite
│   ├── conftest.py             # Shared fixtures and helpers
│   └── test_compiler.py        # Integration tests
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI (lint, typecheck, test)
├── pyproject.toml              # Project metadata, dependencies, tool config
└── justfile                    # Task runner commands
```

## Python Package

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `compiler.py` | Locate LaTeX class files, build environment, invoke latexmk, collect outputs |
| `converter.py` | Convert a compiled PDF to PNG using `pymupdf` |
| `__main__.py` | Parse CLI arguments (`--format`, `--engine`), call `compile_latex`, handle errors |
| `__init__.py` | Re-export public API: `compile_latex`, `CompilationError` |

### Compilation Flow

```
CLI / Python API
        │
        ▼
compile_latex(input_path, output_path, formats, engine, verbose)
        │
        ├── _find_latex_dir()          # Locate leadsheet/latex/ inside the package
        │
        ├── _build_env(latex_dir)      # Set TEXINPUTS so TeX finds class files
        │
        ├── _build_cmd(engine, ...)    # Assemble latexmk command
        │
        ├── subprocess.run(cmd, ...)   # Execute latexmk in a temp directory
        │
        ├── shutil.copy2(tmp_pdf, ...)     # Move PDF to requested location
        │
        └── pdf_to_png(pdf, png)  ──────── If "png" in formats
                │                          (converter.py, uses pymupdf/fitz)
                └── returns png path
```

### Error Handling

- `FileNotFoundError` — input file not found, or LaTeX class files not found
- `CompilationError` — latexmk exited with non-zero code; carries `.stdout` and `.stderr` for debugging

### LaTeX Class File Resolution

The LaTeX class files live in `leadsheet/latex/` — the single source of truth, both in the repository and in the installed wheel. Hatchling includes all files under the `leadsheet/` directory automatically, so no special `force-include` configuration is needed.

The `TEXINPUTS` environment variable is set at compilation time so `lualatex` finds `leadsheet.cls` regardless of the working directory.

## LaTeX Package

### File Organization and Dependencies

```
leadsheet.cls
    │
    ├─→ leadsheet-core.sty      (no internal deps)
    │       └─→ Provides: preprocessing engine, barline commands, layout utils
    │
    ├─→ leadsheet-chords.sty    (depends on core)
    │       └─→ Provides: chord parsing, chord formatting, progression storage
    │
    └─→ leadsheet-sections.sty  (depends on core + chords)
            └─→ Provides: lstabular, songsection, hlsongsection environments
```

### Data Flow: Processing a Song Section

```
User writes:    \begin{songsection}{Verse 1}
                    & ^Cm7 & ^F7 \\
                    <> Hello & world \\
                \end{songsection}
                        │
                        ▼
[leadsheet-sections.sty]  songsection captures body → lstabular receives content
                        │
                        ▼
[leadsheet-core.sty]      __leadsheet_preprocess:n transforms:
                          "<>"  → \lsfill
                          "|"   → \lsbarline
                          "^Cm7" → \__leadsheet_chord_draw:n{Cm7}
                          "^{Name}" → \__leadsheet_progression_use:n{Name}
                        │
                        ▼
[leadsheet-chords.sty]    __leadsheet_chord_draw:n parses "Cm7":
                          Root: C  |  Quality: m  |  Extension: 7
                        │
                        ▼
                    Final output: bold C with superscript ⁷
```

### Naming Conventions (LaTeX3/expl3)

| Type | Pattern | Examples |
|---|---|---|
| Document commands | `\name` | `\chord`, `\key`, `\lsfill` |
| Environments | `lowercase` | `lstabular`, `songsection` |
| Public L3 functions | `\leadsheet_name:spec` | `\leadsheet_chord_format_root:n` |
| Internal functions | `\__leadsheet_name:spec` | `\__leadsheet_preprocess:n` |
| Local variables | `\l__leadsheet_name_type` | `\l__leadsheet_chord_input_tl` |
| Constants | `\c__leadsheet_name_type` | `\c__leadsheet_progression_register_*` |

## Tooling

| Tool | Purpose |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Python package and virtual environment management |
| [just](https://just.systems/) | Task runner (`just test`, `just lint`, `just typecheck`, etc.) |
| [ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [pyright](https://github.com/microsoft/pyright) | Static type checking |
| [pytest](https://pytest.org/) | Test framework |
| [pymupdf](https://pymupdf.readthedocs.io/) | PDF-to-PNG conversion (runtime dependency) |
| [latexmk](https://ctan.org/pkg/latexmk) | Multi-pass LaTeX build tool (backend for compilation) |
| [hatchling](https://hatch.pypa.io/) | Build backend for the Python wheel |

## Testing Strategy

Tests are integration tests that compile real `.tex` files via the CLI and Python API:

- **`TestPDFOutput`** — compile `examples/maniac.tex` once per session (session-scoped fixture), then check that the PDF contains expected text (title, section headings, lyrics).
- **`TestCompilerAPI`** — test `compile_latex()` directly: default output paths, explicit paths, missing input, invalid LaTeX, nested output directory creation, and format validation.
- **`TestPNGFormat`** — test PNG output: `formats="png"`, `formats=["pdf", "png"]`, PNG magic bytes, and the standalone `pdf_to_png()` converter.
- **`TestPageNumbers`** — verify page numbers appear only on multi-page documents by compiling a minimal single-page and a long multi-page document and inspecting extracted text per page.
- **`TestCLI`** — test `python -m leadsheet` via subprocess: `--format`, `--engine`, error exit codes, success messages.

Shared helpers in `conftest.py` (`extract_pdf_text`, `extract_pdf_pages`, `pdf_page_count`, `run_cli`) prevent duplication across test classes.

## Extension Points

### Custom Chord Formatting (LaTeX)

```latex
\ExplSyntaxOn
\cs_set_protected:Npn \leadsheet_chord_format_root:n #1 {
    % Custom root formatting
}
\ExplSyntaxOff
```

### Additional Engines (Python)

The `--engine` CLI flag and `engine` parameter of `compile_latex` accept any engine supported by `latexmk`: `lualatex`, `xelatex`, `pdflatex`.

### Future Extensions

- `leadsheet-tablature.sty` — Guitar tabs
- `leadsheet-diagrams.sty` — Chord diagrams
- `leadsheet-transposition.sty` — Key transposition utilities
