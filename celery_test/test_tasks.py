"""
Simple test tasks to verify Railway worker functionality.
"""
from celery_config import celery_app
import time
import random

@celery_app.task(bind=True)
def simple_test_task(self):
    """Simple test task that returns basic information."""
    print(f"🧪 SIMPLE TEST TASK EXECUTED")
    print(f"🧪 Task ID: {self.request.id}")
    print(f"🧪 Worker: {self.request.hostname}")
    print(f"🧪 Queue: {self.request.delivery_info.get('routing_key', 'default')}")
    
    return {
        "status": "success",
        "message": "Simple test task completed",
        "task_id": self.request.id,
        "worker": self.request.hostname
    }

@celery_app.task(bind=True)
def echo_task(self, message):
    """Echo back a message to test parameter passing."""
    print(f"📢 ECHO TASK RECEIVED: {message}")
    print(f"📢 Task ID: {self.request.id}")
    
    return {
        "status": "success",
        "echo": message,
        "task_id": self.request.id
    }

@celery_app.task(bind=True)
def processing_test_task(self, duration=5):
    """Test task that simulates processing for a specified duration."""
    print(f"⏱️ PROCESSING TEST TASK STARTED - Duration: {duration}s")
    print(f"⏱️ Task ID: {self.request.id}")
    
    # Simulate processing
    for i in range(duration):
        print(f"⏱️ Processing... {i+1}/{duration}")
        time.sleep(1)
    
    result = {
        "status": "completed",
        "duration": duration,
        "task_id": self.request.id,
        "message": f"Processed for {duration} seconds"
    }
    
    print(f"⏱️ PROCESSING TEST TASK COMPLETED")
    return result

@celery_app.task(bind=True)
def error_test_task(self, should_fail=False):
    """Test task that can optionally fail to test error handling."""
    print(f"❌ ERROR TEST TASK - Should fail: {should_fail}")
    print(f"❌ Task ID: {self.request.id}")
    
    if should_fail:
        raise Exception("This is a test error - task failed as expected")
    
    return {
        "status": "success",
        "message": "Error test task completed successfully",
        "task_id": self.request.id
    }

@celery_app.task(bind=True)
def random_data_task(self, count=10):
    """Generate random data to test data handling."""
    print(f"🎲 RANDOM DATA TASK - Generating {count} random numbers")
    print(f"🎲 Task ID: {self.request.id}")
    
    random_numbers = [random.randint(1, 100) for _ in range(count)]
    
    return {
        "status": "success",
        "count": count,
        "random_numbers": random_numbers,
        "sum": sum(random_numbers),
        "average": sum(random_numbers) / len(random_numbers),
        "task_id": self.request.id
    }

print("🚀 Test tasks module loaded")
