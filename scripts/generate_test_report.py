# scripts/generate_test_report.py
import xml.etree.ElementTree as ET
import datetime
import json
import os
from pathlib import Path

def analyze_coverage_report():

    try:
        if not os.path.exists('coverage.xml'):
            print("Warning: coverage.xml not found. Running tests to generate it...")
            os.system('pytest tests/ --cov=telemetry_toolkit --cov-report=xml')
        
        tree = ET.parse('coverage.xml')
        root = tree.getroot()
        
        coverage = float(root.attrib.get('line-rate', 0)) * 100
        
        # Find modules with low coverage
        low_coverage_modules = []
        for package in root.findall('.//package'):
            for module in package.findall('classes/class'):
                module_coverage = float(module.attrib.get('line-rate', 0)) * 100
                if module_coverage < 80:  # Threshold for low coverage
                    low_coverage_modules.append({
                        'name': module.attrib.get('name', 'Unknown Module'),
                        'coverage': module_coverage
                    })
        
        return {
            'overall_coverage': coverage,
            'low_coverage_modules': low_coverage_modules
        }
    except Exception as e:
        print(f"Error analyzing coverage report: {str(e)}")
        return {
            'overall_coverage': 0.0,
            'low_coverage_modules': []
        }

def analyze_test_results():

    try:
        if not os.path.exists('test-results/junit.xml'):
            print("Warning: junit.xml not found. Running tests to generate it...")
            os.system('pytest tests/ --junitxml=test-results/junit.xml')
        
        tree = ET.parse('test-results/junit.xml')
        root = tree.getroot()
        
        # Get test counts with fallbacks
        total_tests = int(root.attrib.get('tests', 0))
        failures = int(root.attrib.get('failures', 0))
        errors = int(root.attrib.get('errors', 0))
        skipped = int(root.attrib.get('skipped', 0))
        
        # Extract test failures
        failed_tests = []
        for testcase in root.findall('.//testcase'):
            failure = testcase.find('failure')
            if failure is not None:
                failed_tests.append({
                    'name': testcase.attrib.get('name', 'Unknown Test'),
                    'message': failure.attrib.get('message', 'No message provided')
                })
        
        return {
            'total': total_tests,
            'passed': total_tests - failures - errors - skipped,
            'failures': failures,
            'errors': errors,
            'skipped': skipped,
            'failed_tests': failed_tests
        }
    except Exception as e:
        print(f"Error analyzing test results: {str(e)}")
        return {
            'total': 0,
            'passed': 0,
            'failures': 0,
            'errors': 0,
            'skipped': 0,
            'failed_tests': []
        }

def generate_html_report(coverage_data, test_data):
    """
    Generate an HTML report combining coverage and test results.
    """
    template = """
    <h2>Telemetry System Test Report</h2>
    <p>Generated on: {date}</p>
    
    <h3>Test Results Summary</h3>
    <ul>
        <li>Total Tests: {total_tests}</li>
        <li>Passed: {passed_tests}</li>
        <li>Failed: {failed_tests}</li>
        <li>Errors: {errors}</li>
        <li>Skipped: {skipped}</li>
    </ul>
    
    <h3>Coverage Summary</h3>
    <p>Overall coverage: {coverage:.2f}%</p>
    
    {low_coverage_section}
    
    {failed_tests_section}
    """
    
    # Generate low coverage section
    if coverage_data['low_coverage_modules']:
        low_coverage_section = "<h3>Modules Needing Improvement</h3><ul>"
        for module in coverage_data['low_coverage_modules']:
            low_coverage_section += f"<li>{module['name']}: {module['coverage']:.2f}%</li>"
        low_coverage_section += "</ul>"
    else:
        low_coverage_section = "<p>All modules have acceptable coverage levels.</p>"
    
    # Generate failed tests section
    if test_data['failed_tests']:
        failed_tests_section = "<h3>Failed Tests</h3><ul>"
        for test in test_data['failed_tests']:
            failed_tests_section += f"<li>{test['name']}: {test['message']}</li>"
        failed_tests_section += "</ul>"
    else:
        failed_tests_section = "<p>All tests passed successfully!</p>"
    
    # Generate the complete report
    report = template.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_tests=test_data['total'],
        passed_tests=test_data['passed'],
        failed_tests=test_data['failures'],
        errors=test_data['errors'],
        skipped=test_data['skipped'],
        coverage=coverage_data['overall_coverage'],
        low_coverage_section=low_coverage_section,
        failed_tests_section=failed_tests_section
    )
    
    # Create directories if they don't exist
    Path('test-results').mkdir(exist_ok=True)
    
    # Save the report
    with open('test_report.html', 'w') as f:
        f.write(report)
    print(f"Test report generated: {os.path.abspath('test_report.html')}")

if __name__ == '__main__':
    # Ensure test results directory exists
    Path('test-results').mkdir(exist_ok=True)
    
    print("Analyzing coverage data...")
    coverage_data = analyze_coverage_report()
    
    print("Analyzing test results...")
    test_data = analyze_test_results()
    
    print("Generating HTML report...")
    generate_html_report(coverage_data, test_data)