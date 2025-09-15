#!/bin/bash

# Script para calificar un solo estudiante con JSON schema y PDF estético
# Ejecutar desde EJ01 como: ./score.sh msc25ahl/TAREA01
# Requiere: llm, python3, generate_aesthetic_pdf.py, prompt.txt
# Genera: JSON con calificaciones y PDF estético

if [ $# -ne 1 ]; then
    echo "🎓 Script de Calificación Automática"
    echo ""
    echo "Uso: $0 <ruta_a_TAREA01>"
    echo ""
    echo "Ejemplos:"
    echo "  $0 msc25ahl/TAREA01"
    echo "  $0 msc25apn/TAREA01"
    echo ""
    echo "Requisitos:"
    echo "  • llm (instalado y configurado)"
    echo "  • python3"
    echo "  • generate_aesthetic_pdf.py"
    echo "  • prompt.txt"
    echo ""
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
        sed -i '' "/• Código de $key:/ s/ \[PEGAR CÓDIGO AQUÍ O DEJAR VACÍO PARA EJEMPLO\]//" "$temp_prompt"
        sed -i '' "/• Código de $key:/ r $file_path" "$temp_prompt"
    else
        sed -i '' "/• Código de $key:/ s/\[PEGAR CÓDIGO AQUÍ O DEJAR VACÍO PARA EJEMPLO\]/ (archivo no encontrado)/" "$temp_prompt"
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

# Ejecutar llm con schema y guardar JSON
JSON_FILE="${student}.json"

# Schema para validación JSON
SCHEMA='{
  "type": "object",
  "properties": {
    "operaciones": {
      "type": "object",
      "properties": {
        "calificacion": {"type": "integer", "minimum": 0, "maximum": 10},
        "comentarios": {"type": "string", "minLength": 10}
      },
      "required": ["calificacion", "comentarios"]
    },
    "resistencia": {
      "type": "object",
      "properties": {
        "calificacion": {"type": "integer", "minimum": 0, "maximum": 10},
        "comentarios": {"type": "string", "minLength": 10}
      },
      "required": ["calificacion", "comentarios"]
    },
    "conversionCmsMts": {
      "type": "object",
      "properties": {
        "calificacion": {"type": "integer", "minimum": 0, "maximum": 10},
        "comentarios": {"type": "string", "minLength": 10}
      },
      "required": ["calificacion", "comentarios"]
    },
    "conversionSegHMS": {
      "type": "object",
      "properties": {
        "calificacion": {"type": "integer", "minimum": 0, "maximum": 10},
        "comentarios": {"type": "string", "minLength": 10}
      },
      "required": ["calificacion", "comentarios"]
    },
    "total": {"type": "number", "minimum": 0, "maximum": 40}
  },
  "required": ["operaciones", "resistencia", "conversionCmsMts", "conversionSegHMS", "total"]
}'

echo "Generando calificación con schema JSON..."
cat "$TEMP_PROMPT" | llm --schema "$SCHEMA" -m gpt-4o-mini > "$JSON_FILE"

# Verificar que el JSON se generó correctamente
if [ ! -s "$JSON_FILE" ]; then
    echo "❌ Error: No se pudo generar el JSON de calificación"
    rm "$TEMP_PROMPT"
    exit 1
fi

# Verificar que el JSON es válido
if ! python3 -m json.tool "$JSON_FILE" > /dev/null 2>&1; then
    echo "❌ Error: El JSON generado no es válido"
    echo "Contenido del archivo:"
    cat "$JSON_FILE"
    rm "$TEMP_PROMPT"
    exit 1
fi

echo "JSON generado exitosamente:"
cat "$JSON_FILE"
echo ""

# Generar PDF estético
echo "Generando PDF estético..."
if [ ! -f "generate_aesthetic_pdf.py" ]; then
    echo "❌ Error: generate_aesthetic_pdf.py no encontrado"
    rm "$TEMP_PROMPT"
    exit 1
fi

python3 generate_aesthetic_pdf.py "$JSON_FILE"

# Verificar que el PDF se generó
PDF_FILE="calificaciones_${student}.pdf"
if [ -f "$PDF_FILE" ]; then
    echo "✅ PDF generado exitosamente: $PDF_FILE"
else
    echo "❌ Error: No se pudo generar el PDF"
fi

# Limpiar archivo temporal
rm "$TEMP_PROMPT"

echo "🎓 Calificación completada para $student"
echo "📄 Archivos generados:"
if [ -f "$JSON_FILE" ]; then
    JSON_SIZE=$(ls -lh "$JSON_FILE" | awk '{print $5}')
    echo "   • JSON: $JSON_FILE ($JSON_SIZE)"
fi
if [ -f "$PDF_FILE" ]; then
    PDF_SIZE=$(ls -lh "$PDF_FILE" | awk '{print $5}')
    echo "   • PDF: $PDF_FILE ($PDF_SIZE)"
fi
echo ""
echo "✨ Proceso completado exitosamente"