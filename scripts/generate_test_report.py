import xml.etree.ElementTree as ET
import datetime
import json

def analyze_coverage_report():

    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    
    # Extract overall coverage
    coverage = float(root.attrib['line-rate']) * 100
    
    # Find modules with low coverage
    low_coverage_modules = []
    for package in root.findall('.//package'):
        for module in package.findall('classes/class'):
            module_coverage = float(module.attrib['line-rate']) * 100
            if module_coverage < 80:  # Threshold for low coverage
                low_coverage_modules.append({
                    'name': module.attrib['name'],
                    'coverage': module_coverage
                })
    
    return {
        'overall_coverage': coverage,
        'low_coverage_modules': low_coverage_modules
    }

def analyze_test_results():
    """
    Analyze the JUnit XML report to extract test statistics and failures.
    """
    tree = ET.parse('test-results/junit.xml')
    root = tree.getroot()
    
    total_tests = int(root.attrib['tests'])
    failures = int(root.attrib['failures'])
    errors = int(root.attrib['errors'])
    skipped = int(root.attrib['skipped'])
    
    # Extract test failures for detailed reporting
    failed_tests = []
    for testcase in root.findall('.//testcase'):
        failure = testcase.find('failure')
        if failure is not None:
            failed_tests.append({
                'name': testcase.attrib['name'],
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
    
    # Save the report
    with open('test_report.html', 'w') as f:
        f.write(report)

if __name__ == '__main__':
    coverage_data = analyze_coverage_report()
    test_data = analyze_test_results()
    generate_html_report(coverage_data, test_data)