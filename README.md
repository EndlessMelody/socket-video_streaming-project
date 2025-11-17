# Socket Communication System

A Python-based real-time communication system implementing TCP socket programming with client-server architecture. The system supports multiple concurrent client connections, persistent message storage, and a desktop GUI client application.

## Overview

This project demonstrates fundamental network programming concepts including socket communication, multi-threading, database integration, and GUI development. Designed for educational purposes and as a foundation for building scalable chat applications.

## Key Features

- **TCP Socket Server**: Multi-threaded server handling concurrent client connections
- **Desktop Client**: Cross-platform GUI application built with PyQt5/tkinter
- **Real-time Messaging**: Instant message broadcasting to all connected clients
- **Persistent Storage**: SQLite database for message history and user management
- **JSON Protocol**: Structured message format for reliable communication
- **Docker Support**: Containerized deployment for development and production
- **Comprehensive Testing**: Unit and integration tests with pytest

## Technology Stack

**Core Technologies**

- Python 3.10+
- socket (TCP/IP networking)
- threading (concurrent connection handling)
- asyncio (asynchronous I/O operations)

**Supporting Technologies**

- SQLite / PostgreSQL (database)
- PyQt5 / tkinter (GUI framework)
- pytest (testing framework)
- Docker (containerization)
- Git (version control)

## Project Structure

```
socket-video_streaming-project/
├── server/                 # Server-side components
│   ├── socket_server.py   # Main server implementation
│   ├── connection_handler.py
│   ├── message_protocol.py
│   ├── config.py          # Configuration management
│   └── database/          # Database layer
│       ├── db_manager.py
│       └── models.py
├── client/                # Client-side components
│   ├── socket_client.py   # Client implementation
│   ├── gui/               # GUI components
│   └── utils/             # Helper utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   ├── SETUP.md          # Setup guide
│   ├── DIAGRAMS.md       # System diagrams
│   └── API.md            # API reference
├── docker/                # Docker configuration
└── requirements.txt       # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Docker (optional)

### Installation

1. Clone the repository

```bash
git clone https://github.com/EndlessMelody/socket-video_streaming-project.git
cd socket-video_streaming-project
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### Running the Application

**Start the server:**

```bash
python server/socket_server.py
```

**Start a client (in another terminal):**

```bash
python client/socket_client.py
```

### Docker Deployment

```bash
docker-compose -f docker/docker-compose.yml up
```

## Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md) - System design and components
- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [System Diagrams](docs/DIAGRAMS.md) - Network and data flow diagrams
- [API Reference](docs/API.md) - Message protocol and API documentation

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=server --cov=client tests/
```

### Code Quality

```bash
# Format code
black server/ client/

# Lint
pylint server/ client/

# Type checking
mypy server/ client/
```

## Architecture

The system follows a three-tier architecture:

1. **Client Layer**: Desktop GUI application for user interaction
2. **Server Layer**: Multi-threaded TCP server managing connections and message routing
3. **Database Layer**: Persistent storage for users, messages, and sessions

Communication uses JSON-formatted messages over TCP sockets. Each client connection is handled in a separate thread, enabling concurrent operations.

For detailed architecture information, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Message Protocol

Messages are exchanged in JSON format:

```json
{
  "command": "MESSAGE",
  "username": "user123",
  "message": "Hello, World!",
  "timestamp": "2025-11-17T10:00:00"
}
```

Supported commands: CONNECT, MESSAGE, DISCONNECT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Roadmap

**Week 1: Foundation**

- Basic socket server and client
- Database schema implementation
- Initial documentation

**Week 2: Core Features**

- Multi-threading support
- Message broadcasting
- GUI client development

**Week 3: Enhancement**

- Error handling and recovery
- Message history
- User authentication

**Week 4: Production Ready**

- Docker deployment
- Complete testing
- Performance optimization

## License

This project is licensed under the MIT License.

## Team

- Member A: Team Leader & Backend Developer
- Member B: Frontend Developer
- Member C: DevOps & QA Engineer

## Acknowledgments

Built as part of a network programming course to demonstrate practical socket communication concepts.

## Contact

For questions or issues, please open an issue on GitHub.
