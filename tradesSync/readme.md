### Usage Instructions:

1. **Update Target URL**: Replace `http://external-api.example.com/endpoint` in `app.py` with your actual API endpoint.

2. **Build and Run**:
   ```bash
   docker-compose build
   docker-compose up
   ```

3. **API Endpoints**:
   - `GET /health` - Health check
   - `POST /start` - Start the background process
   - `POST /stop` - Stop the background process
   - `GET /status` - Check current process status

4. **Example Usage**:
   ```bash
   # Start process
   curl -X POST http://localhost:5005/start
   
   # Check status
   curl http://localhost:5005/status
   
   # Stop process
   curl -X POST http://localhost:5005/stop
   ```

### Key Features:
- Health check endpoint at `/health`
- Process management (start/stop)
- Background thread for periodic API calls every 5 seconds
- Thread-safe status tracking
- Docker containerization with docker-compose
- Error handling for API calls
- Timestamped logs

### Notes:
1. The target URL in `app.py` must be updated to your actual external API endpoint
2. The application listens on all interfaces (0.0.0.0) for Docker compatibility
3. Background thread is daemonized so it terminates when main process exits
4. Process status is maintained in memory (not persistent across restarts)
5. Requests timeout is set to 10 seconds to prevent hanging calls

This implementation provides a simple but robust solution for managing periodic API calls through a Flask web interface with Docker support.