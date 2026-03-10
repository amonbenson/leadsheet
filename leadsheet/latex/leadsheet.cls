%!TeX program = LuaLaTeX
%
% leadsheet.cls
% A document class for creating musical leadsheets with lyrics and chords
%
% This class provides environments and commands for typesetting song leadsheets
% with integrated chord symbols, lyrics, barlines, and sectional structure.
%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{leadsheet}[2025/12/29 v2.0 Leadsheet document class]

% ============================================================================
% BASE CLASS AND CORE PACKAGES
% ============================================================================

% Load the article base class
\LoadClass{extarticle}

% Key-value options support
\RequirePackage{kvoptions}

\SetupKeyvalOptions{
    family=LS,
    prefix=LS@
}

\DeclareStringOption[11pt]{fontsize}
\DeclareStringOption[1.5cm]{margin}
\DeclareStringOption[0.25cm]{hlmargin}
\DeclareStringOption[2.5ex plus 0.5ex minus 0.5ex]{titlespacebefore}
\DeclareStringOption[0pt]{titlespaceafter}

\ProcessKeyvalOptions*

% Page layout
\RequirePackage[a4paper,margin=\LS@margin]{geometry}
\RequirePackage[fontsize=\LS@fontsize]{fontsize}

\RequirePackage{titlesec}
\titlespacing*{\section}{0pt}{\LS@titlespacebefore}{\LS@titlespaceafter}
\titlespacing*{\subsection}{0pt}{\LS@titlespacebefore}{\LS@titlespaceafter}

% Font and encoding support
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[english]{babel}
\RequirePackage{fontspec}
\RequirePackage[babel=true]{microtype}
\RequirePackage{lilyglyphs}

% Math support (for symbols used in formatting)
\RequirePackage{amsmath}

% Utility packages
\RequirePackage{etoolbox}

% Set the main font to TeX Gyre Heros (Helvetica clone)
\setmainfont{TeX Gyre Heros}
\pgfmathsetmacro{\lsFontSizeRatio}{\f@size / 10.95}%


% ============================================================================
% LOAD LEADSHEET PACKAGE MODULES
% ============================================================================
% The leadsheet functionality is split into modular components:
%   - leadsheet-core: preprocessing engine, barlines, utilities
%   - leadsheet-chords: chord parsing, formatting, and progressions
%   - leadsheet-sections: song sections and tabular environments

\RequirePackage{leadsheet-core}
\RequirePackage{leadsheet-chords}
\RequirePackage{leadsheet-sections}


% ============================================================================
% TITLE PAGE CUSTOMIZATION
% ============================================================================
% Custom title page that displays song title and key signature

\makeatletter

% Variables to store the key signature and tempo information
\newcommand{\@key}{}
\newcommand{\@tempo}{}

% \key{<key>}
% Sets the key signature to be displayed in the title.
% The key is rendered as a chord symbol.
% Handles # character properly by storing it for later rendering
%
% Example: \key{Cm}
%
\ExplSyntaxOn
\tl_new:N \g__leadsheet_key_tl
\NewDocumentCommand { \key } { m } {
    \tl_gset:Nn \g__leadsheet_key_tl { #1 }
    \renewcommand{\@key}{\expandafter\chord\expandafter{\g__leadsheet_key_tl}}
}
\ExplSyntaxOff

% \tempo[<note>]{<bpm>}
% Sets the tempo to be displayed in the title.
% The optional <note> argument specifies the note value for the tempo marking.
% Default is quarter note.
%
% Example: \tempo{120} or \tempo[\musicalhalfnote]{60}
%
\ExplSyntaxOn
\NewDocumentCommand { \tempo } { o m } {
    \IfNoValueTF { #1 }
        { \renewcommand{\@tempo}{\quarterNote[scale=\lsFontSizeRatio] = #2} }
        { \renewcommand{\@tempo}{#1 = #2} }
}
\ExplSyntaxOff

% Redefine \maketitle to show title and key on the same line
% Title is large and bold on the left, key is on the right
\renewcommand{\maketitle}{%
    \noindent\textbf{\Huge%
        \@title%
        \hfill%
        \ifx\@tempo\empty\else\quad\@tempo\fi%
        \ifx\@key\empty\else\quad\@key\fi%
    }%
    \par\vspace{\LS@titlespaceafter}%
}

% Remove paragraph indentation globally
\setlength\parindent{0pt}

\makeatother


% ============================================================================
% BACKWARD COMPATIBILITY
% ============================================================================
% Some legacy commands are kept for compatibility with existing documents

% Note: The following commands are defined in the modular packages but are
% documented here for reference:
%
% Core utilities (from leadsheet-core.sty):
%   \lsfill           - Infinite fill space
%   \lsjoin           - Join cells with dashes
%   \lsbarline        - Regular barline
%   \lsrepstart       - Repeat start barline (||:)
%   \lsrepend         - Repeat end barline (:||)
%
% Chord system (from leadsheet-chords.sty):
%   \chord{...}       - Render a chord symbol
%   chordprogression  - Define a named chord progression
%
% Section environments (from leadsheet-sections.sty):
%   lstabular         - Tabular environment for lyrics/chords
%   songsection       - Song section with title
%   hlsongsection     - Highlighted song section

\endinput
