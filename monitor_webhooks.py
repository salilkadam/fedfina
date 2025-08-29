#!/usr/bin/env python3
"""
Real-time monitoring script for webhook activity and conversation processing
"""

import subprocess
import time
import json
import psycopg2
from datetime import datetime, timedelta
import os

# Configuration
DATABASE_URL = "postgresql://fedfina:fedfinaTh1515T0p53cr3t@pg-rw.postgres.svc.cluster.local:5432/fedfina"
NAMESPACE = "fedfina"
BACKEND_PODS = ["fedfina-backend-546679df54-2zsbc", "fedfina-backend-546679df54-vzlhq", "fedfina-backend-5c865f48df-c8lvk"]

class WebhookMonitor:
    def __init__(self):
        self.last_webhook_time = None
        self.last_conversation_time = None
        self.webhook_count = 0
        self.successful_webhooks = 0
        self.failed_webhooks = 0
        
    def get_pod_logs(self, pod_name, since_minutes=5):
        """Get recent logs from a specific pod"""
        try:
            result = subprocess.run([
                "kubectl", "logs", "-n", NAMESPACE, pod_name, 
                f"--since={since_minutes}m"
            ], capture_output=True, text=True, timeout=30)
            return result.stdout
        except Exception as e:
            return f"Error getting logs from {pod_name}: {e}"
    
    def check_webhook_activity(self):
        """Check for webhook activity across all backend pods"""
        print(f"\n🔍 Checking webhook activity at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        
        webhook_activity = []
        
        for pod in BACKEND_PODS:
            logs = self.get_pod_logs(pod, since_minutes=5)
            
            # Look for webhook-related activity
            webhook_lines = []
            for line in logs.split('\n'):
                if any(keyword in line.lower() for keyword in ['webhook', 'elevenlabs', 'signature']):
                    webhook_lines.append(line.strip())
            
            if webhook_lines:
                print(f"\n📡 {pod}:")
                for line in webhook_lines[-5:]:  # Show last 5 webhook-related lines
                    print(f"  {line}")
                webhook_activity.extend(webhook_lines)
            else:
                print(f"📡 {pod}: No webhook activity")
        
        # Count webhook attempts
        webhook_posts = sum(1 for line in webhook_activity if 'POST /api/v1/webhook' in line)
        successful_webhooks = sum(1 for line in webhook_activity if 'webhook.*success' in line.lower() or 'webhook.*completed' in line.lower())
        failed_webhooks = sum(1 for line in webhook_activity if '401' in line or 'error' in line.lower())
        
        if webhook_posts > 0:
            print(f"\n📊 Webhook Summary (last 5 minutes):")
            print(f"  - Total webhook attempts: {webhook_posts}")
            print(f"  - Successful: {successful_webhooks}")
            print(f"  - Failed: {failed_webhooks}")
            self.webhook_count += webhook_posts
            self.successful_webhooks += successful_webhooks
            self.failed_webhooks += failed_webhooks
        
        return webhook_activity
    
    def check_conversation_processing(self):
        """Check for new conversation processing in database"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Check for recent conversation processing
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            cursor.execute("""
                SELECT conversation_id, email_id, account_id, created_at 
                FROM conversation_runs 
                WHERE created_at >= %s 
                ORDER BY created_at DESC
            """, (five_minutes_ago,))
            
            recent_conversations = cursor.fetchall()
            
            if recent_conversations:
                print(f"\n🎯 New conversation processing detected:")
                print("-" * 60)
                for conv in recent_conversations:
                    print(f"  - {conv[0]} (Email: {conv[1]}, Account: {conv[2]}, Time: {conv[3]})")
            
            # Check conversation_processing table
            cursor.execute("""
                SELECT conversation_id, email_id, account_id, status, created_at 
                FROM conversation_processing 
                WHERE created_at >= %s 
                ORDER BY created_at DESC
            """, (five_minutes_ago,))
            
            recent_processing = cursor.fetchall()
            
            if recent_processing:
                print(f"\n⚙️  New processing jobs detected:")
                print("-" * 60)
                for proc in recent_processing:
                    print(f"  - {proc[0]} (Email: {proc[1]}, Account: {proc[2]}, Status: {proc[3]}, Time: {proc[4]})")
            
            cursor.close()
            conn.close()
            
            return len(recent_conversations) + len(recent_processing)
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
    
    def check_system_health(self):
        """Check overall system health"""
        try:
            # Check pod status
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", NAMESPACE, 
                "-l", "app=fedfina-backend", "-o", "json"
            ], capture_output=True, text=True, timeout=10)
            
            pods_data = json.loads(result.stdout)
            
            print(f"\n🏥 System Health Check:")
            print("-" * 40)
            
            for pod in pods_data['items']:
                pod_name = pod['metadata']['name']
                status = pod['status']['phase']
                ready = pod['status']['containerStatuses'][0]['ready'] if pod['status']['containerStatuses'] else False
                
                status_icon = "✅" if status == "Running" and ready else "❌"
                print(f"  {status_icon} {pod_name}: {status} (Ready: {ready})")
            
            # Check health endpoint
            try:
                result = subprocess.run([
                    "kubectl", "exec", "-n", NAMESPACE, BACKEND_PODS[0], 
                    "--", "curl", "-s", "http://localhost:8000/api/v1/health"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    health_data = json.loads(result.stdout)
                    print(f"  ✅ Health endpoint: {health_data.get('message', 'Unknown')}")
                else:
                    print(f"  ❌ Health endpoint: Failed")
                    
            except Exception as e:
                print(f"  ❌ Health endpoint: Error - {e}")
                
        except Exception as e:
            print(f"❌ System health check error: {e}")
    
    def run_monitoring(self, duration_minutes=60, interval_seconds=30):
        """Run continuous monitoring"""
        print(f"🚀 Starting webhook and conversation monitoring")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"🔄 Check interval: {interval_seconds} seconds")
        print(f"📊 Monitoring started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Check webhook activity
                webhook_activity = self.check_webhook_activity()
                
                # Check conversation processing
                new_conversations = self.check_conversation_processing()
                
                # Check system health (every 5 minutes)
                if datetime.now().minute % 5 == 0:
                    self.check_system_health()
                
                # Summary
                if webhook_activity or new_conversations > 0:
                    print(f"\n📈 Activity Summary:")
                    print(f"  - Total webhooks since start: {self.webhook_count}")
                    print(f"  - Successful webhooks: {self.successful_webhooks}")
                    print(f"  - Failed webhooks: {self.failed_webhooks}")
                    print(f"  - New conversations this cycle: {new_conversations}")
                
                print(f"\n⏳ Next check in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(interval_seconds)
        
        print(f"\n📊 Final Summary:")
        print(f"  - Total webhook attempts: {self.webhook_count}")
        print(f"  - Successful webhooks: {self.successful_webhooks}")
        print(f"  - Failed webhooks: {self.failed_webhooks}")
        print(f"  - Monitoring duration: {duration_minutes} minutes")

if __name__ == "__main__":
    monitor = WebhookMonitor()
    monitor.run_monitoring(duration_minutes=60, interval_seconds=30)
