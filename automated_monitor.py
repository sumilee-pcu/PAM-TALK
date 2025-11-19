#!/usr/bin/env python3
"""
Automated PAM-TALK Transaction Monitor
Runs in background and saves reports to files
"""

import requests
import time
import json
import os
from datetime import datetime

class PAMTalkMonitor:
    def __init__(self):
        self.tx_id = "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
        self.admin_addr = "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM"
        self.reports_dir = "monitoring_reports"

        # Create reports directory
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def check_account(self):
        """Check account balance and status"""
        try:
            url = f"https://testnet-api.algonode.cloud/v2/accounts/{self.admin_addr}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                account_info = data.get('account', {})

                return {
                    'success': True,
                    'balance': account_info.get('amount', 0) / 1000000,
                    'status': account_info.get('status', 'Unknown'),
                    'assets': len(account_info.get('assets', [])),
                    'created_apps': len(account_info.get('created-apps', [])),
                    'created_assets': len(account_info.get('created-assets', []))
                }
            else:
                return {'success': False, 'error': f'API_ERROR_{response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_transaction(self):
        """Check transaction status"""
        try:
            url = f"https://testnet-api.algonode.cloud/v2/transactions/{self.tx_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tx_data = data.get('transaction', {})

                result = {
                    'success': True,
                    'status': 'CONFIRMED',
                    'round': tx_data.get('confirmed-round'),
                    'type': tx_data.get('tx-type'),
                    'sender': tx_data.get('sender'),
                    'fee': tx_data.get('fee', 0) / 1000000
                }

                # Payment transaction details
                if 'payment-transaction' in tx_data:
                    payment = tx_data['payment-transaction']
                    result['amount'] = payment.get('amount', 0) / 1000000
                    result['receiver'] = payment.get('receiver')

                return result

            elif response.status_code == 404:
                return {
                    'success': True,
                    'status': 'PENDING',
                    'message': 'Transaction not yet on blockchain'
                }
            else:
                return {'success': False, 'error': f'API_ERROR_{response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_report(self):
        """Generate comprehensive status report"""
        timestamp = datetime.now()

        # Get current status
        account_data = self.check_account()
        tx_data = self.check_transaction()

        # Create report
        report = {
            'timestamp': timestamp.isoformat(),
            'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction': {
                'id': self.tx_id,
                'data': tx_data
            },
            'account': {
                'address': self.admin_addr,
                'data': account_data
            }
        }

        # Determine overall status
        if account_data.get('success') and account_data.get('balance', 0) > 0:
            report['overall_status'] = 'FUNDED'
            report['next_action'] = 'Ready to create PAM token'
        elif tx_data.get('success') and tx_data.get('status') == 'CONFIRMED':
            report['overall_status'] = 'TX_CONFIRMED_BALANCE_PENDING'
            report['next_action'] = 'Wait for balance update or check API sync'
        elif tx_data.get('success') and tx_data.get('status') == 'PENDING':
            report['overall_status'] = 'TX_PENDING'
            report['next_action'] = 'Wait for transaction confirmation'
        else:
            report['overall_status'] = 'ERROR'
            report['next_action'] = 'Check errors and retry funding'

        return report

    def save_report(self, report):
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reports_dir}/pam_status_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return filename

    def print_summary(self, report):
        """Print human-readable summary"""
        print(f"PAM-TALK Status Report - {report['formatted_time']}")
        print("=" * 50)

        # Account status
        acc_data = report['account']['data']
        if acc_data.get('success'):
            balance = acc_data.get('balance', 0)
            print(f"Account Balance: {balance:.6f} ALGO")
            print(f"Account Status: {acc_data.get('status', 'Unknown')}")
            print(f"Assets: {acc_data.get('assets', 0)}")
        else:
            print(f"Account Error: {acc_data.get('error', 'Unknown')}")

        print()

        # Transaction status
        tx_data = report['transaction']['data']
        if tx_data.get('success'):
            status = tx_data.get('status', 'Unknown')
            print(f"Transaction Status: {status}")

            if status == 'CONFIRMED':
                print(f"Round: {tx_data.get('round', 'N/A')}")
                print(f"Amount: {tx_data.get('amount', 0):.6f} ALGO")
            elif status == 'PENDING':
                print("Note: Transaction still processing")
        else:
            print(f"Transaction Error: {tx_data.get('error', 'Unknown')}")

        print()

        # Overall status
        print(f"Overall Status: {report['overall_status']}")
        print(f"Next Action: {report['next_action']}")

        return report['overall_status']

    def monitor_until_funded(self, max_hours=2, check_interval=300):
        """Monitor continuously until funding is complete"""
        print(f"Starting automated monitoring...")
        print(f"Max duration: {max_hours} hours")
        print(f"Check interval: {check_interval} seconds")
        print("=" * 50)

        start_time = datetime.now()
        max_duration = max_hours * 3600  # Convert to seconds

        while True:
            # Generate and save report
            report = self.generate_report()
            filename = self.save_report(report)

            # Print summary
            status = self.print_summary(report)
            print(f"Report saved: {filename}")
            print("-" * 50)

            # Check if funding is complete
            if status == 'FUNDED':
                print("SUCCESS: Funding completed!")
                print("Ready to proceed with PAM token creation")
                break

            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= max_duration:
                print(f"TIMEOUT: Monitoring stopped after {max_hours} hours")
                print("Current status: Still waiting for funding")
                break

            # Wait for next check
            remaining = max_duration - elapsed
            next_check = min(check_interval, remaining)
            print(f"Next check in {next_check:.0f} seconds...")
            print()

            time.sleep(next_check)

def main():
    monitor = PAMTalkMonitor()

    print("PAM-TALK Automated Transaction Monitor")
    print("=" * 40)
    print("1. Single status check")
    print("2. Monitor until funded (2 hours max)")
    print("3. Quick 30-minute monitor")
    print()

    choice = input("Select option (1-3): ").strip()

    if choice == "1":
        report = monitor.generate_report()
        filename = monitor.save_report(report)
        monitor.print_summary(report)
        print(f"\\nReport saved: {filename}")

    elif choice == "2":
        monitor.monitor_until_funded(max_hours=2, check_interval=300)

    elif choice == "3":
        monitor.monitor_until_funded(max_hours=0.5, check_interval=120)

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()