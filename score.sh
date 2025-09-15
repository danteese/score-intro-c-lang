#!/bin/bash

# Script para calificar un solo estudiante
# Ejecutar desde EJ01 como: ./score.sh msc25ahl/TAREA01
# Requiere llm "prompt" instalado y pandoc para PDF
# Asume que prompt.txt está en el directorio EJ01

if [ $# -ne 1 ]; then
    echo "Uso: $0 <ruta_a_TAREA01> (ej. msc25ahl/TAREA01)"
    exit 1
fi

STUDENT_DIR="$1"
PROMPT_PATH="prompt.txt"
student=$(basename $(dirname "$STUDENT_DIR"))

# Verifica que el directorio exista
if [ ! -d "$STUDENT_DIR" ]; then
    echo "Directorio $STUDENT_DIR no encontrado."
    exit 1
fi

echo "Procesando estudiante: $student"

TEMP_PROMPT=$(mktemp)
cp "$PROMPT_PATH" "$TEMP_PROMPT"

# Función para reemplazar código en prompt temporal
replace_code() {
    local temp_prompt="$1"
    local file_path="$2"
    local key="$3"
    if [ -f "$file_path" ]; then
        sed -i '' "/- Código de $key:/ s/ \[PEGAR CÓDIGO AQUÍ O DEJAR VACÍO PARA EJEMPLO\]//" "$temp_prompt"
        sed -i '' "/- Código de $key:/ r $file_path" "$temp_prompt"
    else
        sed -i '' "/- Código de $key:/ s/\[PEGAR CÓDIGO AQUÍ O DEJAR VACÍO PARA EJEMPLO\]/ (archivo no encontrado)/" "$temp_prompt"
    fi
}

# Reemplazos para cada archivo
replace_code "$TEMP_PROMPT" "$STUDENT_DIR/operaciones.c" "operaciones.c"
replace_code "$TEMP_PROMPT" "$STUDENT_DIR/resistencia.c" "resistencia.c"
replace_code "$TEMP_PROMPT" "$STUDENT_DIR/conversionCmsMts.c" "conversionCmsMts.c"

# Maneja variaciones de nombre para conversionSegHMS.c
if [ -f "$STUDENT_DIR/conversionSegsHMS.c" ]; then
    replace_code "$TEMP_PROMPT" "$STUDENT_DIR/conversionSegsHMS.c" "conversionSegHMS.c"
elif [ -f "$STUDENT_DIR/conversionSegHMS.c" ]; then
    replace_code "$TEMP_PROMPT" "$STUDENT_DIR/conversionSegHMS.c" "conversionSegHMS.c"
else
    replace_code "$TEMP_PROMPT" "" "conversionSegHMS.c"
fi

# Ejecutar llm y guardar JSON
JSON_FILE="${student}.json"
cat "$TEMP_PROMPT" | llm "prompt" > "$JSON_FILE"

cat "$JSON_FILE"

# Llamar al script Python para generar PDF
# python generar_pdf_calificaciones.py "$JSON_FILE"

# rm "$TEMP_PROMPT"

echo "Calificación completada para $student. PDF generado: calificaciones_${student}.pdf"