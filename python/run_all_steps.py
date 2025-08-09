"""Comprehensive test runner for all analysis steps with coverage tracking"""

import os
import sys
import subprocess
import coverage

def run_with_coverage():
    """Run all analysis steps with coverage tracking"""
    
    # Initialize coverage
    cov = coverage.Coverage(source=['python'])
    cov.start()
    
    # List of all analysis steps
    steps = [
        'python/step1_csv_import.py',
        'python/step2_nps_analysis.py', 
        'python/step3_visualizations.py',
        'python/step4_word_cloud.py',
        'python/step5_track_improvements.py',
        'python/step6_session_rankings.py',
        'python/step7_lowest_nps.py'
    ]
    
    print("=" * 60)
    print("RUNNING ALL ANALYSIS STEPS WITH COVERAGE TRACKING")
    print("=" * 60)
    
    # Run each step
    for step in steps:
        if os.path.exists(step):
            print(f"\n🔄 Running {step}...")
            try:
                # Import and run the module
                module_name = step.replace('/', '.').replace('.py', '')
                exec(f"import {module_name}")
                print(f"✅ {step} completed successfully")
            except Exception as e:
                print(f"❌ {step} failed: {str(e)}")
        else:
            print(f"⚠️  {step} not found")
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\n" + "=" * 60)
    print("COVERAGE REPORT")
    print("=" * 60)
    
    # Generate coverage report
    cov.report(show_missing=True)
    
    # Calculate overall coverage
    total_statements = 0
    total_missing = 0
    
    for filename in cov.get_data().measured_files():
        if 'python' in filename:
            file_coverage = cov.analysis2(filename)
            statements = len(file_coverage[1])
            missing = len(file_coverage[2])
            total_statements += statements
            total_missing += missing
            
            if statements > 0:
                coverage_percent = ((statements - missing) / statements) * 100
                print(f"\n📊 {os.path.basename(filename)}: {coverage_percent:.1f}% ({statements - missing}/{statements})")
    
    if total_statements > 0:
        overall_coverage = ((total_statements - total_missing) / total_statements) * 100
        print(f"\n🎯 OVERALL COVERAGE: {overall_coverage:.1f}% ({total_statements - total_missing}/{total_statements})")
        
        if overall_coverage >= 95:
            print("✅ TARGET ACHIEVED: 95%+ coverage!")
        else:
            print(f"⚠️  TARGET MISSED: Need {95 - overall_coverage:.1f}% more coverage")
    
    # Generate HTML report
    cov.html_report(directory='htmlcov')
    print(f"\n📄 HTML report generated in htmlcov/ directory")

if __name__ == "__main__":
    run_with_coverage()
