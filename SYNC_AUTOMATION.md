# Prop Firm Sync Automation

This document explains how to automatically call the `sync_prop_firms()` endpoint every 5 seconds using either SvelteKit (frontend) or Python (backend) approaches.

## Overview

I've created a mechanism that allows you to sync prop firms automatically without authentication. This includes:

1. **Public Sync Endpoint**: A new endpoint `/prop_firms/sync_public` that doesn't require authentication
2. **SvelteKit Service**: Frontend-based auto-sync with UI controls
3. **Python Scheduler**: Standalone Python script for backend automation

## 🔧 Backend Changes

### New Public Endpoint

A new public endpoint has been added to `app/routes/prop_firms.py`:

```
POST /prop_firms/sync_public
```

This endpoint:
- Does **NOT** require authentication (no `@login_required` decorator)
- Accepts the same parameters as the original sync endpoint
- Shares the same logic as the authenticated endpoint
- Is designed specifically for automated/scheduled calls

**Usage:**
```bash
# Sync all active prop firms
curl -X POST http://localhost:5000/prop_firms/sync_public \
  -H "Content-Type: application/json" \
  -d '{}'

# Sync specific prop firm
curl -X POST http://localhost:5000/prop_firms/sync_public \
  -H "Content-Type: application/json" \
  -d '{"prop_firm_id": 123}'
```

## 🌐 SvelteKit Frontend Approach

### Auto Sync Service

**Location:** `frontend/src/lib/services/syncService.ts`

**Features:**
- Automatically calls sync endpoint every 5 seconds
- Start/stop controls
- Manual sync trigger
- Error handling and logging
- No authentication required

**Usage in Svelte Components:**

```typescript
import { startAutoSync, stopAutoSync, isAutoSyncRunning, manualSync } from '$lib/services/syncService';

// Start automatic syncing
startAutoSync();

// Stop automatic syncing
stopAutoSync();

// Check if running
const isRunning = isAutoSyncRunning();

// Manual sync
const result = await manualSync();
```

### Auto Sync Manager Component

**Location:** `frontend/src/lib/components/AutoSyncManager.svelte`

**Features:**
- Visual status indicator (green/red dot)
- Start/Stop buttons
- Manual sync button
- Status messages
- Automatic cleanup on component destroy

**Usage:**
```svelte
<script>
    import AutoSyncManager from '$lib/components/AutoSyncManager.svelte';
</script>

<AutoSyncManager />
```

**Integration Example:**
Add to your prop firms overview page:

```svelte
<!-- In frontend/src/routes/(authed)/prop_firms/overview/+page.svelte -->
<script lang="ts">
    import AutoSyncManager from '$lib/components/AutoSyncManager.svelte';
    // ... existing code
</script>

<AutoSyncManager />
<!-- ... rest of your page -->
```

## 🐍 Python Standalone Approach

### Sync Scheduler Script

**Location:** `sync_scheduler.py`

**Features:**
- Standalone Python script
- Configurable sync interval
- Command-line arguments
- Comprehensive logging
- Single sync or continuous mode
- Graceful error handling

### Installation

The script uses the `requests` library which is already in your `requirements.txt`.

### Usage

#### Basic Usage (Every 5 seconds)
```bash
python sync_scheduler.py
```

#### Custom Configuration
```bash
# Custom URL and interval
python sync_scheduler.py --url http://localhost:5000 --interval 10

# Sync specific prop firm
python sync_scheduler.py --prop-firm-id 123

# Run once (no scheduling)
python sync_scheduler.py --once

# Full example
python sync_scheduler.py --url http://your-server.com --interval 30 --prop-firm-id 456
```

#### Command Line Arguments
- `--url`: Base URL of Flask application (default: http://localhost:5000)
- `--interval`: Sync interval in seconds (default: 5)
- `--prop-firm-id`: Specific prop firm ID to sync (optional)
- `--once`: Run sync once and exit

#### Running as Background Service

**Linux/macOS:**
```bash
# Run in background
nohup python sync_scheduler.py > sync.log 2>&1 &

# Check if running
ps aux | grep sync_scheduler

# Stop
pkill -f sync_scheduler.py
```

**Windows:**
```cmd
# Run in background
start /B python sync_scheduler.py

# Or use Windows Service Wrapper (NSSM) for proper service installation
```

#### Logging

The script creates a `sync_scheduler.log` file with detailed logs:
```
2024-01-15 10:30:00 - INFO - Starting prop firm sync scheduler (interval: 5s)
2024-01-15 10:30:00 - INFO - Performing initial sync...
2024-01-15 10:30:01 - INFO - Sync successful: Synced 3 out of 5 prop firms
2024-01-15 10:30:06 - INFO - Sync successful: Synced 3 out of 5 prop firms
```

## 🚀 Quick Start

### Option 1: SvelteKit Frontend (Recommended for Development)

1. Import the AutoSyncManager component in your prop firms page:
```svelte
<script>
    import AutoSyncManager from '$lib/components/AutoSyncManager.svelte';
</script>

<AutoSyncManager />
```

2. Start syncing from the UI or programmatically:
```typescript
import { startAutoSync } from '$lib/services/syncService';
startAutoSync();
```

### Option 2: Python Script (Recommended for Production)

1. Run the scheduler:
```bash
python sync_scheduler.py
```

2. For production, run as a service:
```bash
nohup python sync_scheduler.py --interval 5 > sync.log 2>&1 &
```

## 🔍 Monitoring and Troubleshooting

### SvelteKit Approach
- Check browser console for sync results
- Use the AutoSyncManager component to see real-time status
- Network tab shows HTTP requests to the sync endpoint

### Python Approach
- Check `sync_scheduler.log` for detailed logs
- Monitor the process with `ps aux | grep sync_scheduler`
- HTTP errors and network issues are logged with timestamps

### Common Issues

1. **Connection Refused**: Make sure your Flask app is running
2. **404 Error**: Verify the endpoint URL is correct
3. **500 Error**: Check Flask app logs for backend issues
4. **High CPU Usage**: Consider increasing the sync interval

## 🛡️ Security Considerations

The public endpoint `/sync_public` does not require authentication by design, making it suitable for automated calls. However:

1. **Network Security**: Ensure this endpoint is not exposed to untrusted networks
2. **Rate Limiting**: Consider implementing rate limiting if needed
3. **Monitoring**: Monitor sync frequency and results
4. **Access Control**: Use firewall rules to restrict access if necessary

## 📝 Integration Examples

### Start Auto Sync on Page Load
```svelte
<script>
    import { onMount } from 'svelte';
    import { startAutoSync } from '$lib/services/syncService';
    
    onMount(() => {
        startAutoSync();
    });
</script>
```

### Conditional Auto Sync
```typescript
// Only start auto sync for admin users
if (user.role === 'admin') {
    startAutoSync();
}
```

### Environment-Based Sync
```typescript
// Different intervals for different environments
const interval = process.env.NODE_ENV === 'production' ? 10 : 5;
// Configure sync accordingly
```

---

Choose the approach that best fits your deployment scenario:
- **SvelteKit**: Better for development and when you want UI controls
- **Python Script**: Better for production deployments and server-side automation
