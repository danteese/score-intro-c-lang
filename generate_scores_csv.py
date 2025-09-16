#!/usr/bin/env python3
"""
Script to process all JSON files from the scores directory and generate a comprehensive CSV
with student scores per program.
"""

import json
import csv
import os
import glob
from pathlib import Path
import pandas as pd

def load_json_file(file_path):
    """Load and parse a JSON file, return None if invalid."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_student_id_from_filename(filename):
    """Extract student ID from filename."""
    # Remove .json extension and get the basename
    base_name = os.path.basename(filename).replace('.json', '')
    
    # Handle different naming patterns
    if base_name.startswith('evaluation_results_'):
        return base_name.replace('evaluation_results_', '')
    elif base_name.startswith('msc25'):
        return base_name
    else:
        return base_name

def normalize_program_scores(record):
    """Normalize program score column names to handle naming inconsistencies."""
    # Handle the conversionSegHMS vs conversionSegsHMS inconsistency
    # Standardize on conversionSegsHMS (with 's') as it appears in evaluation results
    
    # If we have conversionSegHMS_score (without 's'), rename it to conversionSegsHMS_score
    if 'conversionSegHMS_score' in record and 'conversionSegsHMS_score' not in record:
        record['conversionSegsHMS_score'] = record['conversionSegHMS_score']
        del record['conversionSegHMS_score']
    
    # If we have conversionSegHMS_comments (without 's'), rename it to conversionSegsHMS_comments
    if 'conversionSegHMS_comments' in record and 'conversionSegsHMS_comments' not in record:
        record['conversionSegsHMS_comments'] = record['conversionSegHMS_comments']
        del record['conversionSegHMS_comments']
    
    # Handle .c versions - convert to standard format
    for key in list(record.keys()):
        if key.endswith('.c_score'):
            program_name = key.replace('.c_score', '')
            if f'{program_name}_score' not in record:
                record[f'{program_name}_score'] = record[key]
            del record[key]
        elif key.endswith('.c_comments'):
            program_name = key.replace('.c_comments', '')
            if f'{program_name}_comments' not in record:
                record[f'{program_name}_comments'] = record[key]
            del record[key]
    
    return record

def process_student_json(data, student_id):
    """Process individual student JSON file (format like msc25ahl.json)."""
    if not data or not isinstance(data, dict):
        return None
    
    result = {
        'student_id': student_id,
        'file_type': 'student_scores'
    }
    
    # Extract program scores
    programs = ['operaciones', 'resistencia', 'conversionCmsMts', 'conversionSegHMS']
    
    for program in programs:
        if program in data:
            result[f'{program}_score'] = data[program].get('calificacion', 0)
            result[f'{program}_comments'] = data[program].get('comentarios', '')
        else:
            result[f'{program}_score'] = 0
            result[f'{program}_comments'] = 'Not found'
    
    # Add total score if available
    result['total_score'] = data.get('total', 0)
    
    return result

def process_evaluation_json(data, student_id):
    """Process evaluation results JSON file (format like evaluation_results_msc25ahl.json)."""
    if not data or not isinstance(data, dict):
        return None
    
    result = {
        'student_id': student_id,
        'file_type': 'evaluation_results'
    }
    
    # Extract summary information
    summary = data.get('summary', {})
    result['total_score'] = summary.get('total_score', 0)
    result['max_score'] = summary.get('max_score', 0)
    result['base_percentage'] = summary.get('base_percentage', 0)
    result['overall_percentage'] = summary.get('overall_percentage', 0)
    result['grade'] = summary.get('grade', '')
    result['programs_evaluated'] = summary.get('programs_evaluated', 0)
    result['programs_expected'] = summary.get('programs_expected', 0)
    result['penalty_factor'] = summary.get('penalty_factor', 1.0)
    result['missing_programs'] = ', '.join(summary.get('missing_programs', []))
    
    # Extract program details
    program_details = data.get('program_details', {})
    programs = ['operaciones.c', 'resistencia.c', 'conversionCmsMts.c', 'conversionSegsHMS.c']
    
    for program in programs:
        if program in program_details:
            details = program_details[program]
            result[f'{program}_exists'] = details.get('exists', False)
            result[f'{program}_score'] = details.get('total_score', 0)
            result[f'{program}_max_score'] = details.get('max_score', 0)
            result[f'{program}_percentage'] = details.get('percentage', 0)
            result[f'{program}_tests'] = details.get('tests', 0)
            result[f'{program}_passed'] = details.get('passed', 0)
            result[f'{program}_failed'] = details.get('failed', 0)
            result[f'{program}_compilation_errors'] = details.get('compilation_errors', 0)
        else:
            # Set default values for missing programs
            result[f'{program}_exists'] = False
            result[f'{program}_score'] = 0
            result[f'{program}_max_score'] = 0
            result[f'{program}_percentage'] = 0
            result[f'{program}_tests'] = 0
            result[f'{program}_passed'] = 0
            result[f'{program}_failed'] = 0
            result[f'{program}_compilation_errors'] = 0
    
    return result

def main():
    """Main function to process all JSON files and generate CSV."""
    scores_dir = "/Users/dantebazaldua/Work/Edgar/progra_1/EJ01/scores"
    
    if not os.path.exists(scores_dir):
        print(f"Error: Scores directory {scores_dir} not found")
        return
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(scores_dir, "*.json"))
    
    if not json_files:
        print("No JSON files found in scores directory")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process all JSON files
    student_scores_data = []
    evaluation_results_data = []
    
    for json_file in sorted(json_files):
        print(f"Processing: {os.path.basename(json_file)}")
        
        data = load_json_file(json_file)
        if data is None:
            continue
        
        student_id = extract_student_id_from_filename(json_file)
        
        # Determine file type and process accordingly
        if 'evaluation_results' in os.path.basename(json_file):
            processed_data = process_evaluation_json(data, student_id)
            if processed_data:
                evaluation_results_data.append(processed_data)
        else:
            processed_data = process_student_json(data, student_id)
            if processed_data:
                student_scores_data.append(processed_data)
    
    if not student_scores_data and not evaluation_results_data:
        print("No valid data found to process")
        return
    
    # Convert to DataFrames
    student_df = pd.DataFrame(student_scores_data) if student_scores_data else pd.DataFrame()
    evaluation_df = pd.DataFrame(evaluation_results_data) if evaluation_results_data else pd.DataFrame()
    
    # Merge the data to create one row per student
    merged_data = []
    unique_students = set()
    
    # Get all unique student IDs
    if not student_df.empty:
        unique_students.update(student_df['student_id'].unique())
    if not evaluation_df.empty:
        unique_students.update(evaluation_df['student_id'].unique())
    
    for student_id in sorted(unique_students):
        # Get records for this student
        student_record = student_df[student_df['student_id'] == student_id] if not student_df.empty else pd.DataFrame()
        evaluation_record = evaluation_df[evaluation_df['student_id'] == student_id] if not evaluation_df.empty else pd.DataFrame()
        
        # Start with basic student info
        merged_record = {'student_id': student_id}
        
        # Add evaluation results data (preferred for scores and statistics)
        if not evaluation_record.empty:
            eval_data = evaluation_record.iloc[0].to_dict()
            eval_data = normalize_program_scores(eval_data)
            for key, value in eval_data.items():
                if key != 'student_id' and pd.notna(value):
                    merged_record[key] = value
        
        # Add student scores data (for comments and additional info)
        if not student_record.empty:
            student_data = student_record.iloc[0].to_dict()
            student_data = normalize_program_scores(student_data)
            for key, value in student_data.items():
                if key != 'student_id' and pd.notna(value):
                    # Only add if not already present from evaluation data
                    if key not in merged_record:
                        merged_record[key] = value
        
        merged_data.append(merged_record)
    
    # Convert merged data to DataFrame
    merged_df = pd.DataFrame(merged_data)
    
    # Generate CSV files
    output_dir = "/Users/dantebazaldua/Work/Edgar/progra_1/EJ01/scores"
    
    # 1. Merged CSV with all data (one row per student)
    merged_csv = os.path.join(output_dir, "all_scores_merged.csv")
    merged_df.to_csv(merged_csv, index=False, encoding='utf-8')
    print(f"Merged CSV saved to: {merged_csv}")
    
    # 2. Separate CSVs by file type (for reference)
    if not student_df.empty:
        student_csv = os.path.join(output_dir, "student_scores.csv")
        student_df.to_csv(student_csv, index=False, encoding='utf-8')
        print(f"Student scores CSV saved to: {student_csv}")
    
    if not evaluation_df.empty:
        evaluation_csv = os.path.join(output_dir, "evaluation_results.csv")
        evaluation_df.to_csv(evaluation_csv, index=False, encoding='utf-8')
        print(f"Evaluation results CSV saved to: {evaluation_csv}")
    
    # 3. Summary CSV with key metrics
    summary_columns = ['student_id', 'total_score', 'max_score', 'overall_percentage', 'grade', 
                      'programs_evaluated', 'programs_expected', 'missing_programs']
    
    # Add program score columns
    programs = ['operaciones', 'resistencia', 'conversionCmsMts', 'conversionSegsHMS']
    for program in programs:
        summary_columns.append(f'{program}_score')
    
    # Create summary DataFrame
    summary_df = merged_df[summary_columns].copy() if all(col in merged_df.columns for col in summary_columns) else merged_df
    
    summary_csv = os.path.join(output_dir, "scores_summary.csv")
    summary_df.to_csv(summary_csv, index=False, encoding='utf-8')
    print(f"Summary CSV saved to: {summary_csv}")
    
    # Print statistics
    print(f"\nProcessed {len(json_files)} JSON files")
    print(f"Unique students: {len(unique_students)}")
    print(f"Student scores records: {len(student_scores_data)}")
    print(f"Evaluation results records: {len(evaluation_results_data)}")
    print(f"Merged records: {len(merged_data)}")

if __name__ == "__main__":
    main()
