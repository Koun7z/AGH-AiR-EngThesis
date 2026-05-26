$out_dir = 'latex-build';
$aux_dir = 'latex-build';

$pdf_mode = 1;           # Build PDF
$interaction = 'nonstopmode';
$diagnostics = 1;

$pdflatex = 'pdflatex -file-line-error -synctex=1 -interaction=nonstopmode';

#Use biber instead of bibtex:
$bibtex_use = 2;
