#!/bin/bash

# Script general para ejecutar todo el proceso de evaluación
# Uso: ./general.sh <student_directory>
# Ejemplo: ./general.sh msc25arg

# Verificar que se proporcionó el directorio del estudiante
if [ $# -eq 0 ]; then
    echo "❌ Error: Debe proporcionar el directorio del estudiante"
    echo "Uso: ./general.sh <student_directory>"
    echo "Ejemplo: ./general.sh msc25arg"
    exit 1
fi

STUDENT_ID="$1"
STUDENT_DIR="${STUDENT_ID}/TAREA01"

echo "🚀 Iniciando proceso completo de evaluación para: $STUDENT_ID"
echo "📁 Directorio: $STUDENT_DIR"
echo "================================================"

# Paso 1: Ejecutar score.sh para generar calificaciones
echo "📊 Paso 1/4: Generando calificaciones con score.sh..."
if ./score.sh "$STUDENT_DIR"; then
    echo "✅ Calificaciones generadas exitosamente"
else
    echo "❌ Error en score.sh"
    exit 1
fi

echo ""

# Paso 2: Ejecutar test.sh para generar pruebas de ejecución
echo "🧪 Paso 2/4: Ejecutando pruebas con test.sh..."
if ./test.sh "$STUDENT_DIR" -o "scores/${STUDENT_ID}.csv"; then
    echo "✅ Pruebas de ejecución completadas"
else
    echo "❌ Error en test.sh"
    exit 1
fi

echo ""

# Paso 3: Generar PDF de pruebas de ejecución
echo "📄 Paso 3/4: Generando PDF de pruebas de ejecución..."
if python3 generate_test_pdf.py "scores/${STUDENT_ID}.csv" -o scores/; then
    echo "✅ PDF de pruebas generado exitosamente"
else
    echo "❌ Error generando PDF de pruebas"
    exit 1
fi

echo ""

# Paso 4: Generar PDF de calificaciones
echo "📋 Paso 4/4: Generando PDF de calificaciones..."
if python3 generate_pdf.py "scores/${STUDENT_ID}.json" -o scores/; then
    echo "✅ PDF de calificaciones generado exitosamente"
else
    echo "❌ Error generando PDF de calificaciones"
    exit 1
fi

echo ""

# Paso 5: Combinar los PDFs
echo "🔗 Paso 5/5: Combinando PDFs..."
if ./merge_pdfs.sh "scores/calificaciones_${STUDENT_ID}.pdf" "scores/testing_${STUDENT_ID}.pdf" "scores/final_report_${STUDENT_ID}.pdf"; then
    echo "✅ PDFs combinados exitosamente"
else
    echo "❌ Error combinando PDFs"
    exit 1
fi

echo ""
echo "🎉 ¡Proceso completo finalizado exitosamente!"
echo "================================================"
echo "📄 Archivos generados:"
echo "   • scores/${STUDENT_ID}.json - Calificaciones"
echo "   • scores/${STUDENT_ID}.csv - Resultados de pruebas"
echo "   • scores/calificaciones_${STUDENT_ID}.pdf - PDF de calificaciones"
echo "   • scores/testing_${STUDENT_ID}.pdf - PDF de pruebas de ejecución"
echo "   • scores/final_report_${STUDENT_ID}.pdf - PDF COMBINADO FINAL"
echo ""
echo "🎯 Archivo principal: scores/final_report_${STUDENT_ID}.pdf"
