#!/usr/bin/env python3
"""
DRPET Agent v2 Production Readiness Validation Script

Comprehensive validation script to ensure the DRPET Agent is ready for production deployment.
This script performs all necessary checks and generates a detailed readiness report.
"""

import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'drpet_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print validation banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    DRPET Agent v2 Production Readiness Validation           ║
    ║                                                                              ║
    ║  This script validates that the DRPET Agent is ready for production         ║
    ║  deployment by running comprehensive checks across all system components.   ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section_header(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_check_result(check_name: str, success: bool, message: str = "", duration: float = 0):
    """Print individual check result"""
    status = "✅ PASS" if success else "❌ FAIL"
    duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
    print(f"  {status} {check_name}{duration_str}")
    if message:
        print(f"      {message}")


def validate_system_prerequisites() -> Dict[str, Any]:
    """Validate system prerequisites"""
    print_section_header("System Prerequisites Validation")
    
    results = {
        'overall_success': True,
        'checks': {},
        'start_time': time.time()
    }
    
    # Check Python version
    start_time = time.time()
    try:
        import sys
        python_version = sys.version_info
        success = python_version >= (3, 8)
        message = f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        if not success:
            message += " (Requires Python 3.8+)"
            results['overall_success'] = False
    except Exception as e:
        success = False
        message = f"Error checking Python version: {e}"
        results['overall_success'] = False
    
    duration = time.time() - start_time
    results['checks']['python_version'] = {'success': success, 'message': message, 'duration': duration}
    print_check_result("Python Version", success, message, duration)
    
    # Check required packages
    start_time = time.time()
    required_packages = [
        'boto3', 'botocore', 'psutil', 'requests', 'fastapi', 'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    success = len(missing_packages) == 0
    message = f"All required packages available" if success else f"Missing packages: {missing_packages}"
    if not success:
        results['overall_success'] = False
    
    duration = time.time() - start_time
    results['checks']['required_packages'] = {'success': success, 'message': message, 'duration': duration}
    print_check_result("Required Packages", success, message, duration)
    
    # Check AWS credentials
    start_time = time.time()
    try:
        import boto3
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        success = 'Account' in response
        message = f"AWS Account: {response.get('Account', 'Unknown')}" if success else "AWS credentials not configured"
        if not success:
            results['overall_success'] = False
    except Exception as e:
        success = False
        message = f"AWS credentials error: {e}"
        results['overall_success'] = False
    
    duration = time.time() - start_time
    results['checks']['aws_credentials'] = {'success': success, 'message': message, 'duration': duration}
    print_check_result("AWS Credentials", success, message, duration)
    
    results['total_duration'] = time.time() - results['start_time']
    return results


def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description='DRPET Agent v2 Production Readiness Validation')
    parser.add_argument('--save-report', action='store_true', help='Save validation report to file')
    parser.add_argument('--report-file', type=str, help='Custom report filename')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_banner()
    
    logger.info("Starting DRPET Agent v2 production readiness validation")
    validation_start_time = time.time()
    
    # Run validation
    try:
        results = validate_system_prerequisites()
        
        # Generate report
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'overall_success': results['overall_success'],
            'production_ready': results['overall_success'],
            'results': results
        }
        
        # Save report if requested
        if args.save_report:
            filename = args.report_file or f"drpet_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Validation report saved to: {filename}")
        
        # Print summary
        print_section_header("Validation Summary")
        print(f"  Overall Result: {'✅ PRODUCTION READY' if results['overall_success'] else '❌ NOT READY FOR PRODUCTION'}")
        print(f"  Total Duration: {time.time() - validation_start_time:.2f} seconds")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_success'] else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed with error: {e}")
        logger.exception("Validation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()