#!/bin/bash

# Script de instalación para el Sistema de Evaluación de Programas C
# Uso: ./install.sh

echo "🚀 Instalando Sistema de Evaluación de Programas C"
echo "=================================================="

# Verificar sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo "❌ Sistema operativo no soportado: $OSTYPE"
    exit 1
fi

echo "📱 Sistema detectado: $OS"

# Verificar si Homebrew está instalado (macOS)
if [[ "$OS" == "macOS" ]]; then
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew no está instalado"
        echo "Instala Homebrew desde: https://brew.sh"
        exit 1
    fi
    echo "✅ Homebrew encontrado"
fi

# Instalar dependencias del sistema
echo ""
echo "📦 Instalando dependencias del sistema..."

if [[ "$OS" == "macOS" ]]; then
    echo "Instalando Ghostscript..."
    brew install ghostscript
    
    echo "Instalando LaTeX..."
    brew install --cask mactex
    
    echo "Instalando llm..."
    pip3 install llm
elif [[ "$OS" == "Linux" ]]; then
    echo "Instalando Ghostscript..."
    sudo apt-get update
    sudo apt-get install -y ghostscript
    
    echo "Instalando LaTeX..."
    sudo apt-get install -y texlive-full
    
    echo "Instalando llm..."
    pip3 install llm
fi

# Crear entorno virtual de Python
echo ""
echo "🐍 Configurando entorno virtual de Python..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual e instalar dependencias
echo "Instalando dependencias de Python..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar llm
echo ""
echo "🤖 Configurando LLM..."
echo "Necesitas configurar tu API key para LLM"
echo "Ejecuta: llm keys set openai"
echo "Y proporciona tu API key de OpenAI"

# Hacer scripts ejecutables
echo ""
echo "🔧 Configurando permisos de ejecución..."
chmod +x *.sh
chmod +x *.py

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."

# Verificar Ghostscript
if command -v gs &> /dev/null; then
    echo "✅ Ghostscript: $(gs --version)"
else
    echo "❌ Ghostscript no encontrado"
fi

# Verificar LaTeX
if command -v pdflatex &> /dev/null; then
    echo "✅ LaTeX: $(pdflatex --version | head -n1)"
else
    echo "❌ LaTeX no encontrado"
fi

# Verificar llm
if command -v llm &> /dev/null; then
    echo "✅ LLM: $(llm --version)"
else
    echo "❌ LLM no encontrado"
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python no encontrado"
fi

# Verificar pandas en el entorno virtual
source .venv/bin/activate
if python3 -c "import pandas; print('✅ Pandas:', pandas.__version__)" 2>/dev/null; then
    echo ""
else
    echo "❌ Pandas no encontrado en el entorno virtual"
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura tu API key de LLM: llm keys set openai"
echo "2. Verifica que todos los estudiantes tengan sus archivos C en msc25*/TAREA01/"
echo "3. Ejecuta el sistema: ./all.sh"
echo ""
echo "📚 Para más información, consulta README.md"
