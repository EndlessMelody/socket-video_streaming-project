# Network & System Diagrams

## 1. Network Communication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT SIDE                               │
└──────────────────────────────────────────────────────────────────┘

Client Application (127.0.0.1:random_port)
    │
    │ 1. TCP Socket Connection Request
    ▼
┌────────────────────────────────────────────┐
│        Network Layer (TCP/IP)              │
│        Protocol: TCP                       │
│        Port: 5555                          │
└────────────────────────────────────────────┘
    │
    │ 2. Connection Established (3-way handshake)
    ▼
┌──────────────────────────────────────────────────────────────────┐
│                         SERVER SIDE                               │
└──────────────────────────────────────────────────────────────────┘

Socket Server (127.0.0.1:5555)
    │
    │ 3. Accept Connection
    ├── Create new thread for client
    │
    ▼
Connection Handler Thread
    │
    │ 4. Receive Message (JSON)
    ▼
Message Protocol Parser
    │
    ├── CONNECT → Authenticate
    ├── MESSAGE → Process & Broadcast
    └── DISCONNECT → Cleanup
    │
    │ 5. Database Operations
    ▼
Database Manager → SQLite
```

## 2. Multi-Client Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Client 1   │     │  Client 2   │     │  Client N   │
│  (Thread)   │     │  (Thread)   │     │  (Thread)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │
       │  TCP :5555        │  TCP :5555        │  TCP :5555
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Socket Server        │
              │   Main Accept Loop     │
              └────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   Handler    │ │   Handler    │ │   Handler    │
    │   Thread 1   │ │   Thread 2   │ │   Thread N   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │    Database    │
                   │    Manager     │
                   └────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │   SQLite DB    │
                   └────────────────┘
```

## 3. Message Broadcasting Flow

```
Client A sends message:
───────────────────────

Client A                Server               Client B               Client C
   │                      │                      │                      │
   │──MESSAGE──────────>  │                      │                      │
   │  {                   │                      │                      │
   │   "command": "MSG"   │                      │                      │
   │   "text": "Hello"    │                      │                      │
   │  }                   │                      │                      │
   │                      │                      │                      │
   │                      │ ──Save to DB──────>  │                      │
   │                      │                      │                      │
   │                      │ ──Broadcast────────> │                      │
   │                      │                      │                      │
   │                      │ ──Broadcast──────────────────────────────>  │
   │                      │                      │                      │
   │ <─ACK────────────────│                      │                      │
   │                      │                      │                      │
   │                      │                      │──Display─────>       │
   │                      │                      │                      │
   │                      │                      │                      │──Display───>
```

## 4. Connection State Machine

```
[DISCONNECTED]
      │
      │ connect()
      ▼
[CONNECTING]
      │
      │ TCP handshake success
      ▼
[AUTHENTICATING]
      │
      │ CONNECT command success
      ▼
[CONNECTED]
      │
      ├── Send MESSAGE ──> [CONNECTED]
      │
      ├── Receive MESSAGE ──> [CONNECTED]
      │
      ├── Timeout/Error ──> [RECONNECTING]
      │                         │
      │                         │ retry
      │                         └──> [CONNECTING]
      │
      │ disconnect() / DISCONNECT command
      ▼
[DISCONNECTING]
      │
      │ cleanup complete
      ▼
[DISCONNECTED]
```

## 5. Database Schema Diagram

```
┌─────────────────────────────────────┐
│             USERS                    │
├─────────────────────────────────────┤
│ id (PK)          INTEGER             │
│ username         TEXT UNIQUE         │
│ password_hash    TEXT                │
│ created_at       TIMESTAMP           │
│ last_login       TIMESTAMP           │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│            MESSAGES                  │
├─────────────────────────────────────┤
│ id (PK)          INTEGER             │
│ sender_id (FK)   INTEGER ───────┐   │
│ receiver_id (FK) INTEGER        │   │
│ message          TEXT            │   │
│ timestamp        TIMESTAMP       │   │
│ is_read          BOOLEAN         │   │
└─────────────────────────────────┴───┘
                  │ N
                  │
                  │ 1
┌─────────────────▼───────────────────┐
│            SESSIONS                  │
├─────────────────────────────────────┤
│ id (PK)          INTEGER             │
│ user_id (FK)     INTEGER             │
│ ip_address       TEXT                │
│ connect_time     TIMESTAMP           │
│ disconnect_time  TIMESTAMP           │
└─────────────────────────────────────┘
```

## 6. Deployment Architecture

### Development Environment
```
┌────────────────────────────────────────────┐
│         Local Machine                      │
│  ┌──────────────────────────────────────┐ │
│  │  Terminal 1: Server                  │ │
│  │  python server/socket_server.py      │ │
│  │  Listening on 127.0.0.1:5555        │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Terminal 2: Client 1                │ │
│  │  python client/socket_client.py      │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Terminal 3: Client 2                │ │
│  │  python client/socket_client.py      │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Database: chat_server.db            │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### Docker Environment
```
┌────────────────────────────────────────────┐
│         Docker Network                     │
│  ┌──────────────────────────────────────┐ │
│  │  Container: socket-server            │ │
│  │  Image: python:3.10-slim            │ │
│  │  Port: 5555:5555                    │ │
│  │  Volume: ./:/app                    │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Container: postgres (optional)      │ │
│  │  Image: postgres:14                 │ │
│  │  Port: 5432:5432                    │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

## 7. Security Layers

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  - Input validation                     │
│  - Authentication                       │
│  - Authorization                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Protocol Layer                  │
│  - Message format validation            │
│  - JSON schema validation               │
│  - Command whitelisting                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Transport Layer                 │
│  - TCP/IP                              │
│  - (Future: SSL/TLS encryption)        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database Layer                  │
│  - Parameterized queries                │
│  - SQL injection prevention             │
│  - Transaction isolation                │
└─────────────────────────────────────────┘
```

## 8. Error Handling Flow

```
Client Request
      │
      ▼
Try: Parse Message
      │
      ├─ Success ──> Process Command
      │                     │
      │                     ├─ Success ──> Send Response
      │                     │
      │                     └─ Error ──> Log & Send Error Response
      │
      └─ Error (Invalid JSON)
             │
             ├─> Log Error
             ├─> Send Error Response
             └─> Maintain Connection
```

---

**Legend:**
- `│ ▼ ─>` : Data flow direction
- `[STATE]` : System state
- `(PK)` : Primary Key
- `(FK)` : Foreign Key
- `───>` : One-way communication
- `<──>` : Two-way communication
