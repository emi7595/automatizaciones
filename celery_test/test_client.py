"""
Test client to send tasks to the Railway worker.
"""
import time
from celery_test.celery_config import celery_app
from celery_test.test_tasks import (
    simple_test_task,
    echo_task,
    processing_test_task,
    error_test_task,
    random_data_task
)

def test_worker_connection():
    """Test basic worker connection."""
    print("🧪 Testing worker connection...")
    
    # Send simple test task
    result = simple_test_task.delay()
    print(f"📤 Sent simple test task: {result.id}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"📥 Simple test result: {task_result}")
        return True
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False

def test_echo_functionality():
    """Test parameter passing."""
    print("🧪 Testing echo functionality...")
    
    test_message = "Hello from Railway worker test!"
    result = echo_task.delay(test_message)
    print(f"📤 Sent echo task: {result.id}")
    
    try:
        task_result = result.get(timeout=30)
        print(f"📥 Echo result: {task_result}")
        return task_result.get("echo") == test_message
    except Exception as e:
        print(f"❌ Echo test failed: {e}")
        return False

def test_processing_task():
    """Test longer processing task."""
    print("🧪 Testing processing task...")
    
    result = processing_test_task.delay(duration=3)
    print(f"📤 Sent processing task: {result.id}")
    
    try:
        task_result = result.get(timeout=30)
        print(f"📥 Processing result: {task_result}")
        return task_result.get("status") == "completed"
    except Exception as e:
        print(f"❌ Processing test failed: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print("🧪 Testing error handling...")
    
    # Test successful task
    result1 = error_test_task.delay(should_fail=False)
    print(f"📤 Sent success error test: {result1.id}")
    
    # Test failing task
    result2 = error_test_task.delay(should_fail=True)
    print(f"📤 Sent failure error test: {result2.id}")
    
    try:
        # Should succeed
        task_result1 = result1.get(timeout=30)
        print(f"📥 Success result: {task_result1}")
        
        # Should fail
        try:
            task_result2 = result2.get(timeout=30)
            print(f"❌ Expected failure but got: {task_result2}")
            return False
        except Exception as e:
            print(f"📥 Expected failure caught: {e}")
            return True
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_data_handling():
    """Test data handling with random numbers."""
    print("🧪 Testing data handling...")
    
    result = random_data_task.delay(count=20)
    print(f"📤 Sent random data task: {result.id}")
    
    try:
        task_result = result.get(timeout=30)
        print(f"📥 Random data result: {task_result}")
        return task_result.get("status") == "success"
    except Exception as e:
        print(f"❌ Data handling test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting Railway worker tests...")
    print("=" * 50)
    
    tests = [
        ("Worker Connection", test_worker_connection),
        ("Echo Functionality", test_echo_functionality),
        ("Processing Task", test_processing_task),
        ("Error Handling", test_error_handling),
        ("Data Handling", test_data_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print("-" * 30)
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Railway worker is working correctly.")
    else:
        print("⚠️ Some tests failed. Check worker configuration and logs.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
