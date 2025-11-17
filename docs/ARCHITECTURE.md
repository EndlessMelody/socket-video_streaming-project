# Video Streaming over Socket - Architecture Document

## 1. SYSTEM OVERVIEW

### 1.1 Objectives

- Build a real-time video streaming system using socket programming
- Support 1-to-many video broadcasting (one sender, multiple viewers)
- Implement frame buffering and synchronization
- Support multiple video quality levels with dynamic adjustment
- Ensure low latency video transmission

### 1.2 Tech Stack

- **Core:** Python 3.10+, socket, threading
- **Video Processing:** OpenCV (cv2), PyAV, NumPy
- **Video Codecs:** H.264 (primary), MJPEG (fallback)
- **Database:** SQLite (session logging)
- **Frontend:** PyQt5 (GUI for video display/controls)
- **Testing:** pytest
- **Deployment:** Docker

### 1.3 Key Features

- Real-time video capture from webcam
- Video encoding and compression (H.264/MJPEG)
- Frame packetization for network transmission
- Multi-client video broadcasting
- Frame buffering and drop mechanism
- Quality adaptation (Low/Medium/High/Ultra)
- Session persistence and viewer logging

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    BROADCASTER CLIENT                             │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Video Capture Module (OpenCV)                             │ │
│  │    - Initialize webcam                                     │ │
│  │    - Capture frames at specified FPS                       │ │
│  │    - Pre-processing (resize, format conversion)            │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │ Raw frames                                   │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  Video Encoder (PyAV/H.264)                                │ │
│  │    - Encode frames using H.264/MJPEG                       │ │
│  │    - Apply compression based on quality settings           │ │
│  │    - Generate keyframes periodically                       │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │ Encoded frames                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  Frame Packetizer                                          │ │
│  │    - Add frame header (seq, timestamp, size, flags)        │ │
│  │    - Split large frames into chunks                        │ │
│  │    - Prepare for socket transmission                       │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │ Video packets                                │
└───────────────────┼──────────────────────────────────────────────┘
                    │ TCP Socket
                    │
┌───────────────────▼──────────────────────────────────────────────┐
│                    VIDEO STREAMING SERVER                         │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Socket Server (Main Thread)                               │ │
│  │    - Accept broadcaster connection                         │ │
│  │    - Accept viewer connections                             │ │
│  │    - Manage video sessions                                 │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  Video Frame Handler                                       │ │
│  │    - Receive video packets from broadcaster                │ │
│  │    - Parse frame headers                                   │ │
│  │    - Reassemble chunked frames                             │ │
│  │    - Validate frame integrity                              │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  Frame Buffer Manager                                      │ │
│  │    - Circular buffer for frame storage                     │ │
│  │    - Frame drop logic when buffer full                     │ │
│  │    - Priority queue (keyframes > P-frames)                 │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  Broadcaster (Multi-threaded)                              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │ │
│  │  │ Thread 1 │  │ Thread 2 │  │ Thread N │                │ │
│  │  │ Viewer 1 │  │ Viewer 2 │  │ Viewer N │                │ │
│  │  └──────────┘  └──────────┘  └──────────┘                │ │
│  │    - Send frames to connected viewers                      │ │
│  │    - Handle viewer quality preferences                     │ │
│  │    - Monitor bandwidth and adjust                          │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │ TCP Sockets (Multiple)
                    │
┌───────────────────▼──────────────────────────────────────────────┐
│                    VIEWER CLIENTS                                 │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Viewer 1    │  │  Viewer 2    │  │  Viewer N    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│  ┌──────▼──────────────────▼──────────────────▼───────────────┐ │
│  │  Frame Receiver                                             │ │
│  │    - Receive video packets                                 │ │
│  │    - Parse frame headers                                   │ │
│  │    - Reassemble frames                                     │ │
│  └────────────────┬────────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼────────────────────────────────────────────┐ │
│  │  Frame Buffer                                               │ │
│  │    - Buffer incoming frames                                │ │
│  │    - Handle jitter and network delays                      │ │
│  └────────────────┬────────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼────────────────────────────────────────────┐ │
│  │  Video Decoder                                              │ │
│  │    - Decode H.264/MJPEG frames                             │ │
│  │    - Convert to display format (RGB)                       │ │
│  └────────────────┬────────────────────────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼────────────────────────────────────────────┐ │
│  │  Video Display (GUI)                                        │ │
│  │    - Render frames using OpenCV/PyQt5                      │ │
│  │    - Display FPS and latency stats                         │ │
│  │    - Quality control UI                                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                 │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              SQLite Database                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Video       │  │  Viewer     │  │  Session    │        │ │
│  │  │ Sessions    │  │  Logs       │  │  Stats      │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

#### Broadcasting Flow (Sender → Server → Viewers)

```
[Webcam]
    ↓ (30 FPS raw frames)
[Capture Thread]
    ↓ (Resize, preprocess)
[Encoder]
    ↓ (H.264 compressed frames)
[Packetizer]
    ↓ (Frame packets with headers)
[Socket Send]
    ↓ (TCP transmission)
[Server Receive]
    ↓ (Frame validation)
[Frame Buffer]
    ↓ (Buffered frames)
[Broadcast Threads] → → → [Viewer 1] [Viewer 2] [Viewer N]
    ↓ (Per-client sockets)
[Viewer Receive]
    ↓ (Frame reassembly)
[Viewer Buffer]
    ↓ (Jitter handling)
[Decoder]
    ↓ (RGB frames)
[Display]
```

---

## 3. COMPONENT ARCHITECTURE

### 3.1 Server Components

#### 3.1.1 Socket Server (`socket_server.py`)

**Responsibilities:**

- Initialize TCP socket on specified host:port
- Listen for incoming connections
- Accept client connections
- Spawn handler threads for each client
- Manage server lifecycle (start/stop)

**Key Methods:**

```python
class SocketServer:
    __init__(host, port)
    start()                    # Start server and listen
    stop()                     # Gracefully shutdown
    accept_connections()       # Accept loop
    broadcast(message, sender) # Broadcast to all clients
```

#### 3.1.2 Connection Handler (`connection_handler.py`)

**Responsibilities:**

- Handle individual client connections
- Receive and send messages
- Maintain connection state
- Handle disconnections gracefully

**Key Methods:**

```python
class ConnectionHandler:
    __init__(client_socket, address, server)
    handle()                   # Main handler loop
    receive_message()          # Receive from client
    send_message(data)         # Send to client
    disconnect()               # Clean disconnect
```

#### 3.1.3 Message Protocol (`message_protocol.py`)

**Responsibilities:**

- Define message format (JSON)
- Parse incoming messages
- Validate message structure
- Route commands to appropriate handlers

**Message Types:**

```json
// CONNECT
{
    "command": "CONNECT",
    "username": "user123",
    "timestamp": "ISO-8601"
}

// MESSAGE
{
    "command": "MESSAGE",
    "to": "all" | "username",
    "message": "text",
    "timestamp": "ISO-8601"
}

// DISCONNECT
{
    "command": "DISCONNECT",
    "username": "user123"
}
```

#### 3.1.4 Database Manager (`database/db_manager.py`)

**Responsibilities:**

- Initialize database schema
- Perform CRUD operations
- Manage transactions
- Handle database connections

**Key Methods:**

```python
class DatabaseManager:
    init_database()
    add_user(username, password_hash)
    save_message(sender_id, message, receiver_id)
    get_message_history(limit)
    create_session(user_id, ip_address)
    close_session(session_id)
```

### 3.2 Client Components

#### 3.2.1 Socket Client (`socket_client.py`)

**Responsibilities:**

- Connect to server
- Send messages to server
- Receive messages from server
- Handle reconnection logic

**Key Methods:**

```python
class SocketClient:
    connect(host, port, username)
    disconnect()
    send_message(message)
    receive_messages()         # Background thread
    auto_reconnect()           # Retry logic
```

#### 3.2.2 GUI Components (`client/gui/`)

**Main Window:** Application container
**Login Window:** User authentication
**Chat Window:** Message display and input

---

## 4. DATA FLOW

### 4.1 Connection Flow

```
Client                    Server                    Database
  |                         |                          |
  |---CONNECT request------>|                          |
  |                         |---Create session-------->|
  |                         |<--Session ID-------------|
  |<--CONNECT response------|                          |
  |                         |                          |
```

### 4.2 Message Flow

```
Client A                  Server                  Client B
  |                         |                        |
  |---MESSAGE-------------->|                        |
  |                         |---Save to DB---------->|
  |                         |---Broadcast----------->|
  |<--ACK-------------------|                        |
  |                         |                        |
```

### 4.3 Disconnection Flow

```
Client                    Server                    Database
  |                         |                          |
  |---DISCONNECT----------->|                          |
  |                         |---Update session-------->|
  |                         |---Notify others--------->|
  |<--Closing connection----|                          |
```

---

## 5. THREADING MODEL

### 5.1 Server Threading

```
Main Thread
├── Socket Accept Loop (blocking)
└── For each connection:
    ├── Spawn Handler Thread
    └── Handler Thread:
        ├── Receive Loop
        ├── Message Processing
        └── Send Responses
```

### 5.2 Client Threading

```
Main Thread (GUI)
├── Event Loop (GUI events)
└── Background Thread:
    ├── Receive Loop
    └── Update GUI via signals
```

---

## 6. ERROR HANDLING

### 6.1 Connection Errors

- **Connection Timeout:** Retry mechanism with exponential backoff
- **Connection Refused:** Notify user, provide retry option
- **Connection Lost:** Auto-reconnect with saved credentials

### 6.2 Message Errors

- **Invalid Format:** Log error, send error response
- **Oversized Message:** Reject with size limit error
- **Encoding Error:** Handle with UTF-8 fallback

### 6.3 Database Errors

- **Connection Error:** Retry with connection pool
- **Constraint Violation:** Return specific error message
- **Deadlock:** Retry transaction with backoff

---

## 7. SECURITY CONSIDERATIONS

### 7.1 Authentication

- Simple username-based (Phase 1)
- Password hashing with bcrypt (Phase 2)
- Token-based auth (Future)

### 7.2 Input Validation

- Sanitize all user inputs
- Validate message length
- Prevent SQL injection (parameterized queries)
- XSS prevention in GUI

### 7.3 Network Security

- Consider SSL/TLS for production
- Rate limiting per client
- IP-based blocking for abuse

---

## 8. SCALABILITY CONSIDERATIONS

### 8.1 Current Limitations

- Single server instance
- Threading-based (limited by GIL)
- SQLite (single file)

### 8.2 Future Improvements

- **Asyncio:** Replace threading with asyncio for better concurrency
- **Load Balancing:** Multiple server instances with load balancer
- **Message Queue:** Redis/RabbitMQ for message buffering
- **Database:** PostgreSQL with connection pooling
- **Distributed:** WebSocket support, microservices architecture

---

## 9. DEPLOYMENT ARCHITECTURE

### 9.1 Development

```
Local Machine
├── Server (localhost:5555)
├── SQLite (chat_server.db)
└── Multiple Client instances
```

### 9.2 Docker Deployment

```
Docker Network
├── Socket Server Container
│   ├── Python 3.10
│   ├── Application code
│   └── Port 5555 exposed
├── Database Container (optional)
│   └── PostgreSQL
└── Client Containers (testing)
```

### 9.3 Production (Future)

```
Cloud Infrastructure
├── Load Balancer
├── Server Cluster (N instances)
├── Database Cluster (Primary + Replicas)
├── Redis Cache
└── Monitoring & Logging
```

---

## 10. MONITORING & LOGGING

### 10.1 Metrics to Track

- Active connections count
- Messages per second
- Connection errors
- Database query performance
- Memory usage per thread

### 10.2 Logging Strategy

```python
# Logging levels
DEBUG:   Detailed debug information
INFO:    Connection events, major operations
WARNING: Recoverable errors
ERROR:   Non-recoverable errors
CRITICAL: System failures
```

---

## 11. TESTING STRATEGY

### 11.1 Unit Tests

- Test individual components in isolation
- Mock external dependencies
- Coverage target: 80%+

### 11.2 Integration Tests

- Test client-server interaction
- Test database operations
- Test message flow end-to-end

### 11.3 Load Tests

- Simulate multiple concurrent clients
- Measure performance under load
- Identify bottlenecks

---

## 12. DEVELOPMENT PHASES

### Phase 1: Foundation (Week 1)

- [ ] Basic socket server (single client)
- [ ] Basic socket client
- [ ] Database schema
- [ ] Simple message protocol

### Phase 2: Core Features (Week 2)

- [ ] Multi-threading support
- [ ] Message broadcasting
- [ ] Database integration
- [ ] GUI client

### Phase 3: Enhancement (Week 3)

- [ ] Error handling
- [ ] Reconnection logic
- [ ] Message history
- [ ] User authentication

### Phase 4: Production Ready (Week 4)

- [ ] Docker deployment
- [ ] Complete testing
- [ ] Documentation
- [ ] Performance optimization

---

## Appendix A: Configuration

```python
# config.py
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5555
MAX_CONNECTIONS = 100
MESSAGE_MAX_SIZE = 4096
DB_NAME = "chat_server.db"
LOG_LEVEL = "INFO"
```

## Appendix B: API Reference

See `docs/API.md` for detailed API documentation.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-17  
**Author:** DevOps Team
