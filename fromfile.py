"""
fromfile.py

construit le fichiet tex à partir d'un fichier de commandes
"""

import subprocess
import sys

HABILLAGE = """
\\begin{minipage}{.49\\linewidth}
\\label{--LABEL--}

\\begin{center}
\\textbf{--LABEL--}

\\medskip

--content--
\\end{center}
\\end{minipage}
"""

def replacement(line:str, repl:str, text:str) -> str:
    """
    cherche le bout suivant "=" dans texte s'il y en a (sinon rien)
    et remplace repl dans text
    """
    parts = line.split("=", 1)
    value = parts[1].strip() if len(parts) > 1 else ""
    return text.replace(repl, value)


if len(sys.argv) != 2:
    print("Usage : python.exe fromfile.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open("./inc/base.tex", "r", encoding="utf-8") as f:
    base_tex = f.read()

with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()

content = ""
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue  # Ignore empty lines and comments
    LINE = line.upper()
    if LINE.startswith("TITLE"):
        base_tex = replacement(line, "--TITLE--", base_tex)
    elif LINE.startswith("AUTHOR"):
        base_tex = replacement(line, "--AUTHOR--", base_tex)
    elif LINE.startswith("LHEAD"):
        base_tex = replacement(line, "--LHEAD--", base_tex)
    elif LINE.startswith("FOOT"):
        base_tex = replacement(line, "--FOOT--", base_tex)
    else:
        parts = [item.strip() for item in line.split(" ") if item]
        result = subprocess.run(["python", "main.py"] + parts, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing command '{line}': {result.stderr}")
            sys.exit(1)
        add_content = HABILLAGE.replace("--LABEL--", parts[0]).replace("--content--", result.stdout.strip())
        content += "\n" + add_content

base_tex = base_tex.replace("--CONTENT--", content)

outfilename = filename.replace(".txt", ".tex") if filename.endswith(".txt") else filename + ".tex"

with open(outfilename, "w", encoding="utf-8") as f:
    f.write(base_tex)

