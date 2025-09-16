#!/usr/bin/env python3
"""
Generador de PDFs estéticos para resultados de pruebas de C
Basado en CSV de resultados de testing
"""

import csv
import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def load_csv_data(csv_file):
    """Carga los datos de testing desde un archivo CSV"""
    try:
        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Use csv.Sniffer to detect delimiter and handle malformed CSV
            sample = f.read(1024)
            f.seek(0)
            
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
            except:
                delimiter = ','  # Default to comma if detection fails
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_num, row in enumerate(reader, 1):
                # Skip malformed rows (rows with wrong number of fields)
                if len(row) < 10:  # Expected number of CSV columns
                    print(f"⚠️  Advertencia: Saltando fila {row_num} malformada en CSV")
                    continue
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {csv_file}")
        return None
    except Exception as e:
        print(f"Error al leer CSV: {e}")
        return None

def calculate_program_scores(csv_data):
    """Calcula puntuaciones por programa basado en los resultados de testing"""
    # Lista de programas esperados
    expected_programs = ['operaciones.c', 'conversionCmsMts.c', 'conversionSegsHMS.c', 'resistencia.c']
    
    program_scores = defaultdict(lambda: {'total_score': 0, 'max_score': 0, 'tests': 0, 'passed': 0, 'failed': 0, 'compilation_errors': 0, 'exists': False})
    
    for row in csv_data:
        program = row['Program_Name']
        
        # Handle Test_Score conversion safely
        try:
            test_score = int(row.get('Test_Score', 0))
        except (ValueError, TypeError):
            # If Test_Score is not a valid integer, default to 0
            test_score = 0
        
        status = row['Test_Status']
        compilation_status = row['Compilation_Status']
        
        # Solo marcar como existente si no es un archivo faltante
        if compilation_status != 'NO_FILE':
            program_scores[program]['exists'] = True
            program_scores[program]['tests'] += 1
            program_scores[program]['total_score'] += test_score
            program_scores[program]['max_score'] += 10  # Each test is worth 10 points
            
            if status == 'PASS':
                program_scores[program]['passed'] += 1
            elif status == 'FAIL':
                program_scores[program]['failed'] += 1
                
            if compilation_status == 'COMPILE_ERROR':
                program_scores[program]['compilation_errors'] += 1
    
    # Calcular penalización por programas faltantes
    missing_programs = [prog for prog in expected_programs if not program_scores[prog]['exists']]
    total_expected_programs = len(expected_programs)
    programs_found = total_expected_programs - len(missing_programs)
    
    # Agregar información sobre programas faltantes
    program_scores['_metadata'] = {
        'expected_programs': expected_programs,
        'missing_programs': missing_programs,
        'programs_found': programs_found,
        'total_expected': total_expected_programs,
        'penalty_factor': programs_found / total_expected_programs  # Factor de penalización
    }
    
    return program_scores

def format_test_results_table(csv_data, program_name):
    """Formatea los resultados de testing en una tabla profesional para un programa específico"""
    program_tests = [row for row in csv_data if row['Program_Name'] == program_name]
    
    if not program_tests:
        return "No hay pruebas disponibles para este programa."
    
    # Crear tabla LaTeX profesional con mejor formato para texto largo
    table_rows = []
    table_rows.append("\\begin{center}")
    table_rows.append("\\resizebox{\\textwidth}{!}{%")
    table_rows.append("\\begin{tabular}{|c|p{2.5cm}|p{5cm}|p{5cm}|c|}")
    table_rows.append("\\hline")
    table_rows.append("\\rowcolor{lightgray}")
    table_rows.append("\\textbf{Prueba} & \\textbf{Entrada} & \\textbf{Esperado} & \\textbf{Resultado} & \\textbf{Estado} \\\\")
    table_rows.append("\\hline")
    
    for i, test in enumerate(program_tests, 1):
        # Limpiar y formatear texto para LaTeX
        input_clean = test['Input_Values'].replace('\\', '\\textbackslash ').replace('{', '\\{').replace('}', '\\}')
        expected_clean = test['Expected_Result'].replace('\\', '\\textbackslash ').replace('{', '\\{').replace('}', '\\}')
        # Para el resultado actual, usar espacios para separar líneas y mantener en la celda
        actual_clean = test['Actual_Result'].replace(chr(10), ' | ').replace(chr(13), '').replace('\\', '\\textbackslash ').replace('{', '\\{').replace('}', '\\}')
        
        # No truncar texto - mostrar salida completa
        # Los textos largos se ajustarán automáticamente con resizebox
            
        # Estado con colores
        if test['Test_Status'] == 'PASS':
            status = "\\textcolor{commentgreen}{\\textbf{PASS}}"
        else:
            status = "\\textcolor{red}{\\textbf{FAIL}}"
        
        # Alternar colores de fila
        if i % 2 == 0:
            table_rows.append("\\rowcolor{lightgray}")
        
        table_rows.append(f"{i} & {input_clean} & {expected_clean} & {actual_clean} & {status} \\\\")
        table_rows.append("\\hline")
    
    table_rows.append("\\end{tabular}")
    table_rows.append("}%")
    table_rows.append("\\end{center}")
    
    return "\n".join(table_rows)

def create_latex_document(csv_data, program_scores, student_id, output_dir='.'):
    """Crea un documento LaTeX estético para resultados de testing"""
    
    # Determinar la ruta correcta de la imagen basada en el directorio de salida
    if output_dir == '.' or output_dir == '':
        image_path = "public/ibero.png"
    else:
        image_path = "../public/ibero.png"
    
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
\\usepackage[letterpaper,top=3cm,bottom=3cm,left=2cm,right=2cm]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage{{listings}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
\\usepackage{{colortbl}}
\\usepackage{{longtable}}
\\usepackage{{adjustbox}}
\\usepackage{{makecell}}

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

% Colores personalizados
\\definecolor{{codeblue}}{{RGB}}{{41, 128, 185}}
\\definecolor{{commentgreen}}{{RGB}}{{39, 174, 96}}
\\definecolor{{scoreorange}}{{RGB}}{{230, 126, 34}}
\\definecolor{{headerblue}}{{RGB}}{{52, 73, 94}}
\\definecolor{{lightgray}}{{RGB}}{{245, 245, 245}}

% Headers y footers
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\includegraphics[height=1cm]{{{image_path}}}}}
\\fancyhead[R]{{\\textbf{{Reporte de Pruebas de Ejecución}}}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}
\\setlength{{\\headheight}}{{35pt}}

% Footer positioning - geometry package handles this
% \\setlength{{\\footskip}}{{1cm}}

\\begin{{document}}

% Título principal
\\begin{{center}}
\\Large\\textbf{{\\color{{headerblue}}Reporte de Pruebas de Ejecución}}\\\\[0.5cm]
\\large\\textbf{{{student_id.upper()}}}\\\\[0.3cm]
\\normalsize Fecha de evaluación: {datetime.now().strftime('%d de %B de %Y')}
\\end{{center}}

\\vspace{{0.5cm}}
\\hrule
\\vspace{{0.5cm}}

"""

    # Procesar cada programa
    program_order = ['operaciones.c', 'conversionCmsMts.c', 'conversionSegsHMS.c', 'resistencia.c']
    program_names = {
        'operaciones.c': 'Operaciones Básicas',
        'conversionCmsMts.c': 'Conversión Centímetros a Metros',
        'conversionSegsHMS.c': 'Conversión Segundos a Horas-Minutos-Segundos',
        'resistencia.c': 'Cálculo de Resistencia Eléctrica'
    }
    
    total_score = 0
    total_max_score = 0
    program_count = 0
    
    for i, program in enumerate(program_order, 1):
        if program in program_scores:
            scores = program_scores[program]
            program_name = program_names.get(program, program.replace('.c', '').title())
            
            # Calcular porcentaje
            percentage = (scores['total_score'] / scores['max_score'] * 100) if scores['max_score'] > 0 else 0
            
            # Determinar color de calificación
            if percentage >= 80:
                score_latex = f"\\textcolor{{commentgreen}}{{\\textbf{{{scores['total_score']}/{scores['max_score']} ({percentage:.1f}\\%)}}}}"
            elif percentage >= 60:
                score_latex = f"\\textcolor{{scoreorange}}{{\\textbf{{{scores['total_score']}/{scores['max_score']} ({percentage:.1f}\\%)}}}}"
            else:
                score_latex = f"\\textcolor{{red}}{{\\textbf{{{scores['total_score']}/{scores['max_score']} ({percentage:.1f}\\%)}}}}"
            
            # Formatear resultados de testing en tabla
            test_results_table = format_test_results_table(csv_data, program)
            
            # Crear tabla de resumen del programa
            summary_table = f"""
\\begin{{table}}[h!]
\\centering
\\begin{{tabular}}{{l|c|c|c|c}}
\\hline
\\rowcolor{{lightgray}}
\\textbf{{Métrica}} & \\textbf{{Valor}} & \\textbf{{Puntuación}} & \\textbf{{Porcentaje}} & \\textbf{{Estado}} \\\\\\\\
\\hline
Pruebas Ejecutadas & {scores['tests']} & - & - & - \\\\\\\\
Pruebas Exitosas & {scores['passed']} & - & - & \\textcolor{{commentgreen}}{{\\textbf{{PASS}}}} \\\\\\\\
Pruebas Fallidas & {scores['failed']} & - & - & \\textcolor{{red}}{{\\textbf{{FAIL}}}} \\\\\\\\
Errores Compilación & {scores['compilation_errors']} & - & - & \\textcolor{{red}}{{\\textbf{{ERROR}}}} \\\\\\\\
\\hline
\\rowcolor{{lightgray}}
\\textbf{{TOTAL}} & \\textbf{{{scores['tests']}}} & \\textbf{{{scores['total_score']}/{scores['max_score']}}} & \\textbf{{{percentage:.1f}\\%}} & {score_latex} \\\\\\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""
            
            latex += f"""
\\vspace{{0.5cm}}
\\section*{{\\textbf{{{i}.}} {program_name}}}

{summary_table}

\\vspace{{0.5cm}}
\\textbf{{Resultados Detallados de Pruebas:}}\\\\[0.3cm]
{test_results_table}

\\vspace{{0.5cm}}
\\hrule
\\vspace{{0.3cm}}

"""
            total_score += scores['total_score']
            total_max_score += scores['max_score']
            program_count += 1
    
    # Resumen general
    if program_count > 0:
        # Aplicar penalización por programas faltantes
        metadata = program_scores.get('_metadata', {})
        penalty_factor = metadata.get('penalty_factor', 1.0)
        missing_programs = metadata.get('missing_programs', [])
        
        # Calcular porcentaje base
        base_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
        
        # Aplicar penalización: si faltan programas, reducir el porcentaje
        overall_percentage = base_percentage * penalty_factor
        
        # Determinar calificación global
        if overall_percentage >= 90:
            grade_color = "\\textcolor{commentgreen}{\\textbf{EXCELENTE}}"
            grade_text = "EXCELENTE"
        elif overall_percentage >= 80:
            grade_color = "\\textcolor{commentgreen}{\\textbf{BIEN}}"
            grade_text = "BIEN"
        elif overall_percentage >= 70:
            grade_color = "\\textcolor{scoreorange}{\\textbf{REGULAR}}"
            grade_text = "REGULAR"
        elif overall_percentage >= 60:
            grade_color = "\\textcolor{scoreorange}{\\textbf{SUFICIENTE}}"
            grade_text = "SUFICIENTE"
        else:
            grade_color = "\\textcolor{red}{\\textbf{INSUFICIENTE}}"
            grade_text = "INSUFICIENTE"
        
        # Información sobre programas faltantes
        missing_info = ""
        if missing_programs:
            missing_list = ", ".join([prog.replace('.c', '') for prog in missing_programs])
            missing_info = f"\\\\\\midrule\nProgramas Faltantes & {missing_list} \\\\\\\\\nPenalización Aplicada & {(1-penalty_factor)*100:.1f}\\% \\\\\\\\"
        
        latex += f"""
\\vspace{{1cm}}
\\section*{{\\textbf{{Resumen General de Ejecución}}}}

\\begin{{center}}
\\begin{{tabular}}{{l r}}
\\toprule
\\textbf{{Métrica}} & \\textbf{{Valor}} \\\\\\\\
\\midrule
Puntuación Total & {total_score}/{total_max_score} puntos \\\\\\\\
Porcentaje Base & {base_percentage:.1f}\\% \\\\\\\\
Programas Evaluados & {program_count}/{metadata.get('total_expected', 4)} \\\\\\\\
{missing_info}
\\midrule
\\textbf{{Porcentaje Final}} & \\textbf{{{overall_percentage:.1f}\\%}} \\\\\\\\
Calificación & {grade_color} \\\\\\\\
\\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.5cm}}
\\begin{{center}}
\\textbf{{Interpretación de Calificaciones:}}\\\\[0.3cm]
\\begin{{itemize}}
\\item \\textcolor{{commentgreen}}{{\\textbf{{90-100\\%: EXCELENTE}}}} - Todos los programas funcionan perfectamente
\\item \\textcolor{{commentgreen}}{{\\textbf{{80-89\\%: BIEN}}}} - La mayoría de programas funcionan correctamente
\\item \\textcolor{{scoreorange}}{{\\textbf{{70-79\\%: REGULAR}}}} - Algunos programas necesitan corrección
\\item \\textcolor{{scoreorange}}{{\\textbf{{60-69\\%: SUFICIENTE}}}} - Varios programas requieren mejoras
\\item \\textcolor{{red}}{{\\textbf{{0-59\\%: INSUFICIENTE}}}} - Necesita revisar y corregir los programas
\\end{{itemize}}
\\end{{center}}

\\vspace{{1cm}}
\\begin{{center}}
\\textbf{{Prof. Edgar Ortiz}}\\\\[0.2cm]
\\end{{center}}

\\end{{document}}
"""
    
    return latex

def save_evaluation_results(student_id, program_scores, total_score, total_max_score, program_count, output_dir='.'):
    """Guarda los resultados de evaluación en formato JSON"""
    import json
    
    # Obtener metadatos
    metadata = program_scores.get('_metadata', {})
    penalty_factor = metadata.get('penalty_factor', 1.0)
    missing_programs = metadata.get('missing_programs', [])
    
    # Calcular porcentajes
    base_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
    overall_percentage = base_percentage * penalty_factor
    
    # Determinar calificación
    if overall_percentage >= 90:
        grade = "EXCELENTE"
    elif overall_percentage >= 80:
        grade = "BIEN"
    elif overall_percentage >= 70:
        grade = "REGULAR"
    elif overall_percentage >= 60:
        grade = "SUFICIENTE"
    else:
        grade = "INSUFICIENTE"
    
    # Crear estructura de datos
    evaluation_results = {
        "student_id": student_id,
        "evaluation_date": datetime.now().isoformat(),
        "summary": {
            "total_score": total_score,
            "max_score": total_max_score,
            "base_percentage": round(base_percentage, 2),
            "overall_percentage": round(overall_percentage, 2),
            "grade": grade,
            "programs_evaluated": program_count,
            "programs_expected": metadata.get('total_expected', 4),
            "penalty_factor": round(penalty_factor, 3),
            "missing_programs": missing_programs
        },
        "program_details": {}
    }
    
    # Agregar detalles por programa
    for program, scores in program_scores.items():
        if program != '_metadata':
            percentage = (scores['total_score'] / scores['max_score'] * 100) if scores['max_score'] > 0 else 0
            evaluation_results["program_details"][program] = {
                "exists": scores['exists'],
                "total_score": scores['total_score'],
                "max_score": scores['max_score'],
                "percentage": round(percentage, 2),
                "tests": scores['tests'],
                "passed": scores['passed'],
                "failed": scores['failed'],
                "compilation_errors": scores['compilation_errors']
            }
    
    # Guardar archivo JSON
    json_file = os.path.join(output_dir, f"evaluation_results_{student_id}.json")
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
        print(f"✅ Resultados de evaluación guardados: {json_file}")
        return json_file
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")
        return None

def generate_pdf_from_latex(latex_content, output_file):
    """Genera PDF desde LaTeX con timeout"""
    try:
        # Crear archivo .tex temporal en el mismo directorio que el PDF
        tex_file = output_file.replace('.pdf', '.tex')
        with open(tex_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(latex_content)
        
        # Compilar con pdflatex
        print("Compilando LaTeX con pdflatex...")
        output_dir = os.path.dirname(output_file)
        tex_filename = os.path.basename(tex_file)
        
        # Cambiar al directorio de salida para que LaTeX genere archivos ahí
        original_cwd = os.getcwd()
        os.chdir(output_dir)
        
        # Ejecutar pdflatex en el directorio de salida
        cmd = ['pdflatex', '-interaction=nonstopmode', tex_filename]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        
        # Volver al directorio original
        os.chdir(original_cwd)
        
        # Verificar si el PDF fue generado exitosamente
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✅ PDF de testing generado exitosamente: {output_file}")
            # Limpiar archivos auxiliares
            for ext in ['.aux', '.log']:
                aux_file = output_file.replace('.pdf', ext)
                if os.path.exists(aux_file):
                    os.remove(aux_file)
            return True
        else:
            print(f"❌ Error al compilar LaTeX:")
            print(f"   Archivo esperado: {output_file}")
            print(f"   Archivo existe: {os.path.exists(output_file)}")
            if os.path.exists(output_file):
                print(f"   Tamaño del archivo: {os.path.getsize(output_file)} bytes")
            if result.stderr:
                print(f"   Error stderr: {result.stderr[-500:]}")
            if result.stdout:
                print(f"   Salida stdout: {result.stdout[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: LaTeX tardó demasiado en compilar")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generador de PDFs estéticos para resultados de testing de C')
    parser.add_argument('csv_file', help='Archivo CSV con los resultados de testing')
    parser.add_argument('-o', '--output-dir', default='.', help='Directorio de salida para el PDF (por defecto: directorio actual)')
    
    args = parser.parse_args()
    
    csv_file = args.csv_file
    output_dir = args.output_dir
    student_id = Path(csv_file).stem
    
    # Cargar datos
    csv_data = load_csv_data(csv_file)
    if not csv_data:
        sys.exit(1)
    
    print(f"🎓 Generando PDF de testing para: {student_id}")
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Calcular puntuaciones por programa
    program_scores = calculate_program_scores(csv_data)
    
    # Crear documento LaTeX
    latex_content = create_latex_document(csv_data, program_scores, student_id, output_dir)
    
    # Calcular totales para guardar en JSON
    total_score = sum(scores['total_score'] for program, scores in program_scores.items() if program != '_metadata')
    total_max_score = sum(scores['max_score'] for program, scores in program_scores.items() if program != '_metadata')
    program_count = sum(1 for program, scores in program_scores.items() if program != '_metadata' and scores['exists'])
    
    # Guardar resultados de evaluación en JSON
    json_file = save_evaluation_results(student_id, program_scores, total_score, total_max_score, program_count, output_dir)
    
    # Generar PDF en el directorio especificado
    output_file = os.path.join(output_dir, f"testing_{student_id}.pdf")
    if generate_pdf_from_latex(latex_content, output_file):
        print(f"🎉 ¡PDF de testing generado exitosamente: {output_file}")
        print(f"📄 El archivo incluye:")
        print(f"   • Resultados detallados de testing")
        print(f"   • Puntuaciones por programa")
        print(f"   • Estadísticas de compilación y ejecución")
        print(f"   • Detalles de cada prueba individual")
        print(f"   • Resumen general con porcentajes")
        if json_file:
            print(f"   • Resultados JSON: {json_file}")
    else:
        print("💥 Error al generar PDF de testing")

if __name__ == "__main__":
    main()
