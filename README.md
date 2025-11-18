# RTSP/RTP Video Streaming Project

## Project Overview

Implementation of RTSP (Real-Time Streaming Protocol) Client and RTP (Real-time Transport Protocol) packetization for video streaming.

## Assignment Requirements

- **Core (4.0 pts)**: Implement RTSP Client (4 commands) + RTP Packetization
- **HD Streaming (3.0 pts)**: Fragmentation for HD video (720p/1080p)
- **Client Caching (2.5 pts)**: Pre-buffering to reduce jitter
- **Report (0.5 pts)**: Technical documentation

## Team Members

- **Member A**: RTP Developer & Team Leader
- **Member B**: RTSP Client Developer
- **Member C**: QA & Documentation Engineer

## Project Timeline

- **Week 1 (18/11-24/11)**: Core RTSP/RTP Implementation
- **Week 2 (25/11-01/12)**: HD Streaming & Fragmentation
- **Week 3 (02/12-08/12)**: Client-Side Caching
- **Week 4 (09/12-17/12)**: Report & Finalization

## Repository Structure

```
├── src/                    # Source code
│   ├── Server.py          # RTSP Server (PROVIDED)
│   ├── ServerWorker.py    # Request handler (PROVIDED)
│   ├── Client.py          # RTSP Client (TO IMPLEMENT)
│   ├── ClientLauncher.py  # GUI (PROVIDED)
│   ├── RtpPacket.py       # RTP handler (TO IMPLEMENT)
│   └── VideoStream.py     # Video reader (PROVIDED)
│
├── media/                 # Video files
├── docs/                  # Documentation
├── tests/                 # Test suite
└── report/                # Final deliverables
```

## Getting Started

See [docs/README.md](docs/README.md) for setup instructions.

## Status

🚧 Project setup complete - Ready to implement Week 1 tasks
