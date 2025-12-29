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

% Load the article base class with extended font sizes
\LoadClass[11pt,a4paper]{extarticle}

% Page layout
\RequirePackage[a4paper,margin=1.5cm]{geometry}

% Font and encoding support
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[english]{babel}
\RequirePackage{fontspec}
\RequirePackage[babel=true]{microtype}

% Math support (for symbols used in formatting)
\RequirePackage{amsmath}

% Utility packages
\RequirePackage{etoolbox}

% Set the main font to TeX Gyre Heros (Helvetica clone)
\setmainfont{TeX Gyre Heros}


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

% Variable to store the key signature
\newcommand{\@key}{}

% \key{<key>}
% Sets the key signature to be displayed in the title.
% The key is rendered as a chord symbol.
%
% Example: \key{Cm}
%
\newcommand{\key}[1]{\renewcommand{\@key}{\chord{#1}}}

% Redefine \maketitle to show title and key on the same line
% Title is large and bold on the left, key is on the right
\renewcommand{\maketitle}{%
    \noindent\textbf{\Huge%
        \@title%
        \hfill%
        \@key%
    }%
    \par\vspace{1em}%
}

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
