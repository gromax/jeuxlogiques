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
corrected_lines = []
correction_needed = False
for line in lines:
    corrected_lines.append(line)
    if "#" in line:
        line = line.split("#", 1)[0]  # Remove comments after '#'
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
        # on veur rectifier le https par un id type tatham si possible
        if len(parts) > 1 and parts[1].startswith("https") and "%id=" in result.stdout:
            correction_needed = True
            id_part = result.stdout.split("%id=", 1)[1].splitlines()[0].strip()
            if id_part.endswith("%"):
                # dans le tex on ajoute des % en fin de ligne
                id_part = id_part[:-1].strip()
            corrected_lines[-1] = f"{parts[0]} {id_part} #{parts[1]}\n"

base_tex = base_tex.replace("--CONTENT--", content)

outfilename = filename.replace(".txt", ".tex") if filename.endswith(".txt") else filename + ".tex"

with open(outfilename, "w", encoding="utf-8") as f:
    f.write(base_tex)

# réécriture du fichier source avec les corrections
if correction_needed:
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(corrected_lines)

