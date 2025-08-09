"""Comprehensive Coverage Analysis for AI Training Program Analysis"""

import os
import sys
import importlib.util
import coverage
from pathlib import Path

def analyze_file_coverage(file_path):
    """Analyze coverage for a single file"""
    try:
        # Initialize coverage for this file
        cov = coverage.Coverage(source=[str(file_path.parent)])
        cov.start()
        
        # Import and execute the module
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Get coverage data
        analysis = cov.analysis2(str(file_path))
        statements = analysis[1]
        missing = analysis[2]
        covered = len(statements) - len(missing)
        total = len(statements)
        
        coverage_percent = (covered / total * 100) if total > 0 else 0
        
        return {
            'file': file_path.name,
            'statements': total,
            'covered': covered,
            'missing': len(missing),
            'coverage': coverage_percent,
            'missing_lines': missing
        }
        
    except Exception as e:
        return {
            'file': file_path.name,
            'statements': 0,
            'covered': 0,
            'missing': 0,
            'coverage': 0,
            'error': str(e)
        }

def main():
    """Main coverage analysis function"""
    print("=" * 80)
    print("COMPREHENSIVE COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Get all Python files in the python directory
    python_dir = Path("python")
    python_files = list(python_dir.glob("step*.py"))
    
    if not python_files:
        print("❌ No step*.py files found in python directory")
        return
    
    print(f"📁 Found {len(python_files)} analysis files to test")
    print()
    
    # Analyze each file
    results = []
    total_statements = 0
    total_covered = 0
    
    for file_path in python_files:
        print(f"🔄 Analyzing {file_path.name}...")
        result = analyze_file_coverage(file_path)
        results.append(result)
        
        if 'error' not in result:
            total_statements += result['statements']
            total_covered += result['covered']
            status = "✅" if result['coverage'] >= 95 else "⚠️"
            print(f"   {status} Coverage: {result['coverage']:.1f}% ({result['covered']}/{result['statements']})")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("DETAILED COVERAGE REPORT")
    print("=" * 80)
    
    # Display detailed results
    for result in results:
        if 'error' not in result:
            status = "✅" if result['coverage'] >= 95 else "⚠️"
            print(f"\n{status} {result['file']}: {result['coverage']:.1f}% ({result['covered']}/{result['statements']})")
            
            if result['missing_lines']:
                print(f"   Missing lines: {sorted(result['missing_lines'])}")
        else:
            print(f"\n❌ {result['file']}: ERROR - {result['error']}")
    
    # Calculate overall coverage
    if total_statements > 0:
        overall_coverage = (total_covered / total_statements) * 100
        print(f"\n" + "=" * 80)
        print(f"🎯 OVERALL COVERAGE: {overall_coverage:.1f}% ({total_covered}/{total_statements})")
        
        if overall_coverage >= 95:
            print("✅ TARGET ACHIEVED: 95%+ coverage!")
        else:
            print(f"⚠️  TARGET MISSED: Need {95 - overall_coverage:.1f}% more coverage")
            
            # Identify files that need improvement
            print(f"\n📋 FILES NEEDING IMPROVEMENT:")
            for result in results:
                if 'error' not in result and result['coverage'] < 95:
                    needed = 95 - result['coverage']
                    print(f"   • {result['file']}: +{needed:.1f}% needed")
    
    print(f"\n📄 Detailed HTML report available in htmlcov/ directory")

if __name__ == "__main__":
    main()
