# Socket Communication System - Architecture Document

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục tiêu
- Xây dựng hệ thống socket communication với client-server architecture
- Hỗ trợ multiple concurrent connections
- Persistent storage với database
- Real-time message broadcasting

### 1.2 Tech Stack
- **Backend:** Python 3.10+, socket, threading/asyncio
- **Database:** SQLite (development), PostgreSQL (production optional)
- **Frontend:** PyQt5/tkinter
- **Testing:** pytest
- **Deployment:** Docker

---

## 2. KIẾN TRÚC TỔNG QUAN

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Client 1   │  │   Client 2   │  │   Client N   │      │
│  │   (GUI App)  │  │   (GUI App)  │  │   (GUI App)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘              │
│                            │                                  │
└────────────────────────────┼──────────────────────────────────┘
                             │ TCP Socket Connection
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                     SERVER LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Socket Server (Main Thread)                  │ │
│  │         - Accept connections                           │ │
│  │         - Spawn handler threads                        │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │         Connection Handler (Multi-threaded)            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │ Thread 1 │  │ Thread 2 │  │ Thread N │            │ │
│  │  │ Client 1 │  │ Client 2 │  │ Client N │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │            Message Protocol Handler                     │ │
│  │  - Parse JSON messages                                 │ │
│  │  - Route commands (CONNECT, MESSAGE, DISCONNECT)      │ │
│  │  - Validate message format                            │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
└───────────────────┼──────────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────────┐
│                  DATABASE LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Database Manager                           │ │
│  │  - Connection pooling                                  │ │
│  │  - CRUD operations                                     │ │
│  │  - Transaction management                              │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │              SQLite Database                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Users   │  │ Messages │  │ Sessions │            │ │
│  │  │  Table   │  │  Table   │  │  Table   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
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
