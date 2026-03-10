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
│   └── latex/                  # LaTeX class files (package data, mirrors latex/)
│       ├── leadsheet.cls
│       ├── leadsheet-core.sty
│       ├── leadsheet-chords.sty
│       └── leadsheet-sections.sty
├── latex/                      # Canonical LaTeX source files
│   ├── leadsheet.cls           # Main document class
│   ├── leadsheet-core.sty      # Core preprocessing & utilities
│   ├── leadsheet-chords.sty    # Chord parsing & progressions
│   └── leadsheet-sections.sty # Section environments
├── examples/                   # Example leadsheets
│   ├── maniac.tex
│   ├── maniac.pdf              # Built by `just example-pdf`
│   └── maniac.png              # Built by `just example-png`
├── tests/                      # Test suite
│   ├── conftest.py             # Shared fixtures and helpers
│   └── test_compiler.py        # Integration tests
├── pyproject.toml              # Project metadata, dependencies, tool config
└── justfile                    # Task runner commands
```

## Python Package

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `compiler.py` | Locate LaTeX class files, build environment, invoke latexmk, collect output PDF |
| `__main__.py` | Parse CLI arguments, call `compile_latex`, handle and format errors |
| `__init__.py` | Re-export public API: `compile_latex`, `CompilationError` |

### Compilation Flow

```
CLI / Python API
        │
        ▼
compile_latex(input_path, output_path, engine, verbose)
        │
        ├── _find_latex_dir()          # Locate leadsheet.cls and .sty files
        │       ├── Try: leadsheet/latex/  (package data, installed or editable)
        │       └── Try: latex/            (repo root, development fallback)
        │
        ├── _build_env(latex_dir)      # Set TEXINPUTS so TeX finds class files
        │
        ├── _build_cmd(engine, ...)    # Assemble latexmk command
        │
        ├── subprocess.run(cmd, ...)   # Execute latexmk in a temp directory
        │
        └── shutil.copy2(tmp_pdf, output_path)   # Move PDF to requested location
```

### Error Handling

- `FileNotFoundError` — input file not found, or LaTeX class files not found
- `CompilationError` — latexmk exited with non-zero code; carries `.stdout` and `.stderr` for debugging

### LaTeX Class File Resolution

The Python package bundles the LaTeX files in two locations:

1. **`leadsheet/latex/`** — package data included in the installed wheel (via `[tool.hatch.build.targets.wheel.force-include]`). This is checked first.
2. **`latex/`** (repo root) — development fallback when running from the source tree without an editable install.

The TEXINPUTS environment variable is set at compilation time so `lualatex` finds `leadsheet.cls` regardless of the working directory.

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
| [just](https://just.systems/) | Task runner (`just test`, `just example`, etc.) |
| [ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [pytest](https://pytest.org/) | Test framework |
| [latexmk](https://ctan.org/pkg/latexmk) | Multi-pass LaTeX build tool (backend for compilation) |
| [hatchling](https://hatch.pypa.io/) | Build backend for the Python wheel |

## Testing Strategy

Tests are integration tests that compile real `.tex` files via the CLI and Python API:

- **`TestPDFOutput`** — compile `examples/maniac.tex` once per session (session-scoped fixture), then check that the PDF contains expected text (title, section headings, lyrics).
- **`TestCompilerAPI`** — test `compile_latex()` directly: default output paths, explicit paths, missing input, invalid LaTeX, and nested output directory creation.
- **`TestCLI`** — test `python -m leadsheet` via subprocess: successful compilation, success message, error exit codes, default output path, `--engine` flag.

Shared helpers in `conftest.py` (`extract_pdf_text`, `run_cli`) prevent code duplication across test classes.

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
- `compile_to_png()` — Direct PDF-to-PNG convenience wrapper
