# Leadsheet Document Class

A LaTeX document class for creating professional musical leadsheets with integrated chord symbols, lyrics, barlines, and sectional structure.

## Features

- **Chord Notation**: Simple syntax for chord symbols (`^Cm7`, `^F#maj9/A`)
- **Chord Progressions**: Define reusable chord progressions with named references
- **Barlines**: Automatic formatting of regular (`|`) and repeat barlines (`||:`, `:||`)
- **Song Sections**: Environments for verses, choruses, bridges with optional highlighting
- **Flexible Layout**: Automatic spacing and alignment for professional appearance
- **Modular Architecture**: Clean separation of concerns following LaTeX3 conventions

## Quick Start

```latex
\documentclass{leadsheet}
\geometry{a5paper,landscape}

\title{Michael Sembello -- Maniac}
\key{Ebm}

\begin{chordprogression}{Verse A}
    |^Ebm#11 >> & |^Ebm7add13 >> & |^Ebm7 >> & |^Ebmmaj7 >>
\end{chordprogression}

\begin{chordprogression}{Verse B}
    |^Bbm5 >> & |^B6 >> & |^Bbsus2 >> & |^Bbsus4 ^B >>
\end{chordprogression}

\begin{document}

\maketitle

\begin{songsection}{Verse 1}
    & ^{Verse A} \\
    <> Just a & steel town girl on a & Saturday night. <> Lookin' & for the fight of her & life \\
    & ^{Verse B} \\
    <> In the & real-time world, no one & sees her at all. <> They & all say she's cra- & zy \\
    & ^{Verse A} \\
    <> Locking & rhythms to the & beat of her heart. <> Changing & movement into light \\
    & ^{Verse B} \\
    <> She has & danced into the & danger zone. <> When the & dancer becomes the & dance
\end{songsection}

\end{document}
```

## Package Structure

The leadsheet class is organized into modular components:

### Core Files

- **[leadsheet.cls](leadsheet.cls)** - Main document class
  - Loads base packages and fonts
  - Defines title page layout
  - Imports all leadsheet modules

- **[leadsheet-core.sty](leadsheet-core.sty)** - Preprocessing engine and utilities
  - Syntax transformation (barlines, symbols, special characters)
  - Barline formatting commands (`\lsbarline`, `\lsrepstart`, `\lsrepend`)
  - Layout utilities (`\lsfill`, `\lsjoin`)

- **[leadsheet-chords.sty](leadsheet-chords.sty)** - Chord system
  - Chord parsing and rendering (`\chord{...}`)
  - Chord progression storage and retrieval
  - `chordprogression` environment

- **[leadsheet-sections.sty](leadsheet-sections.sty)** - Section environments
  - `lstabular` - Tabular environment for lyrics/chords
  - `songsection` - Song section with title
  - `hlsongsection` - Highlighted song section

## Naming Conventions

Following [LaTeX3/expl3 conventions](https://www.latex-project.org/help/documentation/expl3.pdf):

### Public API
- **Document commands**: `\chord`, `\key`, `\lsfill`, etc.
- **Environments**: `lstabular`, `songsection`, `chordprogression`
- **Public functions**: `\leadsheet_chord_format_root:n`

### Internal/Private API
- **Internal functions**: `\__leadsheet_preprocess:n`, `\__leadsheet_chord_draw:n`
- **Variables**: `\l__leadsheet_chord_input_tl`, `\l__leadsheet_tabular_content_tl`

Convention: Private/internal names use double underscore (`__`) after the module prefix.

## Syntax Reference

### Chord Notation

Within `lstabular` or song section environments:

- `^Cm7` - C minor 7th chord
- `^F#maj9` - F# major 9th chord
- `^Dm7/A` - D minor 7th with A in bass
- `^{Verse}` - Reference to named chord progression
- `^!{text}` - Custom annotation
- `^nC` - "No chord" annotation (n. C.)

### Barlines

- `|` - Regular barline
- `||:` - Repeat start
- `:||` - Repeat end

### Special Syntax

- `<>` - Infinite fill space (push content apart)
- `- &` - Join table cells with dashes

### Chord Progressions

Define once, use anywhere:

```latex
\begin{chordprogression}{Intro}
    |^Cm7 & ^F7 & ^Bb & ^Eb
\end{chordprogression}

% Later in the document:
\begin{songsection}{Intro}
    & ^{Intro} \\
    <> & Instrumental \\
\end{songsection}
```

## Customization

### Chord Formatting

Override formatting functions to customize appearance:

```latex
% Redefine in your document preamble
\ExplSyntaxOn
\cs_set_protected:Npn \leadsheet_chord_format_root:n #1 {
    \textcolor{blue}{\textbf{#1}}  % Blue chord roots
}
\ExplSyntaxOff
```

Or use the legacy commands:

```latex
\renewcommand{\lschordfmtroot}[1]{\textcolor{blue}{\textbf{#1}}}
```

### Barline Widths

```latex
\setlength{\lsbarlinewidth}{1.5pt}      % Thicker barlines
\setlength{\lsreplinewidth}{3pt}        % Thicker repeat barlines
```

### Highlight Colors

```latex
% Modify the hlsongsection environment
% (requires understanding mdframed package options)
```

## Requirements

- LuaLaTeX (recommended) or XeLaTeX
- TeX Gyre Heros font (usually included with TeX distributions)
- Packages: `fontspec`, `expl3`, `mdframed`, `soul`, `array`, `geometry`, `microtype`

## Compilation

```bash
lualatex main.tex
```

## Architecture Decisions

### Why Split Into Multiple Files?

1. **Maintainability**: Each module has a single, clear responsibility
2. **Readability**: Smaller files are easier to navigate and understand
3. **Reusability**: Modules can potentially be used independently
4. **Testing**: Isolated components are easier to test and debug
5. **Standards**: Follows best practices from major LaTeX packages

### Design Principles

- **Progressive Enhancement**: Core functionality works simply; advanced features available when needed
- **Backwards Compatibility**: Legacy command names preserved where possible
- **User Control**: Formatting functions exposed for customization
- **Sensible Defaults**: Professional appearance out of the box

## Development

The package follows LaTeX3 programming conventions:

- Variables are properly typed (tl, seq, etc.)
- Function names include argument specifiers (`:n`, `:N`, etc.)
- Private functions clearly marked with `__`
- Comprehensive inline documentation

## Version History

- **v2.0** (2025-12-29): Complete modular refactoring
  - Split into separate `.sty` files
  - Renamed all functions to follow expl3 conventions
  - Added comprehensive documentation
  - Improved code organization and comments

- **v1.0** (2025-11-30): Original monolithic implementation

## License

[Add your license information here]

## Author

[Add your author information here]

## References

- [The expl3 package and LaTeX3 programming](https://tug.org/docs/latex/l3kernel/expl3.pdf)
- [LaTeX3 Interfaces Documentation](https://ctan.org/pkg/l3kernel)
- [LaTeX package structure guide](https://en.wikibooks.org/wiki/LaTeX/Installing_Extra_Packages)
