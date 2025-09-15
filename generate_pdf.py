#!/usr/bin/env python3
"""
Generador de PDFs estéticos con logo y fuentes monospace
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def load_score_data(json_file):
    """Carga los datos de calificación desde un archivo JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        return None

def format_comments_with_bullets(comments):
    """Formatea los comentarios para mostrar bullet points correctamente en LaTeX"""
    if not comments:
        return "Sin comentarios"
    
    # Primero, dividir por líneas reales
    lines = comments.split('\n')
    all_lines = []
    
    # Procesar cada línea para detectar bullet points embebidos
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Si la línea empieza con bullet point (-), agregar directamente
        if line.startswith('- '):
            all_lines.append(line)
        elif line.startswith('•'):
            all_lines.append(line)
        else:
            # Buscar bullet points embebidos en el texto
            # Dividir por " - " para separar bullet points
            parts = line.split(' - ')
            if len(parts) > 1:
                # El primer parte es texto normal
                if parts[0].strip():
                    all_lines.append(parts[0].strip())
                # Los demás son bullet points
                for part in parts[1:]:
                    if part.strip():
                        all_lines.append(f"- {part.strip()}")
            else:
                # No hay bullet points, agregar como está
                all_lines.append(line)
    
    # Ahora procesar las líneas para formatear
    formatted_lines = []
    has_bullets = False
    
    for line in all_lines:
        line = line.strip()
        if not line:
            continue
            
        # Si la línea empieza con bullet point (-), formatear como itemize
        if line.startswith('- '):
            # Remover el bullet point y el espacio
            content = line[2:].strip()
            if content:
                formatted_lines.append(f"\\item {content}")
                has_bullets = True
        elif line.startswith('•'):
            # También manejar bullet points con •
            content = line[1:].strip()
            if content:
                formatted_lines.append(f"\\item {content}")
                has_bullets = True
        else:
            # Si no es bullet point, agregar como párrafo normal
            formatted_lines.append(line)
    
    # Si hay items, envolver en itemize
    if has_bullets:
        result = "\\begin{itemize}\n"
        for line in formatted_lines:
            if line.startswith('\\item'):
                result += f"  {line}\n"
            else:
                # Si no es un item, agregarlo como párrafo antes del itemize
                if line and not line.startswith('\\item'):
                    result += f"  \\item {line}\n"
        result += "\\end{itemize}"
        return result
    else:
        # Si no hay items, devolver como párrafo normal con saltos de línea
        return '\\\\\n'.join(formatted_lines)

def create_latex_document(score_data, student_id):
    """Crea un documento LaTeX estético"""
    
    latex = f"""\\documentclass[11pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[spanish]{{babel}}
\\usepackage{{lmodern}}
\\usepackage{{textcomp}}
\\usepackage{{selinput}}
\\SelectInputMappings{{
  adieresis={{ä}},
  eacute={{é}},
  ntilde={{ñ}},
  uacute={{ú}},
  iacute={{í}},
  oacute={{ó}},
  aacute={{á}},
  egrave={{è}},
  igrave={{ì}},
  ograve={{ò}},
  agrave={{à}},
  ccedilla={{ç}},
  uumlaut={{ü}},
  oumlaut={{ö}},
  aumlaut={{ä}}
}}
\\usepackage[letterpaper,top=3cm,bottom=2cm,left=2cm,right=2cm]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage{{listings}}
\\usepackage{{booktabs}}
\\usepackage{{array}}

% Sin indentación en párrafos
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{0.5em}}

% Sin indentación en títulos
\\usepackage{{titlesec}}
\\titleformat{{\\section}}{{\\Large\\bfseries}}{{}}{{0pt}}{{}}
\\titleformat{{\\subsection}}{{\\large\\bfseries}}{{}}{{0pt}}{{}}
\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries}}{{}}{{0pt}}{{}}

% Sin indentación en listas
\\usepackage{{enumitem}}
\\setlist{{leftmargin=0pt,itemindent=0pt}}

% Sin indentación en todo el documento
\\raggedright

% Sin indentación en listings
\\lstset{{
    basicstyle=\\small,
    breaklines=true,
    frame=none,
    backgroundcolor=\\color{{white}},
    commentstyle=\\color{{commentgreen}},
    keywordstyle=\\color{{codeblue}},
    stringstyle=\\color{{red}},
    showstringspaces=false,
    numbers=none,
    tabsize=2,
    columns=flexible,
    keepspaces=true,
    fontadjust=true,
    xleftmargin=0pt,
    xrightmargin=0pt
}}

% Colores personalizados
\\definecolor{{codeblue}}{{RGB}}{{41, 128, 185}}
\\definecolor{{commentgreen}}{{RGB}}{{39, 174, 96}}
\\definecolor{{scoreorange}}{{RGB}}{{230, 126, 34}}
\\definecolor{{headerblue}}{{RGB}}{{52, 73, 94}}
\\definecolor{{lightgray}}{{RGB}}{{245, 245, 245}}


% Headers y footers
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\includegraphics[height=1cm]{{public/ibero.png}}}}
\\fancyhead[R]{{\\textbf{{Reporte de Calificaciones}}}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}
\\setlength{{\\headheight}}{{15pt}}

\\begin{{document}}

% Título principal
\\begin{{center}}
\\Large\\textbf{{\\color{{headerblue}}Reporte de Calificaciones}}\\\\[0.5cm]
\\large\\textbf{{{student_id.upper()}}}\\\\[0.3cm]
\\normalsize Fecha de evaluación: {datetime.now().strftime('%d de %B de %Y')}
\\end{{center}}

\\vspace{{0.5cm}}
\\hrule
\\vspace{{0.5cm}}

"""

    # Procesar cada ejercicio
    exercises = ['operaciones', 'resistencia', 'conversionCmsMts', 'conversionSegHMS']
    total_score = 0
    exercise_count = 0
    
    for exercise in exercises:
        # Try both with and without .c extension
        exercise_key = exercise
        if exercise_key not in score_data:
            exercise_key = f"{exercise}.c"
        
        if exercise_key in score_data:
            score = score_data[exercise_key].get('calificacion', 0)
            comments = score_data[exercise_key].get('comentarios', 'Sin comentarios')
            
            # Determinar símbolo según el ejercicio
            exercise_symbols = {
                'operaciones': '⚙',
                'resistencia': '⚡',
                'conversionCmsMts': '📏',
                'conversionSegHMS': '🕐'
            }
            symbol = exercise_symbols.get(exercise, '💻')
            
            # Determinar color de calificación
            if score >= 8:
                score_latex = f"\\textcolor{{commentgreen}}{{\\textbf{{{score}/10}}}}"
            elif score >= 6:
                score_latex = f"\\textcolor{{scoreorange}}{{\\textbf{{{score}/10}}}}"
            else:
                score_latex = f"\\textcolor{{red}}{{\\textbf{{{score}/10}}}}"
            
            # Capitalizar correctamente el nombre del ejercicio
            exercise_name = exercise.replace('conversionCmsMts', 'ConversionCmsMts').replace('conversionSegHMS', 'ConversionSegHMS').capitalize()
            
            # Procesar comentarios para formatear bullet points
            formatted_comments = format_comments_with_bullets(comments)
            
            latex += f"""
\\section*{{{symbol} {exercise_name}.c}}

\\begin{{minipage}}{{\\textwidth}}
\\textbf{{Calificación:}} {score_latex}\\\\[0.3cm]

\\textbf{{Comentarios del evaluador:}}\\\\[0.2cm]
\\begin{{minipage}}{{\\textwidth}}
\\small
{formatted_comments}
\\end{{minipage}}
\\end{{minipage}}

\\vspace{{0.5cm}}
\\hrule
\\vspace{{0.3cm}}

"""
            total_score += score
            exercise_count += 1
    
    # Resumen general
    if exercise_count > 0:
        average = total_score / exercise_count
        latex += f"""
\\section*{{🏆 Resumen General}}

\\begin{{center}}
\\begin{{tabular}}{{l r}}
\\toprule
\\textbf{{Métrica}} & \\textbf{{Valor}} \\\\\\\\
\\midrule
Calificación Total & {total_score}/{exercise_count * 10} \\\\\\\\
Promedio & {average:.2f}/10 \\\\\\\\
\\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{1cm}}
\\begin{{center}}
\\textbf{{Prof. Edgar Ortiz}}\\\\[0.2cm]
\\small\\textit{{Sistema de Evaluación Automática}}
\\end{{center}}

\\end{{document}}
"""
    
    return latex

def generate_pdf_from_latex(latex_content, output_file):
    """Genera PDF desde LaTeX con timeout"""
    try:
        # Crear archivo .tex temporal
        tex_file = output_file.replace('.pdf', '.tex')
        with open(tex_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(latex_content)
        
        # Compilar con pdflatex (soporte completo para diacríticos con lmodern)
        print("Compilando LaTeX con pdflatex...")
        cmd = ['pdflatex', '-interaction=nonstopmode', tex_file]
        
        # Ejecutar con timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        
        # Verificar si el PDF fue generado exitosamente
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✅ PDF generado exitosamente: {output_file}")
            # Limpiar archivos auxiliares
            for ext in ['.aux', '.log', '.tex']:
                aux_file = output_file.replace('.pdf', ext)
                if os.path.exists(aux_file):
                    os.remove(aux_file)
            return True
        else:
            print(f"❌ Error al compilar LaTeX:")
            if result.stderr:
                print(result.stderr[-500:])  # Mostrar últimos 500 caracteres del error
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: LaTeX tardó demasiado en compilar")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python generate_aesthetic_pdf.py <archivo.json>")
        print("Ejemplo: python generate_aesthetic_pdf.py msc25ahl.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    student_id = Path(json_file).stem
    
    # Cargar datos
    score_data = load_score_data(json_file)
    if not score_data:
        sys.exit(1)
    
    print(f"🎓 Generando PDF estético para: {student_id}")
    
    # Crear documento LaTeX
    latex_content = create_latex_document(score_data, student_id)
    
    # Generar PDF
    output_file = f"calificaciones_{student_id}.pdf"
    if generate_pdf_from_latex(latex_content, output_file):
        print(f"🎉 ¡PDF generado exitosamente: {output_file}")
        print(f"📄 El archivo incluye:")
        print(f"   • Logo de la universidad (tamaño optimizado)")
        print(f"   • Fuente Computer Modern (soporte completo para español)")
        print(f"   • Configuración de página optimizada (sin overflow)")
        print(f"   • Sin indentación en párrafos, títulos y comentarios")
        print(f"   • Comentarios sin marco (más limpio)")
        print(f"   • Colores diferenciados por calificación")
        print(f"   • Símbolos para cada ejercicio")
        print(f"   • Firma del Prof. Edgar Ortiz")
        print(f"   • Tabla de resumen profesional")
    else:
        print("💥 Error al generar PDF")

if __name__ == "__main__":
    main()
