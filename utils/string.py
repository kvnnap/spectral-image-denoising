from pathlib import Path

def extract_file_extension(file_path):
    return Path(file_path).suffix

def extract_file_name(file_path):
    return Path(file_path).stem

def concat_paths(a, b):
    return str(Path(a).joinpath(b))

def comma_to_list(str):
    str = str.strip().lower()
    return list(map(lambda x: x.strip(), str.split(','))) if str else []

def get_prefix(text, steps = -1):
    return '_'.join(text.split('_')[:steps])

def get_suffix(text, steps = -1):
    return text.split('_')[steps]

def tables_to_csv(tables):
    # tables to csv/latex etc
    csvStr = ''
    for i, table in enumerate(tables):
        csvStr += f'Samples 4^{i}\n'
        for row in table:
            csvStr += ','.join(row) + '\n'
        csvStr += '\n\n'
    return csvStr

def array_to_latex_table(array):
    lStr = "\\begin{table}\n"
    lStr += "\\centering\n"
    lStr += "\\begin{tabular}{|" + "c|" * len(array[0]) + "}\n"
    lStr += "\\hline\n"
    
    head, *tail = array
    lStr += " & ".join(map(lambda x: f'\\textbf{{{x}}}', head)) + " \\\\\n"
    lStr += "\\hline\n"
    for row in tail:
        # row[0] = f'\\textsc{{{str(row[0])}}}'
        # row[1] = str(row[1]).upper()
        lStr += " & ".join(map(str, row)) + " \\\\\n"
    
    lStr += "\\hline\n"
    lStr += "\\end{tabular}\n"
    lStr += "\\caption{Your caption here.}\n"
    lStr += "\\label{tab:my_table}\n"
    lStr += "\\end{table}\n"
    
    return lStr

def tables_to_latex(tables):
    # tables to csv/latex etc
    lStr = ''
    for i, table in enumerate(tables):
        lStr += f'Samples 4^{i}\n'
        lStr += array_to_latex_table(table)
        lStr += '\n\n'
    return lStr