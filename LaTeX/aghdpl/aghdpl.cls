%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
% File:     aghdpl.cls           (LaTeX Document class option "aghdpl")
%          
% Author:  Paweł Kłeczek      (pkleczek@agh.edu.pl)
%          Grzegorz J. Nalepa (gjn@agh.edu.pl)
%          Marcin Szpyrka     (mszpyrka@agh.edu.pl)
%          AGH University of Science and Technology, Kraków, POLAND
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\message{*** [aghdpl.cls] ---  (PK, GJN, MSz)  v4.0 <2020-11-03>  ***}

\newif\ifpdflatex\pdflatexfalse
\NeedsTeXFormat{LaTeX2e} % 
\ProvidesClass{aghdpl/aghdpl}

\RequirePackage{kvoptions}

\DeclareStringOption[pl]{language}
\DeclareBoolOption[true]{symmetric}
\ProcessKeyvalOptions*

\DeclareOption{pdflatex}{\pdflatextrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions

\ifaghdpl@symmetric
	\LoadClass[a4paper,oneside]{report}
\else
	\LoadClass[a4paper,twoside,openright]{report}
\fi

\RequirePackage{float}

\RequirePackage{xstring}

\newcommand{\ThesisLanguage}{pl}
\IfStrEqCase{\aghdpl@language}
{%
	{en}{\renewcommand{\ThesisLanguage}{en}}%
	{pl}{\renewcommand{\ThesisLanguage}{pl}}%
}[\PackageError{aghdpl}{Invalid thesis language.}{Available languages: Polish (pl), English (en)}]

\RequirePackage{times}
\RequirePackage[T1]{fontenc}

% Lista wszystkich języków stanowiących języki pozycji bibliograficznych użytych w pracy.
% (Zgodnie z zasadami tworzenia bibliografii każda pozycja powinna zostać utworzona zgodnie z zasadami języka, w którym dana publikacja została napisana.)
\IfStrEq{\ThesisLanguage}{en}
{%
    \RequirePackage[english,polish]{babel}
    \selectlanguage{english}
}

\IfStrEq{\ThesisLanguage}{pl}
{%
    \RequirePackage[polish,english]{babel}
    \selectlanguage{polish}
    \RequirePackage{polski}
}

% Użyj kodowania UTF-8.
\RequirePackage[utf8]{inputenc}

\RequirePackage{mathtools}
\RequirePackage{amsfonts}
\RequirePackage{amsmath}
\RequirePackage{amsthm}

\RequirePackage{graphicx}
\RequirePackage[usenames]{color}
\RequirePackage{url}
\RequirePackage{titlesec}
\RequirePackage{tocloft}

\RequirePackage[font=small, labelfont=bf, labelsep=period]{caption}
\RequirePackage{subcaption}
\RequirePackage{enumerate}
\RequirePackage{enumitem}

% =============================================================================
% SEC:   Ustawienia związane z formatowaniem tekstu
% =============================================================================

\RequirePackage{geometry}

\RequirePackage{geometry}
\ifaghdpl@symmetric
	% Symmetric layout for single-sided or digital
	\geometry{
		margin=25mm,   % equal margins left/right/top/bottom
		head=10mm,
		foot=10mm
	}
\else
	% Book-style (more inner margin)
	\geometry{
		lmargin=30mm,  % inner on odd pages
		rmargin=20mm,  % outer on odd pages
		tmargin=20mm,
		bmargin=20mm,
		head=10mm,
		foot=10mm
	}
\fi

\linespread{1.25}  % interlinia
\renewcommand{\labelitemi}{--}  % znak wypunktowania użyty w liście wypunktowania

\setlist[itemize]{itemsep=3pt, topsep=5pt}
\setlist[enumerate]{itemsep=3pt, topsep=5pt}

\RequirePackage[all,defaultlines=2]{nowidow} % Kontrola sierot i wdów - działa lepiej niż \widowpenalty i \clubpenalty
\brokenpenalty=10000\relax

% =============================================================================
% SEC:   Polecenia wymagane m.in. do generowania strony tytułowej
% =============================================================================

\def\shorttitlePL#1   {\gdef\@shorttitlePL{#1}}
\def\shorttitleEN#1   {\gdef\@shorttitleEN{#1}}
\def\shortauthor#1    {\gdef\@shortauthor{#1}}
\def\titlePL#1        {\gdef\@titlePL{#1}}
\def\titleEN#1        {\gdef\@titleEN{#1}}
\def\faculty#1      {\gdef\@faculty{#1}}
\def\thesistype#1   {\gdef\@thesistype{#1}}
\def\supervisor#1   {\gdef\@supervisor{#1}}
\def\acknowledgements#1   {\gdef\@acknowledgements{#1}}
\def\department#1   {\gdef\@department{#1}}
\def\degreeprogramme#1 {\gdef\@degreeprogramme{#1}}

% --- Detect multiple authors and choose labels accordingly ---
% Helper: choose #1 if multiple authors, else #2

\newcommand{\aghdpl@ifmultipleauthors}[2]{%
	\IfSubStr{\@author}{\\}{#1}{%
		\IfSubStr{\@author}{,}{#1}{#2}%
	}%
}


% Public macro: language-aware singular/plural label
\newcommand{\AuthorsLabel}{%
	\IfStrEqCase{\ThesisLanguage}{%
		{pl}{\aghdpl@ifmultipleauthors{Autorzy}{Autor}}%
		{en}{\aghdpl@ifmultipleauthors{Authors}{Author}}%
	}[\aghdpl@ifmultipleauthors{Authors}{Author}]%
}

% --- User-tunable knobs ---
\newcommand{\aghdpl@authorslinespread}{0.8} % < 1.0 makes lines tighter;
\newcommand{\aghdpl@authorslineextra}{0pt}  % extra vertical space per line

% Render authors as a single multi-line cell with tight line spacing
\newcommand{\aghdpl@authorscell}{%
	\begingroup
	\def\and{\\}%
	% Tighter line spacing within the mini-tabular
	\renewcommand{\arraystretch}{\aghdpl@authorslinespread}%
	\begin{tabular}[t]{@{}l@{}}%
		\@author
	\end{tabular}%
	\endgroup
}



%------------------------------------------------------------------------------
\newcommand{\aghdpl@tablerowsep}{0.9ex}
\IfStrEqCase{\ThesisLanguage}
{
	{pl}{%
		\def\thesisheaders
        {
			\fancyfoot[LO,LE]{\small \textit{\@shorttitlePL}}
			\fancyfoot[RO,RE]{\small \@shortauthor}
		}

		\def\thesistable
        {
			\begingroup
			\setlength{\extrarowheight}{\aghdpl@tablerowsep}
			\begin{tabular}{p{45mm}l}
				\AuthorsLabel:    & {\itshape \aghdpl@authorscell} \\[-1mm]
				Kierunek studiów: & {\itshape \@degreeprogramme}   \\[-1mm]
				\IfStrEq{\@supervisor}{}{}{Opiekun pracy: & {\itshape \@supervisor}\\}
			\end{tabular}
			\endgroup
		}
	}
	{en}{%
		\def\thesisheaders
        {
			\fancyfoot[LO,LE]{\small \textit{\@shorttitleEN}}
			\fancyfoot[RO,RE]{\small \@shortauthor}
		}

		\def\thesistable
        {
			\begingroup
			\setlength{\extrarowheight}{\aghdpl@tablerowsep}
			\begin{tabular}{p{45mm}l}
				\AuthorsLabel:    & {\itshape \aghdpl@authorscell} \\[-1mm]
				Degree programme: & {\itshape \@degreeprogramme}   \\[-1mm]
				\IfStrEq{\@supervisor}{}{}{Supervisor: & {\itshape \@supervisor}\\}
			\end{tabular}
			\endgroup
		}
	}%
}

\newcommand{\titlepages}{%

	\titlepage

	\begin{center}
		\vspace*{1.5cm}

		\includegraphics[scale=0.6]{aghdpl/agh.jpg}

		\vspace*{2mm}
		{
            \IfStrEq{\ThesisLanguage}{en}
            {% t
                \scalebox{0.95}{\sffamily{\large{\bfseries{\scshape AGH University of Kraków}}}}
            }
            {% f
                \scalebox{0.95}{\sffamily{\large{\bfseries{\scshape Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie}}}}
            }
            
			\vspace*{1mm}

			{\sffamily\small\bfseries \@faculty}
		}
		\vspace*{15mm}

		{\sffamily\Large \@thesistype}
		\vspace*{9mm}

		{\sffamily\Large\itshape
			\IfStrEqCase{\ThesisLanguage}{%
				{pl}{\@titlePL}
				{en}{\@titleEN}
			}
		}
		\vspace*{1mm}

		{\sffamily\large\itshape
			\IfStrEqCase{\ThesisLanguage}{%
				{pl}{\@titleEN}
				{en}{\@titlePL}
			}
		}
		\vspace{\fill}
	\end{center}

	\noindent
	{
		\sffamily
		\thesistable
	}

	\vspace*{17mm}

	\centerline{\small\sffamily Kraków, \@date}

	\clearpage
	\thispagestyle{empty}

	{~}\vspace{20mm}

	\clearpage
	\titlepage

	% Strona z podziękowaniami.
	\IfStrEq{\@acknowledgements}{}{
		\setcounter{page}{3}
	}{

		\vspace*{15cm} \vfill
		\begin{flushright}
			\begin{minipage}[!h]{10cm}
				{\Large\itshape \@acknowledgements}
			\end{minipage}
		\end{flushright}

		\clearpage
		\thispagestyle{empty}

		~ \newpage
		\setcounter{page}{5}
	}
}


% =============================================================================
% SEC:   Ustawienia nagłówków i stopek
% =============================================================================

\RequirePackage{fancyhdr}

\pagestyle{fancy}
\renewcommand{\chaptermark}[1]{\markboth{\thechapter.\ #1}{}}
\renewcommand{\sectionmark}[1]{\markright{\thesection.\ #1}}

\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0.5pt}
\fancyhf{}
\fancyhead{}
\fancyhead[RE,LO]{\slshape{\small \rightmark}}
\fancyhead[RO,LE]{\bfseries \thepage}

\thesisheaders

\frenchspacing
\sloppy
\flushbottom


% =============================================================================
% SEC:   Ustawienia formatowania tytułów rozdziałów, podrozdziałów, itd.
% =============================================================================

\titleformat{\chapter}[block]
{\bfseries\LARGE}{\filright \LARGE\thechapter. }{0ex}{}
%odstępy: lewy, góra, dół
\titlespacing{\chapter}{0pt}{17mm}{19mm}
\titleformat{\section}[block]
{\bfseries\Large}{\filright \Large\thesection. }{0ex}{}
\titlespacing{\section}{7mm}{8mm plus 0mm minus 1mm}{4mm plus 0mm minus 1mm}
\titleformat{\subsection}[block]
{\bfseries\large}{\filright \large\thesubsection. }{0ex}{}
\titlespacing{\subsection}{7mm}{6mm}{2.5mm}
\titleformat{\subsubsection}[block]
{\bfseries\normalsize}{\filright \normalsize\thesubsubsection. }{0ex}{}
\titlespacing{\subsubsection}{7mm}{3mm}{1.5mm}

% Określ maksymalny poziom numeracji (głębsze poziomy nie będą miały numeru).
%   (np. 1 - chapter, 2 - section, itd.)
\setcounter{secnumdepth}{4}


% =============================================================================
% SEC:   Ustawienia generowania spisu treści i spisu rysunków
% =============================================================================

\renewcommand{\cfttoctitlefont}{\bfseries\Large}
\renewcommand{\cftbeforetoctitleskip}{20mm}
\renewcommand{\cftaftertoctitleskip}{19mm}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdot}}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdot}}
\renewcommand{\cftsubsecleader}{\cftdotfill{\cftdot}}
\renewcommand{\cftchapaftersnum}{.}
\renewcommand{\cftsecaftersnum}{.}
\renewcommand{\cftsubsecaftersnum}{.}
\setlength{\cftparskip}{2pt}
\setlength{\cftbeforechapskip}{0mm}
\renewcommand{\cftchappagefont}{\normalsize}


% =============================================================================
% SEC:   Ustawienia wyświetlania liczb (zgodne z polskimi zwyczajami typograficznymi)
% =============================================================================

\RequirePackage{siunitx}

\IfStrEq{\ThesisLanguage}{pl}
{%
    \sisetup{
    	output-decimal-marker = {,},  % symbol dziesiętny
    	%	round-mode=places,
    	%	round-precision=4,
    	group-separator={~},  % separator grupy 3 cyfr
    }
}

% =============================================================================
% SEC:   Ustawienia wyświetlania URL-i
% =============================================================================

% Zmiana kroju czcionki URL-i z czcionki o stałej szerokości na szeryfową z kursywą.
\renewcommand\UrlFont{\rmfamily\itshape}


% =============================================================================
% SEC:   Ustawienia podpisów pod ilustracjami
% =============================================================================

\captionsetup[subfigure]{labelfont=md}
\captionsetup{%
	% Użyj okrągłych nawiasów wokół odwołań do "podilustracji".
	subrefformat=parens,
	% Margines z obu stron podpisu.
	margin=2cm,
	% W przypadku podpisów mieszczących się w jednej linii nie stosuj justowania, tylko wyśrodkuj cały podpis.
	singlelinecheck=on,
}


% =============================================================================
%    SEC:   Konfiguracja bibliografii
% =============================================================================

\RequirePackage[
	style=numeric,
	sorting=none,
	%
	% Zastosuj styl wpisu bibliograficznego właściwy językowi publikacji.
	language=autobib,
	autolang=other,
	% Zapisuj datę dostępu do strony WWW w formacie RRRR-MM-DD.
	urldate=iso,
	seconds=true,
	% Nie dodawaj numerów stron, na których występuje cytowanie.
	backref=false,
	% Podawaj ISBN.
	isbn=true,
	% Nie podawaj URL-i, o ile nie jest to konieczne.
	url=false,
	%
	% Ustawienia związane z polskimi normami dla bibliografii.
	maxbibnames=3,
	% Wybór silnika generowania bibliografii:
	%	backend=bibtex  % - jeżeli używamy BibTeX-a
	backend=biber   % - jeżeli używamy biber-a
]{biblatex}

\RequirePackage{csquotes}
% Ponieważ `csquotes` nie posiada polskiego stylu, można skorzystać z mocno zbliżonego stylu chorwackiego.
\IfStrEq{\ThesisLanguage}{pl}{% 
    \DeclareQuoteAlias{croatian}{polish}
}

\addbibresource{bibliography.bib}

% Nie wyświetlaj wybranych pól.
%\AtEveryBibitem{\clearfield{note}}

\DeclareFieldFormat*{title}{''\textit{#1}''}

% =============================================================================
%    SEC:   Konfiguracja listingów
% =============================================================================

% Użyj czcionki kroju Courier.
\RequirePackage{courier}

\RequirePackage{listings}
\lstloadlanguages{TeX}

\lstset{
	literate={ą}{{\k{a}}}1
		{ć}{{\'c}}1
		{ę}{{\k{e}}}1
		{ó}{{\'o}}1
		{ń}{{\'n}}1
		{ł}{{\l{}}}1
		{ś}{{\'s}}1
		{ź}{{\'z}}1
		{ż}{{\.z}}1
		{Ą}{{\k{A}}}1
		{Ć}{{\'C}}1
		{Ę}{{\k{E}}}1
		{Ó}{{\'O}}1
		{Ń}{{\'N}}1
		{Ł}{{\L{}}}1
		{Ś}{{\'S}}1
		{Ź}{{\'Z}}1
		{Ż}{{\.Z}}1,
	basicstyle=\footnotesize\ttfamily,
}


% =============================================================================
%    SEC:   Konfiguracja tabel
% =============================================================================

\RequirePackage{array}
\RequirePackage{tabularx}
\RequirePackage{multirow}
\RequirePackage{booktabs}
\RequirePackage{makecell}
\RequirePackage[flushleft]{threeparttable}

% defines the X column to use m (\parbox[c]) instead of p (`parbox[t]`)
\newcolumntype{C}[1]{>{\hsize=#1\hsize\centering\arraybackslash}X}

% =============================================================================
%    SEC:   INNE
% =============================================================================

\newcommand{\RedefinePlainStyle}{%
	% Ponowne zdefiniowanie stylu `plain`, aby usunąć numer strony z pierwszej strony spisu treści i poszczególnych rozdziałów.
	\fancypagestyle{plain}
	{
		% Usuń nagłówek i stopkę
		\fancyhf{}
		% Usuń linie.
		\renewcommand{\headrulewidth}{0pt}
		\renewcommand{\footrulewidth}{0pt}
	}
}

\AtBeginDocument{
  \IfStrEq{\ThesisLanguage}{en}{
    \renewcommand{\tablename}{Table}
    \renewcommand{\figurename}{Fig.}
    \renewcommand{\bibname}{Bibliography}
  }{
    \renewcommand{\tablename}{Tabela}
    \renewcommand{\figurename}{Rys.}
    \renewcommand{\bibname}{Bibliografia}
  }
}

% =============================================================================
% SEC:   Niestandardowe środowiska
% =============================================================================

% ----------------------------------------------------------------------------
%    Środowisko do tworzenia opisów symboli użytych w równaniu
% ----------------------------------------------------------------------------

\SetLabelAlign{parright}{\parbox[t]{\labelwidth}{\raggedleft#1}}
\setlist[description]{style=multiline, topsep=10pt, align=parright}

% Odstęp po obu stronach półpauzy.
\newlength{\descriptiondashgap}
\setlength{\descriptiondashgap}{0.5em}

% Element na liście symboli matematycznych użytych w równaniu (symbol wyrównany do prawej, oddzielony półpauzą od definicji)
\renewcommand*\descriptionlabel[1]{\hspace \labelsep \normalfont \bfseries #1 \mdseries\hspace{\descriptiondashgap}--\hspace{\descriptiondashgap}}

% Odległość półpauzy od lewego marginesu.
\newlength{\eqwheremargin}
\setlength{\eqwheremargin}{2cm}

\newenvironment{eqwhere}[1][]
{%
	\setlength{\eqwheremargin}{#1}%
	\begin{description}[leftmargin=\eqwheremargin, itemsep=0cm, labelsep=0cm]
}
{\end{description}}

% =============================================================================
% SEC:   Makra urzytkownika
% =============================================================================

\newcommand{\Lagr}{\mathcal{L}}

% =============================================================================
% SEC:   lst styles
% =============================================================================

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.95}
\lstdefinestyle{matlab-style}{
	language=matlab,
	escapechar=|,
	backgroundcolor=\color{backcolour},
	commentstyle=\color{codegreen},
	keywordstyle=\color{codepurple},
	numberstyle=\tiny\color{codegray},
	stringstyle=\color{codepurple},
	basicstyle=\ttfamily\footnotesize,
	breakatwhitespace=false,
	breaklines=true,
	captionpos=b,
	keepspaces=true,
	numbers=left,
	numbersep=5pt,
	showspaces=false,
	showstringspaces=false,
	showtabs=false,
	tabsize=2
}