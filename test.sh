#!/bin/bash

# Test Suite for C Programs - Per Directory Execution
# Usage: ./test.sh <student_directory> -o <output_csv_file>
# Example: ./test.sh msc25ahl/TAREA01 -o scores/msc25ahl.csv

# Parse command line arguments
if [ $# -lt 3 ] || [ "$2" != "-o" ]; then
    echo "🎓 C Program Test Suite"
    echo ""
    echo "Usage: $0 <student_directory> -o <output_csv_file>"
    echo ""
    echo "Examples:"
    echo "  $0 msc25ahl/TAREA01 -o scores/msc25ahl.csv"
    echo "  $0 msc25apn/TAREA01 -o scores/msc25apn.csv"
    echo ""
    echo "The script will test all C programs in the specified directory"
    echo "and generate a CSV report with test results."
    exit 1
fi

STUDENT_DIR="$1"
OUTPUT_CSV="$3"
STUDENT_ID=$(basename "$(dirname "$STUDENT_DIR")")

# Verify directory exists
if [ ! -d "$STUDENT_DIR" ]; then
    echo "❌ Error: Directory $STUDENT_DIR not found"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_CSV")"

# Initialize CSV file with headers
echo "Student_ID,Program_Name,Test_Type,Input_Values,Expected_Result,Actual_Result,Test_Status,Compilation_Status,Error_Details,Test_Score,Notes" > "$OUTPUT_CSV"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to test a single program
test_program() {
    local program_file="$1"
    local program_name="$2"
    
    log "Testing $program_name for student $STUDENT_ID"
    
    # Check if file exists
    if [ ! -f "$program_file" ]; then
        log "❌ File $program_name not found for $STUDENT_ID"
        echo "$STUDENT_ID,$program_name,FILE_NOT_FOUND,N/A,N/A,N/A,FAIL,NO_FILE,File not found,0,Missing program file" >> "$OUTPUT_CSV"
        return 1
    fi
    
    # Compile the program
    local executable="${program_name%.c}"
    local compile_output
    local compile_status
    
    compile_output=$(gcc -o "$STUDENT_DIR/$executable" "$program_file" 2>&1)
    compile_status=$?
    
    if [ $compile_status -ne 0 ]; then
        log "❌ Compilation failed for $program_name ($STUDENT_ID)"
        echo "$STUDENT_ID,$program_name,COMPILATION,N/A,N/A,N/A,FAIL,COMPILE_ERROR,\"$compile_output\",0,Compilation failed" >> "$OUTPUT_CSV"
        return 1
    fi
    
    log "✅ Compilation successful for $program_name ($STUDENT_ID)"
    
    # Define test cases based on program type
    case "$program_name" in
        "operaciones.c")
            test_operaciones "$STUDENT_DIR" "$executable"
            ;;
        "conversionCmsMts.c")
            test_conversion_cms_mts "$STUDENT_DIR" "$executable"
            ;;
        "conversionSegsHMS.c")
            test_conversion_segs_hms "$STUDENT_DIR" "$executable"
            ;;
        "resistencia.c")
            test_resistencia "$STUDENT_DIR" "$executable"
            ;;
        *)
            log "⚠️  Unknown program type: $program_name"
            echo "$STUDENT_ID,$program_name,UNKNOWN,N/A,N/A,N/A,SKIP,COMPILED,Unknown program type,0,Unknown program type" >> "$OUTPUT_CSV"
            ;;
    esac
    
    # Clean up executable
    rm -f "$STUDENT_DIR/$executable"
}

# Test function for operaciones.c
test_operaciones() {
    local student_dir="$1"
    local executable="$2"
    
    local test_cases=(
        "10:5:15:5:50:2:0:Basic arithmetic test"
        "20:4:24:16:80:5:0:Positive numbers test"
        "100:25:125:75:2500:4:0:Large numbers test"
        "7:3:10:4:21:2:1:Small numbers test"
        "0:5:5:-5:0:0:0:Zero handling test"
    )
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r a b expected_sum expected_rest expected_mult expected_div expected_mod description <<< "$test_case"
        local input="a=$a, b=$b"
        local expected_output="Suma: $expected_sum, Resta: $expected_rest, Multiplicacion: $expected_mult, Division: $expected_div, Residuo: $expected_mod"
        
        local actual_output=$(printf "$a\n$b" | "$student_dir/$executable" 2>&1)
        local status="PASS"
        local score=10
        local notes="All operations correct"
        
        # Check if all expected values are in output
        if ! echo "$actual_output" | grep -q "la suma da:$expected_sum" || \
           ! echo "$actual_output" | grep -q "la resta da:$expected_rest" || \
           ! echo "$actual_output" | grep -q "la multiplicacion da:$expected_mult" || \
           ! echo "$actual_output" | grep -q "la division da:$expected_div" || \
           ! echo "$actual_output" | grep -q "residuo:$expected_mod"; then
            status="FAIL"
            score=0
            notes="One or more operations failed"
        fi
        
        echo "$STUDENT_ID,operaciones.c,OPERATIONS,\"$input\",\"$expected_output\",\"$actual_output\",$status,COMPILED,,$score,$description" >> "$OUTPUT_CSV"
        log "Test case $a,$b: $status ($score/10)"
    done
}

# Test function for conversionCmsMts.c
test_conversion_cms_mts() {
    local student_dir="$1"
    local executable="$2"
    
    local test_cases=(
        "150:1:50:Normal conversion test"
        "100:1:0:Exact meter boundary test"
        "75:0:75:Less than meter test"
        "0:0:0:Zero input test"
        "2500:25:0:Multiple meters test"
        "2537:25:37:Complex conversion test"
        "99:0:99:Boundary below meter test"
        "101:1:1:Boundary above meter test"
    )
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r input expected_m expected_c description <<< "$test_case"
        local expected_output="Equivalente: $expected_m metros y $expected_c cm"
        
        local actual_output=$(echo "$input" | "$student_dir/$executable" 2>&1)
        local status="PASS"
        local score=10
        local notes="Conversion correct"
        
        # Extract actual values from output
        local actual_m=$(echo "$actual_output" | grep -o '[0-9]\+' | head -1)
        local actual_c=$(echo "$actual_output" | grep -o '[0-9]\+' | tail -1)
        
        if [ "$actual_m" != "$expected_m" ] || [ "$actual_c" != "$expected_c" ]; then
            status="FAIL"
            score=0
            notes="Expected: $expected_m m $expected_c cm, Got: $actual_m m $actual_c cm"
        fi
        
        echo "$STUDENT_ID,conversionCmsMts.c,CONVERSION_CM_MT,$input,\"$expected_output\",\"$actual_output\",$status,COMPILED,,$score,$description" >> "$OUTPUT_CSV"
        log "Test case $input cm: $status ($score/10) - $notes"
    done
}

# Test function for conversionSegsHMS.c
test_conversion_segs_hms() {
    local student_dir="$1"
    local executable="$2"
    
    local test_cases=(
        "3661:1:1:1:Complex time conversion test"
        "3600:1:0:0:Exact hour boundary test"
        "3660:1:1:0:Minute boundary test"
        "59:0:0:59:Less than minute test"
        "0:0:0:0:Zero input test"
        "7200:2:0:0:Multiple hours test"
        "7323:2:2:3:Complex time test"
    )
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r input expected_h expected_m expected_s description <<< "$test_case"
        local expected_output="Horas: $expected_h, Minutos: $expected_m, Segundos: $expected_s"
        
        local actual_output=$(echo "$input" | "$student_dir/$executable" 2>&1)
        local status="PASS"
        local score=10
        local notes="Time conversion correct"
        
        # Extract actual values from output
        local actual_h=$(echo "$actual_output" | grep "Horas:" | grep -o '[0-9]\+')
        local actual_m=$(echo "$actual_output" | grep "Minutos:" | grep -o '[0-9]\+')
        local actual_s=$(echo "$actual_output" | grep "Segundos:" | grep -o '[0-9]\+')
        
        if [ "$actual_h" != "$expected_h" ] || [ "$actual_m" != "$expected_m" ] || [ "$actual_s" != "$expected_s" ]; then
            status="FAIL"
            score=0
            notes="Expected: ${expected_h}h ${expected_m}m ${expected_s}s, Got: ${actual_h}h ${actual_m}m ${actual_s}s"
        fi
        
        echo "$STUDENT_ID,conversionSegsHMS.c,CONVERSION_SEGS_HMS,$input,\"$expected_output\",\"$actual_output\",$status,COMPILED,,$score,$description" >> "$OUTPUT_CSV"
        log "Test case $input seconds: $status ($score/10) - $notes"
    done
}

# Test function for resistencia.c
test_resistencia() {
    local student_dir="$1"
    local executable="$2"
    
    local test_cases=(
        "1.0:0.001:Basic resistance calculation"
        "2.0:0.002:Medium resistance calculation"
        "0.5:0.0005:Small resistance calculation"
    )
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r length radius description <<< "$test_case"
        local input="Length=$length m, Radius=$radius m"
        local expected_output="Resistance calculation with given parameters"
        
        local actual_output=$(printf "$length\n$radius" | "$student_dir/$executable" 2>&1)
        local status="PASS"
        local score=10
        local notes="Resistance calculation successful"
        
        # Check if output contains expected patterns (resistencia calculations can vary slightly)
        if ! echo "$actual_output" | grep -q "Longitud:$length" || \
           ! echo "$actual_output" | grep -q "Radio:$radius" || \
           ! echo "$actual_output" | grep -q "La resistencia del conductor es:"; then
            status="FAIL"
            score=0
            notes="Missing expected output patterns"
        fi
        
        echo "$STUDENT_ID,resistencia.c,RESISTANCE,\"$input\",\"$expected_output\",\"$actual_output\",$status,COMPILED,,$score,$description" >> "$OUTPUT_CSV"
        log "Test case L=$length, R=$radius: $status ($score/10) - $notes"
    done
}

# Main execution
main() {
    log "🚀 Starting C program test suite for $STUDENT_ID"
    log "📁 Testing directory: $STUDENT_DIR"
    log "📊 Results will be saved to: $OUTPUT_CSV"
    
    # Test each program type
    local programs=("operaciones.c" "conversionCmsMts.c" "conversionSegsHMS.c" "resistencia.c")
    
    for program in "${programs[@]}"; do
        test_program "$STUDENT_DIR/$program" "$program"
    done
    
    log "✅ Completed testing for $STUDENT_ID"
    
    # Generate summary statistics
    local total_tests=$(tail -n +2 "$OUTPUT_CSV" | wc -l)
    local passed_tests=$(tail -n +2 "$OUTPUT_CSV" | grep ",PASS," | wc -l)
    local failed_tests=$(tail -n +2 "$OUTPUT_CSV" | grep ",FAIL," | wc -l)
    local compilation_errors=$(tail -n +2 "$OUTPUT_CSV" | grep "COMPILE_ERROR" | wc -l)
    local total_score=$(tail -n +2 "$OUTPUT_CSV" | cut -d',' -f10 | awk '{sum+=$1} END {print sum}')
    local max_possible_score=$(tail -n +2 "$OUTPUT_CSV" | wc -l | awk '{print $1 * 10}')
    
    echo ""
    echo "📈 TEST SUMMARY for $STUDENT_ID"
    echo "================================"
    echo "Total tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $failed_tests"
    echo "Compilation errors: $compilation_errors"
    echo "Total score: $total_score/$max_possible_score"
    if [ $total_tests -gt 0 ]; then
        echo "Success rate: $(( (passed_tests * 100) / total_tests ))%"
        echo "Score percentage: $(( (total_score * 100) / max_possible_score ))%"
    fi
    echo ""
    echo "📄 Detailed results: $OUTPUT_CSV"
}

# Run main function
main "$@"
