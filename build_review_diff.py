"""Generate a marked review against an unchanged digest source.

Expand local input tables, but leave bibliography commands for BibTeX.
The review uses one column to accommodate the digest's original wide tables;
the clean main.tex remains the six-page IEEE two-column manuscript.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def expand_inputs(path, stack=()):
    path = Path(path).resolve()
    if path in stack:
        raise ValueError('Recursive input: ' + str(path))
    content = path.read_text()
    def expand(match):
        target = path.parent / match.group(1)
        if target.suffix != '.tex':
            target = target.with_suffix('.tex')
        return expand_inputs(target, (*stack, path))
    return re.sub(r'\\input\{([^}]+)\}', expand, content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, default=Path('Digest_v1.tex'))
    parser.add_argument('--new', type=Path, default=Path('main.tex'))
    parser.add_argument('--output', type=Path, default=Path('diff.tex'))
    parser.add_argument('--latexdiff', default='latexdiff')
    args = parser.parse_args()
    baseline_hash = hashlib.sha256(args.baseline.read_bytes()).hexdigest()
    table_definitions = []
    table_commands = []
    def atomic_tables(text, side):
        count = 0
        def atomic(match):
            nonlocal count
            # The original schema retains its rows and columns. Let latexdiff
            # mark only its corrected values, rather than replacing the table.
            if r'\label{tab:dataset_schema}' in match.group(0):
                return match.group(0)
            command = 'APECReview' + side + 'Table' + chr(65+count)
            count += 1
            table = match.group(0)
            if side == 'Old':
                # Avoid duplicate labels for the old and updated schema tables.
                table = re.sub(r'\\label\{([^}]+)\}', r'\\label{\1_digest}', table)
            # Mark cells separately: ulem cannot wrap a whole table float.
            marker = r'\DIFdel' if side == 'Old' else r'\DIFadd'
            def mark_cell(cell):
                cell = cell.strip()
                stack = re.fullmatch(r'\\shortstack\{(.*)\}',cell,re.S)
                if stack:
                    return r'\shortstack{' + r'\\'.join(
                        marker+'{'+line+'}' for line in stack.group(1).split(r'\\')) + '}'
                span = re.fullmatch(r'(\\multicolumn\{[^}]+\}\{[^}]+\})\{(.*)\}',cell,re.S)
                if span:
                    return span.group(1)+'{'+marker+'{'+span.group(2)+'}}'
                return marker+'{'+cell+'}'
            rows = []
            for line in table.splitlines():
                stripped = line.strip()
                if stripped.endswith(r'\\'):
                    cells = stripped[:-2].split('&')
                    line = ' & '.join(mark_cell(cell) for cell in cells) + r' \\'
                rows.append(line)
            table = '\n'.join(rows)
            table = re.sub(r'\\caption\{([^{}]+)\}',
                lambda m:r'\caption{'+marker+'{'+m.group(1)+'}}',table)
            color = 'red' if side == 'Old' else 'blue'
            table = table.replace(r'\centering',r'\centering\color{'+color+'}',1)
            table_definitions.append('\\newcommand{\\'+command+'}{%\n'+table+'\n}\n')
            table_commands.append(command)
            return '\\'+command+'{}\n'
        return re.sub(r'\\begin\{(table\*?)\}.*?\\end\{\1\}',atomic,text,flags=re.S)
    with tempfile.TemporaryDirectory(prefix='apec-diff-') as directory:
        old = Path(directory)/'old.tex'
        new = Path(directory)/'new.tex'
        # Equivalent Unicode/TeX dash spellings are formatting, not prose edits.
        def normalize_dashes(text):
            text = text.replace('—','---').replace('–','--')
            return re.sub(r'(\\begin\{figure\*?\})[ \t]+(?=\[)', r'\1', text)
        old.write_text(atomic_tables(normalize_dashes(expand_inputs(args.baseline)),'Old'))
        new.write_text(atomic_tables(normalize_dashes(expand_inputs(args.new)),'New'))
        command = [args.latexdiff, '--type=CFONT', '--subtype=SAFE', '--floattype=FLOATSAFE',
            '--graphics-markup=none', '--math-markup=0',
            '--append-safecmd='+','.join(table_commands), str(old), str(new)]
        result = subprocess.run(command, text=True, capture_output=True, check=True)
    content = result.stdout
    clean_class = r'\documentclass[conference,letterpaper]{IEEEtran}'
    assert content.count(clean_class) == 1
    content = content.replace(clean_class, r'\documentclass[conference,onecolumn,letterpaper]{IEEEtran}', 1)
    compatibility = (r'\usepackage{float}'+'\n'+r'\providecommand{\bstctlcite}[1]{}'+'\n'
        +r'\usepackage[normalem]{ulem}'+'\n'
        +r'\emergencystretch=3em'+'\n'
        +r'\renewcommand{\DIFadd}[1]{{\protect\color{blue}\protect\uline{#1}}}'+'\n'
        +r'\renewcommand{\DIFdel}[1]{{\protect\color{red}\protect\sout{#1}}}'+'\n'
        +''.join(table_definitions))
    content = content.replace(r'\begin{document}', compatibility+r'\begin{document}', 1)
    # Table content already has cell-level marks; avoid wrapping its float.
    content = re.sub(r'\\DIF(?:add|del)\{\s*(\\APECReview(?:Old|New)Table[A-Z]\{\})\s*\}',
        lambda m:m.group(1),content)
    # math-markup=0 keeps display equations compilable. Mark newly labelled
    # equations explicitly so they are also distinguishable in a printed review.
    baseline_labels = set(re.findall(r'\\label\{([^}]+)\}', expand_inputs(args.baseline)))
    def mark_new_equation(match):
        body = match.group(1)
        labels = re.findall(r'\\label\{([^}]+)\}', body)
        if not labels or any(label in baseline_labels for label in labels):
            return match.group(0)
        label_commands = ''.join(r'\label{'+label+'}' for label in labels)
        body = re.sub(r'\\label\{[^}]+\}', '', body).strip()
        return (r'{\color{blue}\begin{equation}\underline{\displaystyle '+body+'}'
                +label_commands+r'\end{equation}}')
    content = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}',
        mark_new_equation, content, flags=re.S)
    # Keep citations/references together inside underline/strikethrough arguments.
    content = re.sub(r'\\(?:cite|ref|eqref)\{[^}]+\}',
        lambda m:r'\mbox{'+m.group(0)+'}',content)
    content = content.replace(r'\maketitle',r'''\maketitle
\pagestyle{plain}\thispagestyle{plain}
\begin{center}\footnotesize Review copy: \textcolor{blue}{\uline{added text}}; \textcolor{red}{\sout{removed text}}.\end{center}''',1)
    # The digest's removed pipeline figure used this legacy label. Keep the
    # deleted prose's reference resolvable at the updated architecture figure.
    content = content.replace(r'\label{fig:model_structure}',
        r'\label{fig:model_structure}\label{architecture}',1)
    # This legacy-font review renders Unicode dashes through their TeX commands.
    content = content.replace('—',r'\textemdash{}').replace('–',r'\textendash{}')
    content = re.sub(r'\\includegraphics(?:\[[^\n]*?\])?\{',
        lambda match:r'\includegraphics[width=.9\linewidth,height=.4\textheight,keepaspectratio]{',content)
    comment = ('% Marked comparison: unchanged Digest_v1.tex -> main.tex.\n'
        '% One-column REVIEW layout accommodates original wide digest tables.\n'
        '% Compile main.tex for the clean six-page conference manuscript.\n'
        '% Additions have a blue underline; deletions have a red strikethrough for printing.\n'
        '% The schema has word-level changes; changed table cells are marked individually.\n'
        '% Replaced comparison/new analysis tables are marked as whole blocks.\n'
        '% Review graphics are bounded in size; the clean main.tex is unchanged.\n')
    content = "\n".join(line.rstrip() for line in content.splitlines())+"\n"
    args.output.write_text(comment+content)
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == baseline_hash
    results = args.output.parent/'results'
    results.mkdir(exist_ok=True)
    (results/'diff_generation.json').write_text(json.dumps(dict(
        tool='latexdiff 1.3.2', baseline='Digest_v1.tex',
        baseline_sha256=baseline_hash, new_source='main.tex',
        new_sha256=hashlib.sha256(args.new.read_bytes()).hexdigest(),
        baseline_modified=False, clean_source_modified=False,
        input_tables_expanded=True, bibliography_not_flattened=True,
        schema_table_word_level=True, replacement_and_new_tables_marked_as_whole_blocks=True,
        equivalent_dash_spellings_normalized_for_comparison=True,
        review_graphics_size_bounded=True,
        deleted_text_style='red strikethrough using ulem; deleted table cells marked individually',
        added_text_style='blue solid underline using ulem; new table cells marked individually',
        print_legend_and_page_numbers=True, new_display_equations_blue_underlined=True,
        legacy_architecture_label_retained_in_review=True,
        review_layout='IEEEtran conference onecolumn; main.tex stays twocolumn',
        generator_stderr=result.stderr),indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output), baseline_unchanged=True,
        inserted_diff_markers=len(re.findall(r'\\DIF(?:add|del)',content)))))


if __name__=='__main__':
    main()
