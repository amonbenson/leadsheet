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

\title{Maniac}
\key{Ebm}
\tempo{160}

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

![Example Leadsheet Output](example.png)

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
- `>>` - Insert a medium space (after a chord)
- `>>>` - Insert a large space (after a chord)

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

## Requirements

- LuaLaTeX (recommended) or XeLaTeX
- TeX Gyre Heros font (usually included with TeX distributions)
- Packages: `fontspec`, `expl3`, `mdframed`, `soul`, `array`, `geometry`, `microtype`

## Compilation

```bash
lualatex main.tex
```

## License

[Add your license information here]

## Author

[Add your author information here]
