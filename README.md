[![CI](https://github.com/amonbenson/leadsheet/actions/workflows/ci.yml/badge.svg)](https://github.com/amonbenson/leadsheet/actions/workflows/ci.yml)

# Leadsheet

A Python library and LaTeX document class for creating professional musical leadsheets with integrated chord symbols, lyrics, barlines, and sectional structure.

## Features

- **Chord Notation**: Simple syntax for chord symbols (`^Cm7`, `^F#maj9/A`)
- **Chord Progressions**: Define reusable chord progressions with named references
- **Barlines**: Automatic formatting of regular (`|`) and repeat barlines (`||:`, `:||`)
- **Song Sections**: Environments for verses, choruses, bridges with optional highlighting
- **Flexible Layout**: Automatic spacing and alignment for professional appearance
- **Python CLI**: Compile `.tex` leadsheets to PDF from the command line

## Quick Start

### Compile a leadsheet

```bash
# Compile to PDF (same directory as input)
python -m leadsheet my_song.tex

# Specify output path
python -m leadsheet my_song.tex output/my_song.pdf

# Compile to PNG
python -m leadsheet my_song.tex output/my_song --format png

# Compile to both PDF and PNG
python -m leadsheet my_song.tex output/my_song --format pdf png

# Use a different LaTeX engine
python -m leadsheet my_song.tex --engine xelatex
```

### Use as a Python library

```python
from leadsheet import compile_latex

# Compile to PDF (default)
result = compile_latex("my_song.tex", "output/my_song.pdf")
print(f"PDF: {result['pdf']}")

# Compile to PNG
result = compile_latex("my_song.tex", "output/my_song", formats="png")
print(f"PNG: {result['png']}")

# Compile to both
result = compile_latex("my_song.tex", "output/my_song", formats=["pdf", "png"])
```

### Write a leadsheet

```latex
\documentclass{leadsheet}

% Make the title size a bit smaller so it fits nicely
\title{\huge{Schlegel Flegel -- No Escape}}
\key{Gm}
\tempo{120}

\begin{chordprogression}{Verse}
    |^Gm >> & |^Dm >> & |^F >> & |^Csus4 ^C
\end{chordprogression}

\begin{chordprogression}{Chorus}
    |^Gm >> & |^Dm >> & |^F >> & |^Cm
\end{chordprogression}

\begin{chordprogression}{Post-Chorus}
    |^Gm >> & |^Dm >> & |^F >> & |^C
\end{chordprogression}

\begin{chordprogression}{Chorus Variation}
    |^G >> & |^D >> & |^Fm >> & |^Cm
\end{chordprogression}

\begin{document}

\maketitle

\begin{songsection}{Intro}
    ^{Verse}
\end{songsection}

\begin{songsection}{Verse 1}
    ^{Verse} \\
    <> What would you do, & trapped in your mind, <> like a & crea - ture in a & cage <> \\
    ^{Verse} \\
    <> Red its eyes, a & terrible scream, <> like a & desperate cry for & help <>
\end{songsection}

\begin{songsection}{Bridge 1}
    & |^Cm >> & |^G >> & |^Cm >> & ^G >> ^G/F \\
    & <> But such a warming & heart. <> & Inside those glaring & eyes \\
    & |^Cm/Eb ^Bb/D ^Cm ^Bb/D & |^Eb >> ^Eb ^F \\
    A & voice sweeter than & mine
\end{songsection}

\begin{hlsongsection}{Chorus 1}
    ^{Chorus} \\
    <> No escape I'm cag-&ed in my own world. <> & I can never die, & >> it is a cry for help <> \\
    ^{Chorus} \\
    <> Burning in my thro-&at cause I taste it, <> but & I can't feel the pa-&in, because I'm already numb <> \\
\end{hlsongsection}

\begin{songsection}{Post-Chorus 1}
    ^{Post-Chorus} \\
    ^{Post-Chorus} \\
    \\
    ^{Chorus}
\end{songsection}

\begin{songsection}{Bridge 2}
    ^{Post-Chorus} \\
    And I & know one & thing for & sure <> \\
\end{songsection}

\begin{hlsongsection}{Chorus 2}
    & ^{Chorus Variation} \\
    I will esca-&pe from my cage and fl-&ee from my own world. <> & I would rather die-&~ and I don't need your help <> \\
    & ^{Chorus Variation} \\
    & <> It will take me a lo-&ng way to go there, <> but & I can't feel the pa-&in, who isn't already numb? <> \\
\end{hlsongsection}

\begin{songsection}{Post-Chorus 2}
    ^{Post-Chorus} \\
    & <> Who isn't already nu-&mb? & >> Who isn't already numb? \\
    ^{Post-Chorus} \\
    & <> Who isn't already nu-&mb? & >> Because I'm already numb
\end{songsection}

\begin{songsection}{Outro}
    ^{Chorus}
\end{songsection}

\end{document}
```

![Example Leadsheet Output](examples/No%20Escape.png)


## Installation

Requires [uv](https://docs.astral.sh/uv/) for package management.

```bash
git clone https://github.com/yourname/leadsheet
cd leadsheet
just setup
```

Or install directly:

```bash
uv add leadsheet
```

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [just](https://just.systems/) — command runner
- A TeX distribution with LuaLaTeX and `latexmk` (e.g. [TeX Live](https://tug.org/texlive/), [MiKTeX](https://miktex.org/))
### Common commands

```bash
just setup          # Install dependencies
just test           # Run the test suite
just lint           # Check for lint and format issues
just typecheck      # Run pyright type checker
just check          # Check for any code issues (runs typecheck and lint)
just fix            # Auto-fix and format
just build-examples # Build examples/maniac.pdf and examples/maniac.png
just build          # Build wheel and sdist
just clean          # Remove temporary output files
```

## LaTeX Syntax Reference

### Chord Notation

Within `lstabular` or song section environments:

| Syntax | Meaning |
|---|---|
| `^Cm7` | C minor 7th chord |
| `^F#maj9` | F# major 9th chord |
| `^Dm7/A` | D minor 7th, A in bass |
| `^{Verse}` | Reference a named chord progression |
| `^!{text}` | Custom annotation |
| `^nC` | "No chord" annotation |

### Barlines

| Syntax | Meaning |
|---|---|
| `\|` | Regular barline |
| `\|\|:` | Repeat start |
| `:\|\|` | Repeat end |

### Special Syntax

| Syntax | Meaning |
|---|---|
| `<>` | Infinite fill space (push content apart) |
| `- &` | Join table cells with dashes |
| `>>` | Medium space after a chord |
| `>>>` | Large space after a chord |

### Chord Progressions

Define once, reuse anywhere:

```latex
\begin{chordprogression}{Intro}
    |^Cm7 & ^F7 & ^Bb & ^Eb
\end{chordprogression}

\begin{songsection}{Intro}
    & ^{Intro} \\
    <> & Instrumental \\
\end{songsection}
```

## Requirements

- Python >= 3.12
- LuaLaTeX (recommended) or XeLaTeX
- TeX Gyre Heros font (usually bundled with TeX distributions)
- LaTeX packages: `fontspec`, `expl3`, `mdframed`, `soul`, `array`, `geometry`, `microtype`, `fancyhdr`, `lastpage`

## Project Structure

```
leadsheet/
├── leadsheet/          # Python package
│   ├── __init__.py
│   ├── __main__.py     # CLI entry point
│   ├── compiler.py     # Compilation engine
│   ├── converter.py    # PDF-to-PNG conversion
│   └── latex/          # LaTeX class files (bundled as package data)
│       ├── leadsheet.cls
│       ├── leadsheet-core.sty
│       ├── leadsheet-chords.sty
│       └── leadsheet-sections.sty
├── examples/           # Example leadsheets
│   └── maniac.tex
├── tests/              # Test suite
│   ├── conftest.py
│   └── test_compiler.py
├── .github/workflows/  # CI
│   └── ci.yml
├── pyproject.toml
└── justfile
```

## License

[Add your license information here]

## Author

[Add your author information here]
