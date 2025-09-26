# Comprehensive Logging System

## **Logging Overview**

The application uses a centralized logging configuration that provides:
- **Colored console output** for development
- **Structured log files** for production
- **Performance monitoring** with execution times
- **Error tracking** with full stack traces
- **Component-specific logging** for different services

## **Log Files Structure**

```
logs/
├── app.log              # Main application logs
├── errors.log           # Error logs only
├── whatsapp.log         # WhatsApp API interactions
├── database.log         # Database operations
└── api.log              # API requests and responses
```

## **Logging Configuration**

### **Log Levels**
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors that may cause application failure

### **Log Format**
```
2024-01-15 10:30:45 | app.services.whatsapp_service | INFO | send_text_message:75 | 📤 Sending text message to +1234567890
```

### **Log Rotation**
- **Max file size**: 10MB per log file
- **Backup count**: 5 rotated files
- **Automatic cleanup**: Old logs are automatically removed

## **Colored Console Output**

The console output uses colors to make logs more readable:
- 🔵 **DEBUG**: Cyan
- 🟢 **INFO**: Green  
- 🟡 **WARNING**: Yellow
- 🔴 **ERROR**: Red
- 🟣 **CRITICAL**: Magenta

## **Component-Specific Logging**

### **WhatsApp Service**
- API requests and responses
- Message sending status
- Webhook processing
- Error handling and retries

### **Message Service**
- Message processing
- Database operations
- Contact lookups
- Conversation management

### **API Endpoints**
- Request/response logging
- Performance metrics
- Error handling
- Authentication attempts

### **Background Tasks**
- Task execution status
- Performance monitoring
- Error tracking
- Retry attempts

### **Database Operations**
- Connection management
- Query execution
- Transaction handling
- Error recovery

## **Performance Logging**

The system includes performance monitoring with decorators:

```python
@log_performance()
async def send_message(self, request: MessageSendRequest):
    # Function execution time is automatically logged
    pass
```

**Example Performance Log:**
```
2024-01-15 10:30:45 | app.services.message_service | INFO | send_message completed in 1.234s
```

## **Logging Examples**

### **Successful Message Send**
```
2024-01-15 10:30:45 | app.services.whatsapp_service | INFO | send_text_message:75 | 📤 Sending text message to +1234567890
2024-01-15 10:30:45 | app.services.whatsapp_service | DEBUG | send_text_message:77 | Message content: Hello from automation!
2024-01-15 10:30:46 | app.services.whatsapp_service | INFO | send_text_message:85 | ✅ Message sent successfully to +1234567890: wamid.1234567890
```

### **Error Handling**
```
2024-01-15 10:30:45 | app.services.whatsapp_service | ERROR | send_text_message:90 | ❌ HTTP error sending message to +1234567890: 400
2024-01-15 10:30:45 | app.services.whatsapp_service | ERROR | send_text_message:91 | Response text: {"error": {"message": "Invalid phone number"}}
```

### **Webhook Processing**
```
2024-01-15 10:30:45 | app.api.webhooks | INFO | receive_webhook:66 | 📨 Webhook data received from Meta
2024-01-15 10:30:45 | app.api.webhooks | INFO | receive_webhook:71 | 📊 Webhook data structure: ['entry']
2024-01-15 10:30:45 | app.api.webhooks | INFO | receive_webhook:77 | ✅ Webhook processing completed: {'messages_processed': 1, 'statuses_processed': 0, 'errors': []}
```

## **Development Usage**

### **Viewing Logs in Development**
```bash
# View all logs
tail -f logs/app.log

# View errors only
tail -f logs/errors.log

# View WhatsApp logs
tail -f logs/whatsapp.log

# View database logs
tail -f logs/database.log
```

### **Docker Logs**
```bash
# View backend logs
docker-compose logs -f backend

# View Celery worker logs
docker-compose logs -f celery_worker

# View all services
docker-compose logs -f
```

## **Production Considerations**

### **Log Rotation**
- Logs are automatically rotated when they reach 10MB
- Old logs are kept for 5 rotations
- Disk space is managed automatically

### **Performance Impact**
- Logging is asynchronous where possible
- Debug logging can be disabled in production
- File I/O is optimized for high throughput

### **Security**
- Sensitive data is masked in logs
- API keys and tokens are not logged
- Personal information is anonymized

## 📈 **Monitoring and Alerting**

### **Key Metrics to Monitor**
- Error rates by component
- Performance bottlenecks
- Failed API calls
- Database connection issues
- Background task failures

### **Log Analysis**
```bash
# Count errors by component
grep "ERROR" logs/app.log | cut -d'|' -f3 | sort | uniq -c

# Find performance issues
grep "completed in" logs/app.log | awk '{print $NF}' | sort -n

# Monitor WhatsApp API errors
grep "HTTP error" logs/whatsapp.log
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable debug mode
DEBUG=true

# Environment
ENVIRONMENT=production
```

### **Custom Logging**
```python
from app.core.logging import get_logger, log_performance

logger = get_logger(__name__)

@log_performance()
def my_function():
    logger.info("Starting my function")
    # Your code here
    logger.info("Function completed successfully")
```

### **Common Issues**

1. **Logs not appearing**:
   - Check log directory permissions
   - Verify logging configuration
   - Check disk space

2. **Performance issues**:
   - Reduce log level in production
   - Monitor disk I/O
   - Check log rotation

3. **Missing logs**:
   - Check file permissions
   - Verify volume mounts
   - Check container logs

### **Debug Commands**
```bash
# Check log file permissions
ls -la logs/

# Monitor disk usage
du -sh logs/

# Check for errors
grep -i error logs/app.log | tail -20

# Monitor real-time logs
tail -f logs/app.log | grep -E "(ERROR|WARNING)"
```