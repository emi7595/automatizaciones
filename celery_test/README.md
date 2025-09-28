# Celery Test Setup

This is a minimal Celery configuration for testing Railway worker functionality.

## Files

- `celery_config.py` - Minimal Celery configuration
- `test_tasks.py` - Simple test tasks
- `test_client.py` - Test client to send tasks to worker
- `requirements.txt` - Dependencies

## Usage

### 1. Start the Worker

```bash
# In the celery_test directory
celery -A celery_config worker --loglevel=info
```

### 2. Run Tests

```bash
# In another terminal, run the test client
python test_client.py
```

### 3. Environment Variables

Make sure these environment variables are set:

```bash
export REDIS_URL="redis://localhost:6379"
export CELERY_BROKER_URL="redis://localhost:6379"
export CELERY_RESULT_BACKEND="redis://localhost:6379"
```

For Railway deployment, these will be automatically set by Railway.

## Test Tasks

The test includes:

1. **Simple Test** - Basic connection test
2. **Echo Test** - Parameter passing test
3. **Processing Test** - Long-running task test
4. **Error Test** - Error handling test
5. **Data Test** - Data handling test

## Railway Deployment

To test on Railway:

1. Deploy the worker with this minimal configuration
2. Run the test client from your local machine or another service
3. Check Railway logs to see task execution

## Expected Output

When working correctly, you should see:

```
🚀 Starting Railway worker tests...
🧪 Testing worker connection...
📤 Sent simple test task: [task-id]
📥 Simple test result: {'status': 'success', 'message': 'Simple test task completed', ...}
✅ Worker Connection: PASSED
...
🎉 All tests passed! Railway worker is working correctly.
```
