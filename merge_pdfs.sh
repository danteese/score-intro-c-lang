#!/bin/bash

# Script para concatenar dos PDFs usando Ghostscript
# Usage: ./merge_pdfs.sh <pdf1> <pdf2> <output_pdf>
# Example: ./merge_pdfs.sh calificaciones_msc25ahl.pdf testing_msc25ahl.pdf final_report_msc25ahl.pdf

# Verificar que Ghostscript esté instalado
if ! command -v gs &> /dev/null; then
    echo "❌ Error: Ghostscript no está instalado"
    echo "Instala Ghostscript con:"
    echo "  macOS: brew install ghostscript"
    echo "  Ubuntu: sudo apt-get install ghostscript"
    exit 1
fi

# Verificar argumentos
if [ $# -ne 3 ]; then
    echo "🔗 Concatenador de PDFs con Ghostscript"
    echo ""
    echo "Usage: $0 <pdf1> <pdf2> <output_pdf>"
    echo ""
    echo "Examples:"
    echo "  $0 calificaciones_msc25ahl.pdf testing_msc25ahl.pdf final_report_msc25ahl.pdf"
    echo "  $0 scores/calificaciones.pdf scores/testing.pdf scores/final.pdf"
    echo ""
    echo "El script concatenará pdf1 y pdf2 en el orden especificado"
    echo "y guardará el resultado en output_pdf"
    exit 1
fi

PDF1="$1"
PDF2="$2"
OUTPUT_PDF="$3"

# Verificar que los archivos de entrada existan
if [ ! -f "$PDF1" ]; then
    echo "❌ Error: El archivo $PDF1 no existe"
    exit 1
fi

if [ ! -f "$PDF2" ]; then
    echo "❌ Error: El archivo $PDF2 no existe"
    exit 1
fi

# Crear directorio de salida si no existe
mkdir -p "$(dirname "$OUTPUT_PDF")"

# Verificar que los PDFs no estén vacíos
if [ ! -s "$PDF1" ]; then
    echo "❌ Error: El archivo $PDF1 está vacío"
    exit 1
fi

if [ ! -s "$PDF2" ]; then
    echo "❌ Error: El archivo $PDF2 está vacío"
    exit 1
fi

echo "🔗 Concatenando PDFs..."
echo "   PDF 1: $PDF1"
echo "   PDF 2: $PDF2"
echo "   Salida: $OUTPUT_PDF"

# Concatenar PDFs usando Ghostscript
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="$OUTPUT_PDF" "$PDF1" "$PDF2"

# Verificar si la concatenación fue exitosa
if [ $? -eq 0 ] && [ -f "$OUTPUT_PDF" ] && [ -s "$OUTPUT_PDF" ]; then
    echo "✅ PDFs concatenados exitosamente: $OUTPUT_PDF"
    
    # Mostrar información del archivo resultante
    file_size=$(ls -lh "$OUTPUT_PDF" | awk '{print $5}')
    echo "📄 Tamaño del archivo: $file_size"
    
    # Verificar que el PDF es válido
    if gs -q -dNOPAUSE -dBATCH -sDEVICE=nullpage "$OUTPUT_PDF" 2>/dev/null; then
        echo "✅ PDF válido y listo para usar"
    else
        echo "⚠️  Advertencia: El PDF generado podría tener problemas"
    fi
else
    echo "❌ Error al concatenar los PDFs"
    exit 1
fi

echo ""
echo "🎉 ¡Concatenación completada!"
echo "📄 Archivo final: $OUTPUT_PDF"
