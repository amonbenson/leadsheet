# Leadsheet Package Architecture

## File Organization

```
texleadsheet/
├── leadsheet.cls              # Main document class
├── leadsheet-core.sty         # Core preprocessing & utilities
├── leadsheet-chords.sty       # Chord parsing & progressions
├── leadsheet-sections.sty     # Section environments
├── main.tex                   # Example document
└── README.md                  # User documentation
```

## Module Dependencies

```
leadsheet.cls
    │
    ├─→ [Base packages: extarticle, geometry, fontspec, etc.]
    │
    ├─→ leadsheet-core.sty
    │       ├─→ soul
    │       ├─→ calc
    │       └─→ Provides:
    │               • Preprocessing engine (__leadsheet_preprocess:n)
    │               • Barline commands (lsbarline, lsrepstart, lsrepend)
    │               • Layout utilities (lsfill, lsjoin)
    │
    ├─→ leadsheet-chords.sty
    │       ├─→ Depends on: leadsheet-core (for preprocessing)
    │       └─→ Provides:
    │               • Chord parsing (__leadsheet_chord_draw:n)
    │               • Chord formatting functions
    │               • Progression storage system
    │               • \chord{...} command
    │               • chordprogression environment
    │
    └─→ leadsheet-sections.sty
            ├─→ mdframed
            ├─→ array
            ├─→ Depends on: leadsheet-core (for preprocessing)
            │              leadsheet-chords (for chord rendering)
            └─→ Provides:
                    • lstabular environment
                    • songsection environment
                    • hlsongsection environment
```

## Data Flow: Processing a Song Section

```
User writes:          \begin{songsection}{Verse 1}
                          & ^Cm7 & ^F7 \\
                          <> Hello & world \\
                      \end{songsection}
                              │
                              ▼
[leadsheet-sections.sty]  songsection environment captures body
                              │
                              ▼
[leadsheet-sections.sty]  lstabular environment receives content
                              │
                              ▼
[leadsheet-core.sty]      __leadsheet_preprocess:n transforms:
                          • "<>" → "\lsfill"
                          • "|" → "\lsbarline"
                          • "^Cm7" → "\__leadsheet_chord_draw:n{Cm7}"
                          • "^{Name}" → "\__leadsheet_progression_use:n{Name}"
                              │
                              ▼
[leadsheet-chords.sty]    __leadsheet_chord_draw:n parses "Cm7":
                          • Root: "C"
                          • Quality: "m"
                          • Extension: "7"
                              │
                              ▼
[leadsheet-chords.sty]    Formatting functions apply:
                          • leadsheet_chord_format_root:n{C}
                          • leadsheet_chord_format_ext:n{7}
                              │
                              ▼
                          Final output: **C**⁷ (bold, with superscript)
```

## Naming Convention Map

### Public Interface (User-Facing)

| Type | Pattern | Examples |
|------|---------|----------|
| Document commands | `\name` | `\chord`, `\key`, `\lsfill` |
| Environments | `lowercase` | `lstabular`, `songsection` |
| Formatting commands | `\lschordfmt*` | `\lschordfmtroot`, `\lschordfmtext` |
| Public L3 functions | `\leadsheet_name:spec` | `\leadsheet_chord_format_root:n` |

### Internal/Private

| Type | Pattern | Examples |
|------|---------|----------|
| Internal functions | `\__leadsheet_name:spec` | `\__leadsheet_preprocess:n`, `\__leadsheet_chord_draw:n` |
| Local variables | `\l__leadsheet_name_type` | `\l__leadsheet_chord_input_tl`, `\l__leadsheet_tabular_content_tl` |
| Constants | `\c__leadsheet_name_type` | `\c__leadsheet_progression_register_*` |

### Argument Specifiers

- `:n` - Single mandatory argument (braced group)
- `:N` - Single token (no braces)
- `:V` - Value of a variable
- `:x` - Fully expanded argument
- `_tl` - Token list variable
- `_seq` - Sequence variable

## Function Categorization

### Core Module (leadsheet-core.sty)

**Preprocessing:**
- `\__leadsheet_preprocess:n` - Main preprocessing engine (INTERNAL)

**Barlines:**
- `\lsbarline` - Regular barline (PUBLIC)
- `\lsrepstart` - Repeat start barline (PUBLIC)
- `\lsrepend` - Repeat end barline (PUBLIC)
- `\lslsym`, `\lsrsym` - Helper macros (PUBLIC but low-level)

**Layout:**
- `\lsfill` - Infinite fill space (PUBLIC)
- `\lsjoin` - Join cells with dashes (PUBLIC)

### Chords Module (leadsheet-chords.sty)

**Parsing:**
- `\__leadsheet_chord_draw:n` - Parse and render chord (INTERNAL)
- `\__leadsheet_chord_draw_annot:n` - Render annotation (INTERNAL)
- `\__leadsheet_chord_draw_nc:` - Render "no chord" (INTERNAL)

**Formatting (Customizable):**
- `\leadsheet_chord_format_root:n` - Format root note (PUBLIC L3)
- `\leadsheet_chord_format_ext:n` - Format extension (PUBLIC L3)
- `\leadsheet_chord_format_slash:` - Format slash separator (PUBLIC L3)
- `\lschordfmtroot`, `\lschordfmtext`, etc. - Legacy formatting commands (PUBLIC)

**Progressions:**
- `\__leadsheet_progression_select_register:n` - Generate register name (INTERNAL)
- `\__leadsheet_progression_use:n` - Retrieve progression (INTERNAL)

**User Interface:**
- `\chord{...}` - Render chord command (PUBLIC)
- `chordprogression` environment - Define progression (PUBLIC)

### Sections Module (leadsheet-sections.sty)

**Environments:**
- `lstabular` - Tabular with preprocessing (PUBLIC)
- `songsection` - Song section with title (PUBLIC)
- `hlsongsection` - Highlighted section (PUBLIC)

## Variable Scope and Lifetime

### Local Variables (l__)
Created fresh for each function call, destroyed on exit:
- `\l__leadsheet_preproc_input_tl` - Preprocessing input buffer
- `\l__leadsheet_chord_input_tl` - Chord parsing input
- `\l__leadsheet_tabular_content_tl` - Tabular content buffer

### Constants (c__)
Created once, never modified:
- `\c__leadsheet_progression_register_*` - Stored chord progressions

## Extension Points

Users can customize the package by redefining:

1. **Chord Formatting Functions**
   ```latex
   \ExplSyntaxOn
   \cs_set_protected:Npn \leadsheet_chord_format_root:n #1 {
       % Custom formatting here
   }
   \ExplSyntaxOff
   ```

2. **Legacy Formatting Commands**
   ```latex
   \renewcommand{\lschordfmtroot}[1]{...}
   ```

3. **Barline Dimensions**
   ```latex
   \setlength{\lsbarlinewidth}{...}
   ```

4. **Environment Styling** (advanced)
   - Modify `mdframed` options for `hlsongsection`
   - Adjust spacing in `songsection`

## Design Rationale

### Why Three Separate `.sty` Files?

1. **leadsheet-core.sty**: Fundamental utilities needed by all other modules
   - No dependencies on chords or sections
   - Pure preprocessing and layout tools

2. **leadsheet-chords.sty**: Chord-specific functionality
   - Depends on core preprocessing
   - Independent of section formatting
   - Could theoretically be used without sections

3. **leadsheet-sections.sty**: High-level document structure
   - Depends on both core and chords
   - Combines all functionality into user-facing environments

### Separation of Concerns

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| core | Syntax transformation, utilities | None (LaTeX3 only) |
| chords | Musical notation parsing | core |
| sections | Document structure | core, chords |
| .cls file | Package assembly, styling | All modules |

## Performance Considerations

1. **Regex Preprocessing**: Most expensive operation happens once per `lstabular` body
2. **Chord Progression Storage**: Progressions stored as constants (created once, never copied)
3. **Variable Scoping**: Local variables properly scoped to avoid memory leaks

## Future Extension Possibilities

1. **Additional Modules** could be added:
   - `leadsheet-tablature.sty` - Guitar tabs
   - `leadsheet-diagrams.sty` - Chord diagrams
   - `leadsheet-transposition.sty` - Key transposition tools

2. **Backend Independence**:
   - Core preprocessing is engine-agnostic
   - Font selection isolated to main `.cls` file

3. **Internationalization**:
   - Error messages already use `\msg_new:nnn`
   - Easy to add translations
