"""
Script to run comprehensive security tests and generate reports
"""
import subprocess
import json
import time
from pathlib import Path
from brownie import network


def run_brownie_tests(test_file, output_file=None):
    """Run brownie tests and capture output"""
    print(f"🧪 Running {test_file}...")
    
    cmd = ["brownie", "test", test_file, "-v", "--tb=short"]
    
    if output_file:
        cmd.extend(["--html", f"reports/{output_file}", "--self-contained-html"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"✅ Tests completed for {test_file}")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ Tests timed out for {test_file}")
        return False
    except Exception as e:
        print(f"❌ Error running tests for {test_file}: {e}")
        return False


def run_security_scan():
    """Run security scan with Slither"""
    print("🔍 Running Slither security scan...")
    
    try:
        cmd = ["slither", "contracts/", "--json", "reports/slither_report.json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Slither scan completed successfully")
            
            # Parse and display results
            try:
                with open("reports/slither_report.json", "r") as f:
                    slither_results = json.load(f)
                
                print(f"📊 Slither found {len(slither_results.get('results', {}).get('detectors', []))} issues")
                
                for detector in slither_results.get('results', {}).get('detectors', []):
                    print(f"⚠️  {detector.get('check', 'Unknown')}: {detector.get('description', 'No description')}")
                    
            except Exception as e:
                print(f"Error parsing Slither results: {e}")
                
        else:
            print("❌ Slither scan failed")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Slither scan timed out")
    except FileNotFoundError:
        print("❌ Slither not found. Install with: pip install slither-analyzer")
    except Exception as e:
        print(f"❌ Error running Slither: {e}")


def generate_comprehensive_report():
    """Generate comprehensive security report"""
    print("📊 Generating comprehensive security report...")
    
    report = {
        "timestamp": int(time.time()),
        "network": network.show_active(),
        "test_results": {},
        "vulnerabilities": [],
        "summary": {}
    }
    
    # Collect test results
    test_files = [
        "test_security_comprehensive.py",
        "test_reentrancy_specific.py"
    ]
    
    total_vulnerabilities = 0
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    for test_file in test_files:
        report_file = test_file.replace(".py", "_report.json")
        report_path = Path(f"reports/{report_file}")
        
        if report_path.exists():
            try:
                with open(report_path, "r") as f:
                    test_results = json.load(f)
                
                report["test_results"][test_file] = test_results
                
                # Count vulnerabilities
                for result in test_results.values():
                    if isinstance(result, dict) and "vulnerabilities" in result:
                        vulns = result["vulnerabilities"]
                        total_vulnerabilities += len(vulns)
                        
                        for vuln in vulns:
                            severity = vuln.get("severity", "LOW")
                            severity_counts[severity] += 1
                            report["vulnerabilities"].append({
                                "test_file": test_file,
                                "type": vuln.get("type", "Unknown"),
                                "description": vuln.get("description", "No description"),
                                "severity": severity
                            })
                        
            except Exception as e:
                print(f"Error reading {report_file}: {e}")
    
    # Add Slither results
    slither_path = Path("reports/slither_report.json")
    if slither_path.exists():
        try:
            with open(slither_path, "r") as f:
                slither_results = json.load(f)
            
            report["slither_results"] = slither_results
            
            # Count Slither issues
            for detector in slither_results.get('results', {}).get('detectors', []):
                severity = "HIGH" if "critical" in detector.get('impact', '').lower() else "MEDIUM"
                severity_counts[severity] += 1
                total_vulnerabilities += 1
                
                report["vulnerabilities"].append({
                    "test_file": "slither",
                    "type": detector.get('check', 'Unknown'),
                    "description": detector.get('description', 'No description'),
                    "severity": severity
                })
                
        except Exception as e:
            print(f"Error reading Slither results: {e}")
    
    # Generate summary
    report["summary"] = {
        "total_vulnerabilities": total_vulnerabilities,
        "severity_counts": severity_counts,
        "risk_level": "HIGH" if severity_counts["HIGH"] > 0 else "MEDIUM" if severity_counts["MEDIUM"] > 0 else "LOW"
    }
    
    # Save comprehensive report
    with open("reports/comprehensive_security_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown report
    generate_markdown_report(report)
    
    print(f"📄 Comprehensive report saved to: reports/comprehensive_security_report.json")
    print(f"📄 Markdown report saved to: reports/security_report.md")
    
    return report


def generate_markdown_report(report):
    """Generate markdown security report"""
    markdown = f"""# 🔒 Smart Contract Security Report

Generated on: {time.ctime(report['timestamp'])}
Network: {report['network']}

## 📊 Executive Summary

- **Total Vulnerabilities**: {report['summary']['total_vulnerabilities']}
- **Risk Level**: {report['summary']['risk_level']}
- **High Severity**: {report['summary']['severity_counts']['HIGH']}
- **Medium Severity**: {report['summary']['severity_counts']['MEDIUM']}
- **Low Severity**: {report['summary']['severity_counts']['LOW']}

## 🚨 Critical Findings

"""
    
    # Add high severity vulnerabilities
    high_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'HIGH']
    if high_vulns:
        markdown += "### High Severity Vulnerabilities\n\n"
        for vuln in high_vulns:
            markdown += f"- **{vuln['type']}**: {vuln['description']} (Found in {vuln['test_file']})\n"
        markdown += "\n"
    
    # Add medium severity vulnerabilities
    medium_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'MEDIUM']
    if medium_vulns:
        markdown += "### Medium Severity Vulnerabilities\n\n"
        for vuln in medium_vulns:
            markdown += f"- **{vuln['type']}**: {vuln['description']} (Found in {vuln['test_file']})\n"
        markdown += "\n"
    
    # Add low severity vulnerabilities
    low_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'LOW']
    if low_vulns:
        markdown += "### Low Severity Vulnerabilities\n\n"
        for vuln in low_vulns:
            markdown += f"- **{vuln['type']}**: {vuln['description']} (Found in {vuln['test_file']})\n"
        markdown += "\n"
    
    # Add recommendations
    markdown += """## 🛡️ Security Recommendations

1. **Immediate Actions Required**:
   - Fix all HIGH severity vulnerabilities before deployment
   - Implement proper access controls
   - Add reentrancy protection to all external calls

2. **Short-term Improvements**:
   - Address MEDIUM severity vulnerabilities
   - Implement proper input validation
   - Add event logging for security monitoring

3. **Long-term Security**:
   - Conduct regular security audits
   - Implement formal verification
   - Set up bug bounty program

## 📋 Test Coverage

"""
    
    for test_file, results in report['test_results'].items():
        markdown += f"### {test_file}\n"
        if isinstance(results, dict) and 'total_vulnerabilities' in results:
            markdown += f"- Vulnerabilities Found: {results['total_vulnerabilities']}\n"
        markdown += "\n"
    
    markdown += """
## 🔍 Tools Used

- **Brownie**: Smart contract testing framework
- **Slither**: Static analysis tool
- **Custom Security Tests**: Comprehensive vulnerability detection

---

*Report generated by Blockchain Security Testing Framework*
"""
    
    with open("reports/security_report.md", "w") as f:
        f.write(markdown)


def main():
    """Main function to run all security tests"""
    print("🚀 Starting comprehensive security testing...")
    print(f"Network: {network.show_active()}")
    
    # Create reports directory
    Path("reports").mkdir(exist_ok=True)
    
    # Run test suites
    test_files = [
        ("tests/test_security_comprehensive.py", "comprehensive_tests.html"),
        ("tests/test_reentrancy_specific.py", "reentrancy_tests.html")
    ]
    
    test_results = {}
    
    for test_file, output_file in test_files:
        success = run_brownie_tests(test_file, output_file)
        test_results[test_file] = success
    
    # Run security scan
    run_security_scan()
    
    # Generate comprehensive report
    report = generate_comprehensive_report()
    
    # Print summary
    print("\n" + "="*50)
    print("🎯 SECURITY TESTING SUMMARY")
    print("="*50)
    print(f"Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
    print(f"Risk Level: {report['summary']['risk_level']}")
    print(f"High Severity: {report['summary']['severity_counts']['HIGH']}")
    print(f"Medium Severity: {report['summary']['severity_counts']['MEDIUM']}")
    print(f"Low Severity: {report['summary']['severity_counts']['LOW']}")
    print("="*50)
    
    if report['summary']['severity_counts']['HIGH'] > 0:
        print("⚠️  CRITICAL: High severity vulnerabilities found!")
        print("🚨 Do NOT deploy to production without fixing these issues!")
    elif report['summary']['severity_counts']['MEDIUM'] > 0:
        print("⚠️  WARNING: Medium severity vulnerabilities found!")
        print("🔧 Address these issues before production deployment.")
    else:
        print("✅ Good: No critical vulnerabilities found!")
        print("🎉 Ready for production deployment!")
    
    print("\n📄 Reports generated:")
    print("- reports/comprehensive_security_report.json")
    print("- reports/security_report.md")
    print("- reports/slither_report.json")
    
    return report


if __name__ == "__main__":
    main()
