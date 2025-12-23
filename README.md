# Socket Programming - RTSP/RTP Video Streaming

A complete implementation of a Video Streaming application using the **Client-Server** model. This project implements **RTSP** (Real Time Streaming Protocol) for session control and **RTP** (Real-time Transport Protocol) over UDP for media data transmission. The system supports HD video streaming (360p, 720p, 1080p) with advanced features including client-side buffering, packet loss detection, network statistics, and adaptive frame management.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Usage Guide](#usage-guide)
- [Architecture & Implementation](#architecture--implementation)
- [Protocol Details](#protocol-details)
- [Advanced Features](#advanced-features)
- [Video File Format](#video-file-format)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Performance Metrics](#performance-metrics)

---

## Overview

This project implements a complete video streaming system that:

- **Establishes RTSP sessions** for control and negotiation between client and server
- **Streams video over RTP/UDP** with proper packetization and fragmentation
- **Supports HD resolutions** (360p, 720p, 1080p) with efficient frame handling
- **Implements client-side buffering** to reduce jitter and improve playback quality
- **Tracks network statistics** including FPS, data rate, packet loss, and buffer status
- **Handles frame fragmentation** for frames exceeding MTU (Maximum Transmission Unit)

The implementation follows RFC 2326 (RTSP) and RFC 3550 (RTP) specifications and includes optimizations for smooth HD video playback.

---

## Features

### ✅ Core Features (Grading Requirements)

1. **RTSP Protocol Implementation**

   - SETUP: Establishes session and transport parameters
   - PLAY: Initiates video streaming
   - PAUSE: Temporarily halts playback
   - TEARDOWN: Terminates session gracefully

2. **RTP Packetization**

   - Complete RTP header construction (12 bytes)
   - Proper sequence numbering
   - Timestamp generation using 90kHz clock approximation
   - SSRC (Synchronization Source) identification
   - Marker bit support for fragmented frames

3. **HD Video Streaming**

   - Frame fragmentation for large frames (>1400 bytes MTU)
   - Frame reassembly on client side
   - Support for 360p, 720p, and 1080p resolutions
   - Adaptive timing for smooth playback

4. **Client-Side Caching**
   - Pre-buffering of 60 frames before playback
   - Frame buffer queue management
   - Adaptive frame skipping to prevent buffer overflow
   - Buffer status monitoring

### 📊 Advanced Features

- **Real-time Statistics Display**

  - FPS (Frames Per Second) calculation
  - Data rate (kbps) monitoring
  - Packet loss rate tracking
  - Buffer size visualization
  - Frame count (received vs displayed)

- **Network Analysis**

  - Packet loss detection and reporting
  - Duplicate packet detection
  - Out-of-order packet handling
  - Average packet size calculation

- **Performance Optimizations**
  - Adaptive buffer management
  - Frame skipping for buffer overflow prevention
  - Efficient frame reassembly
  - Optimized UDP socket buffer sizes (5MB)

---

## Project Structure

```
socket-video_streaming-project/
│
├── src/                          # Source code directory
│   ├── Server.py                # Server entry point (listens on RTSP port)
│   ├── ServerWorker.py          # Handles client connections and RTP streaming
│   ├── Client.py                # Client GUI and RTSP/RTP implementation
│   ├── ClientLauncher.py        # Client application entry point
│   ├── RtpPacket.py             # RTP packet encoding/decoding class
│   └── VideoStream.py           # MJPEG file reader and frame extractor
│
├── video_stream/                 # Video files directory
│   ├── 360.mjpeg                # 360p test video
│   ├── 720.mjpeg                # 720p HD test video
│   └── 1080.mjpeg               # 1080p Full HD test video
│
└── docs/                         # Documentation
    ├── Socket_2526.txt          # Assignment requirements
    └── meeting_minutes.md       # Project meeting notes
```

### File Descriptions

#### Server Components

- **`Server.py`**: Main server application that creates a TCP socket listening on the specified port for RTSP connections. Spawns a `ServerWorker` thread for each client.

- **`ServerWorker.py`**:
  - Processes RTSP requests (SETUP, PLAY, PAUSE, TEARDOWN)
  - Manages RTSP state machine (INIT → READY → PLAYING)
  - Reads frames from `VideoStream` and packetizes them into RTP packets
  - Handles frame fragmentation for HD video
  - Sends RTP packets over UDP to client

#### Client Components

- **`Client.py`**:

  - Implements RTSP client protocol
  - Manages client state machine
  - Receives and reassembles RTP packets
  - Implements frame buffering and playback
  - Provides GUI with control buttons and statistics display

- **`ClientLauncher.py`**: Entry point that parses command-line arguments and launches the client GUI.

#### Supporting Classes

- **`RtpPacket.py`**: Handles RTP packet encoding (server) and decoding (client). Constructs/parses 12-byte RTP header with proper bit manipulation.

- **`VideoStream.py`**: Reads MJPEG video files, extracting individual JPEG frames either from proprietary format (5-byte header) or standard MJPEG format (FF D8 to FF D9 markers).

---

## Prerequisites

### Required Software

- **Python 3.6+** (Python 3.7 or higher recommended)
- **pip** (Python package installer)

### Required Python Libraries

- **tkinter**: Usually included with Python installation (GUI framework)
- **Pillow (PIL)**: For image processing and display

### System Requirements

- **Operating System**: Windows, Linux, or macOS
- **Network**: For same-machine testing, localhost is sufficient. For network testing, ensure firewall allows TCP (RTSP) and UDP (RTP) traffic.
- **Ports**:
  - RTSP server port (default: 8554, must be > 1024)
  - RTP client port (any free port, e.g., 5008)

---

## Installation

### Step 1: Verify Python Installation

Open a terminal/command prompt and check Python version:

```bash
python --version
# Should show: Python 3.x.x
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/).

### Step 2: Install Required Packages

Install Pillow using pip:

```bash
pip install Pillow
```

Or on Linux/Mac, you may need:

```bash
pip3 install Pillow
```

### Step 3: Verify Installation

Test that tkinter is available:

```bash
python -m tkinter
```

A small window should appear. Close it to confirm tkinter works.

### Step 4: Clone/Navigate to Project

Navigate to the project directory:

```powershell
# Windows PowerShell
cd "C:\Users\phanp\OneDrive\Tài liệu\GitHub\socket-video_streaming-project"

# Or on Linux/Mac
cd ~/path/to/socket-video_streaming-project
```

---

## How to Run

### Step 1: Start the Server

**Open a terminal/command prompt** and navigate to the `src` directory:

```powershell
cd src
```

Start the server on port **8554** (or any port number > 1024):

```powershell
python Server.py 8554
```

**Expected Output:**

```
[Server started - no output initially, waiting for connections]
```

**Important Notes:**

- The server will run continuously until you stop it (Ctrl+C)
- Keep this terminal window open
- The server listens on **TCP port 8554** for RTSP connections
- You can use any port number > 1024 (e.g., 8554, 8555, 9000)

### Step 2: Start the Client

**Open a NEW terminal/command prompt** (keep server running):

```powershell
cd src
```

Launch the client with one of the available video files:

#### Option 1: 360p Video (Recommended for Testing)

```powershell
python ClientLauncher.py localhost 8554 5008 ../video_stream/360.mjpeg
```

#### Option 2: 720p HD Video

```powershell
python ClientLauncher.py ClientLauncher.py localhost 8554 5008 ../video_stream/720.mjpeg
```

#### Option 3: 1080p Full HD Video

```powershell
python ClientLauncher.py localhost 8554 5008 ../video_stream/1080.mjpeg
```

### Command-Line Arguments Explained

```
python ClientLauncher.py <server_addr> <server_port> <rtp_port> <video_file>
```

- **`server_addr`**:

  - `localhost` or `127.0.0.1` - if server is on same machine
  - Server's IP address - if server is on different machine

- **`server_port`**:

  - RTSP server port (must match server port, e.g., `8554`)

- **`rtp_port`**:

  - UDP port for receiving RTP packets (any free port, e.g., `5008`)
  - Can be different for multiple clients

- **`video_file`**:
  - Relative path to video file from `src` directory
  - Example: `../video_stream/720.mjpeg`

### Expected Client Output

A GUI window will appear with:

- Video display area (black initially)
- Four buttons: Setup, Play, Pause, Teardown
- Statistics bar at the bottom (initially empty)

---

## Usage Guide

### Client GUI Overview

The client window contains:

1. **Video Display Area**: Shows the streaming video frames
2. **Control Buttons**:
   - **Setup**: Establish RTSP connection
   - **Play**: Start video playback
   - **Pause**: Pause playback
   - **Teardown**: Stop and exit
3. **Statistics Bar**: Real-time streaming metrics

### Step-by-Step Usage

#### 1. Establish Connection (SETUP)

1. Click the **Setup** button
2. Client sends RTSP SETUP request to server
3. Server responds with session ID
4. Client opens UDP socket for RTP reception
5. Status: Client state changes from `INIT` to `READY`

**What happens:**

- RTSP session is established
- Transport parameters are negotiated
- RTP port is opened on client side

#### 2. Start Playback (PLAY)

1. Click the **Play** button
2. Client sends RTSP PLAY request
3. Server begins sending RTP packets
4. Client starts buffering frames

**Buffering Process:**

- Client receives and buffers frames
- Statistics bar shows: `Buffering: X/60 frames (XX.X%)...`
- Once 60 frames are buffered, playback automatically starts
- Statistics bar updates to show real-time metrics

**Expected Console Output:**

```
Buffering: 15/60 frames (25.0%)...
Buffering: 30/60 frames (50.0%)...
Buffering: 45/60 frames (75.0%)...
Buffering Complete. 60 frames loaded. Starting Playback.
```

#### 3. Monitor Playback

During playback, the statistics bar displays:

```
FPS: 29.85 | Data Rate: 1523.45 kbps | Loss Rate: 0.00% | Buffer: 62 frames |
Frames Rcvd: 450 | Frames Disp: 420 | Packets: 523
```

**Metrics Explained:**

- **FPS**: Frames per second (actual playback rate)
- **Data Rate**: Network throughput in kilobits per second
- **Loss Rate**: Percentage of lost packets
- **Buffer**: Current frames in buffer queue
- **Frames Rcvd**: Total frames received from server
- **Frames Disp**: Total frames displayed to user
- **Packets**: Total RTP packets received

#### 4. Pause Playback (PAUSE)

1. Click **Pause** button
2. Server stops sending new frames
3. Client state returns to `READY`
4. Can resume by clicking **Play** again

#### 5. Stop and Exit (TEARDOWN)

1. Click **Teardown** button
2. Client sends TEARDOWN request
3. Server stops streaming and closes connection
4. Client closes sockets and exits

### Running Multiple Clients

You can run multiple clients simultaneously:

1. Keep server running
2. Start multiple client instances in separate terminals
3. Use **different RTP ports** for each client:

   ```powershell
   # Client 1
   python ClientLauncher.py localhost 8554 5008 ../video_stream/360.mjpeg

   # Client 2 (different RTP port)
   python ClientLauncher.py localhost 8554 5009 ../video_stream/720.mjpeg
   ```

---

## Architecture & Implementation

### Client-Server Model

```
┌─────────────┐                    ┌─────────────┐
│   Client    │                    │   Server    │
│             │                    │             │
│  GUI + RTSP │◄───RTSP/TCP───────►│ RTSP Handler│
│   Control   │                    │             │
│             │                    │             │
│  RTP Socket │◄───RTP/UDP────────►│ RTP Stream  │
│  (Receive)  │                    │   (Send)    │
└─────────────┘                    └─────────────┘
```

### RTSP Control Flow

```
Client                          Server
  │                                │
  │───SETUP (filename, port)──────►│
  │◄──200 OK (Session ID)──────────│
  │                                │
  │───PLAY (Session ID)───────────►│
  │◄──200 OK───────────────────────│
  │                                │
  │◄──────RTP Packets──────────────│
  │                                │
  │───PAUSE (Session ID)──────────►│
  │◄──200 OK───────────────────────│
  │                                │
  │───TEARDOWN (Session ID)───────►│
  │◄──200 OK───────────────────────│
```

### RTP Packet Flow

1. **Server Side:**

   - Reads frame from `VideoStream`
   - If frame > 1400 bytes: fragments into multiple packets
   - Creates RTP packet header (12 bytes)
   - Sets sequence number, timestamp, marker bit
   - Sends each packet over UDP

2. **Client Side:**
   - Receives RTP packets on UDP socket
   - Decodes RTP header
   - Reassembles fragmented frames using marker bit
   - Adds complete frames to buffer queue
   - Displays frames from buffer at regular intervals

### State Machines

#### Server State Machine

```
INIT ──[SETUP]──► READY ──[PLAY]──► PLAYING ──[PAUSE]──► READY
                          │                              │
                          └──────[TEARDOWN]──────────────┘
```

#### Client State Machine

```
INIT ──[SETUP OK]──► READY ──[PLAY OK]──► PLAYING ──[PAUSE OK]──► READY
                                    │                              │
                                    └──────[TEARDOWN OK]───────────┘
```

---

## Protocol Details

### RTSP (Real-Time Streaming Protocol)

RTSP runs over **TCP** (port 554 by default, we use custom ports > 1024).

#### RTSP Request Format

```
SETUP movie.mjpeg RTSP/1.0
CSeq: 1
Transport: RTP/AVP;unicast;client_port=5008
```

#### RTSP Response Format

```
RTSP/1.0 200 OK
CSeq: 1
Session: 123456
```

#### RTSP Messages Implemented

| Method   | Purpose           | Headers Required |
| -------- | ----------------- | ---------------- |
| SETUP    | Establish session | CSeq, Transport  |
| PLAY     | Start streaming   | CSeq, Session    |
| PAUSE    | Pause streaming   | CSeq, Session    |
| TEARDOWN | End session       | CSeq, Session    |

### RTP (Real-time Transport Protocol)

RTP runs over **UDP** for low-latency media delivery.

#### RTP Packet Structure

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|V=2|P|X|  CC   |M|     PT      |       sequence number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           timestamp                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           synchronization source (SSRC) identifier            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            Payload                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### RTP Header Fields

- **V (Version)**: Always 2
- **P (Padding)**: 0 (no padding)
- **X (Extension)**: 0 (no extension header)
- **CC (CSRC Count)**: 0 (no contributing sources)
- **M (Marker)**: 1 for last packet of frame, 0 otherwise
- **PT (Payload Type)**: 26 for MJPEG
- **Sequence Number**: Incremented for each packet
- **Timestamp**: 90kHz clock (approximated using milliseconds \* 90)
- **SSRC**: Unique identifier for this source
- **Payload**: Video frame data (JPEG image)

---

## Advanced Features

### 1. Frame Fragmentation

**Problem**: HD video frames can exceed UDP MTU (typically 1500 bytes, payload ~1400 bytes).

**Solution**:

- Server checks frame size before sending
- If frame > 1400 bytes, splits into multiple RTP packets
- Each fragment gets unique sequence number
- Last fragment has marker bit = 1
- Client reassembles fragments using marker bit

**Example:**

```
Frame (3000 bytes) → [Packet 1: 1400 bytes, M=0]
                  → [Packet 2: 1400 bytes, M=0]
                  → [Packet 3: 200 bytes, M=1]
```

### 2. Client-Side Buffering

**Purpose**: Reduce jitter and improve playback smoothness.

**Implementation:**

- Pre-buffer 60 frames before starting playback
- Use `queue.Queue()` for thread-safe frame storage
- Consumer thread displays frames at 30 FPS (33ms intervals)
- Producer thread (RTP receiver) fills buffer continuously

**Buffer Management:**

- **Underflow**: If buffer empty, pause playback and rebuffer
- **Overflow**: If buffer > 500 frames, skip frames to prevent memory issues

### 3. Packet Loss Detection

**Method:**

- Track expected sequence numbers
- Compare received sequence number with expected
- Calculate gap = received_seq - expected_seq
- Report loss events in console and statistics

**Example:**

```
Expected: 100
Received: 103
Loss: 3 packets (101, 102 lost)
```

### 4. FPS Calculation

**Method:**

- Track frames displayed and start time
- Calculate: FPS = frames_displayed / elapsed_time
- Update continuously during playback
- Display in statistics bar

### 5. Network Statistics

**Metrics Tracked:**

- **Data Rate**: (total_bytes \* 8) / elapsed_time / 1000 (kbps)
- **Packet Loss Rate**: (lost_packets / total_packets) \* 100
- **Buffer Size**: Current frames in queue
- **Average Packet Size**: total_bytes / total_packets

---

## Video File Format

The project supports two MJPEG formats:

### Format 1: Proprietary Format (Original)

- Each frame preceded by 5-byte header
- Header contains frame size as integer
- Format: `[5-byte size][frame data][5-byte size][frame data]...`

### Format 2: Standard MJPEG Format

- Standard JPEG markers:
  - Start: `0xFF 0xD8`
  - End: `0xFF 0xD9`
- `VideoStream.py` automatically detects format
- Scans for marker sequences to extract frames

### Video File Locations

Test videos are located in `video_stream/`:

- `360.mjpeg` - Lower resolution (recommended for testing)
- `720.mjpeg` - HD quality
- `1080.mjpeg` - Full HD quality

**Note**: For HD videos, ensure frames don't exceed reasonable memory limits. The implementation handles large frames through fragmentation.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Connection Failed" Error

**Symptoms**: Client cannot connect to server

**Solutions**:

- Verify server is running: Check server terminal window
- Check server port matches: Both must use same port (e.g., 8554)
- Verify server address: Use `localhost` for same machine, IP address for remote
- Check firewall: Allow TCP connections on RTSP port

#### 2. "Unable to Bind" Error

**Symptoms**: `Unable to bind PORT=5008`

**Solutions**:

- Port already in use: Try different RTP port (e.g., 5009, 5010)
- Another client using same port: Use unique ports for each client
- Permission issue: Use port > 1024 (already enforced)

#### 3. "File Not Found" Error

**Symptoms**: `404 NOT FOUND` or file error

**Solutions**:

- Verify file path: Check relative path from `src` directory
- Check file exists: `ls video_stream/` or `dir video_stream`
- Verify file name: Case-sensitive on Linux/Mac
- Check working directory: Must run from `src` directory

#### 4. Video Not Playing / Black Screen

**Symptoms**: Buffer shows frames but video doesn't appear

**Solutions**:

- Wait for buffering: Ensure "Buffering Complete" message appears
- Check statistics: Verify FPS > 0 and frames being received
- Check console: Look for error messages
- Try lower resolution: Start with `360.mjpeg`

#### 5. High Packet Loss

**Symptoms**: Loss rate > 5% in statistics

**Solutions**:

- Network congestion: Reduce resolution or check network
- UDP buffer full: Increase socket buffer size (already set to 5MB)
- Too fast transmission: Server sends at ~40 FPS, may need adjustment
- Firewall interference: Check UDP port blocking

#### 6. Low FPS / Stuttering

**Symptoms**: FPS < 20, video stutters

**Solutions**:

- Check buffer size: Should be > 30 frames during playback
- CPU overload: Close other applications
- Network issues: Check data rate in statistics
- Try lower resolution: Use 360p instead of 1080p

#### 7. Buffer Empty / Playback Stops

**Symptoms**: "Buffer Empty. Buffering..." message repeatedly

**Solutions**:

- Network too slow: Check data rate (should be > 500 kbps for 360p)
- Packet loss: High loss rate causes buffer depletion
- Server issues: Verify server is still running and sending packets
- Increase buffer threshold: Modify `BUFFER_THRESHOLD` in `Client.py`

#### 8. Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError`

**Solutions**:

- Install Pillow: `pip install Pillow`
- Check Python version: `python --version` (need 3.6+)
- Verify tkinter: `python -m tkinter` (should open window)
- Check PYTHONPATH: Run from `src` directory

#### 9. Server Not Accepting Connections

**Symptoms**: Server starts but client can't connect

**Solutions**:

- Check port binding: Server should show no errors on start
- Verify port availability: `netstat -an | findstr 8554` (Windows) or `netstat -an | grep 8554` (Linux/Mac)
- Try different port: Use 8555, 9000, etc.
- Check firewall: Allow incoming TCP connections

#### 10. Multiple Clients Not Working

**Symptoms**: Second client fails to connect or interferes with first

**Solutions**:

- Use different RTP ports: Each client needs unique UDP port
- Server supports multiple clients: Each gets separate `ServerWorker` thread
- Example:
  ```powershell
  # Client 1
  python ClientLauncher.py localhost 8554 5008 ../video_stream/360.mjpeg
  # Client 2 (different RTP port)
  python ClientLauncher.py localhost 8554 5009 ../video_stream/360.mjpeg
  ```

---

## Testing

### Test Scenarios

#### 1. Basic Functionality Test

1. Start server on port 8554
2. Start client with 360p video
3. Click Setup → Play
4. Verify video plays smoothly
5. Click Pause → Play (resume)
6. Click Teardown

**Expected**: All operations work without errors.

#### 2. HD Video Test

1. Start server
2. Start client with 1080p video
3. Monitor statistics for:
   - Fragmented frames (packets > 1 per frame)
   - Buffer stability
   - Data rate (should be higher than 360p)
   - FPS consistency

**Expected**: Smooth playback with higher data rate.

#### 3. Network Resilience Test

1. Start streaming
2. Monitor packet loss (artificially simulate if needed)
3. Verify frame reassembly works correctly
4. Check that playback continues despite occasional losses

**Expected**: System handles packet loss gracefully.

#### 4. Multiple Clients Test

1. Start server
2. Launch 2-3 clients simultaneously
3. Each with different video files or resolutions
4. Verify all streams work independently

**Expected**: Server handles multiple concurrent streams.

#### 5. Buffer Management Test

1. Start streaming
2. Monitor buffer size in statistics
3. Verify pre-buffering works (60 frames before play)
4. Check frame skipping if buffer > 500

**Expected**: Buffer maintains stable size during playback.

---

## Performance Metrics

### Expected Performance

#### 360p Video

- **Data Rate**: ~500-1000 kbps
- **FPS**: ~25-30 FPS
- **Packet Loss**: < 1% (local network)
- **Buffer Size**: 60-80 frames (stable)

#### 720p HD Video

- **Data Rate**: ~2000-4000 kbps
- **FPS**: ~25-30 FPS
- **Packet Loss**: < 2% (local network)
- **Buffer Size**: 60-100 frames (may vary more)
- **Fragmentation**: Most frames fragmented (2-5 packets per frame)

#### 1080p Full HD Video

- **Data Rate**: ~4000-8000 kbps
- **FPS**: ~25-30 FPS
- **Packet Loss**: < 3% (local network)
- **Buffer Size**: 60-120 frames (higher variance)
- **Fragmentation**: All large frames fragmented (3-10 packets per frame)

### Optimizing Performance

1. **Reduce Resolution**: Use 360p for testing, 720p for presentation
2. **Increase Buffer**: Raise `BUFFER_THRESHOLD` if network is unstable
3. **Adjust Frame Rate**: Modify server wait time (currently 25ms = ~40 FPS)
4. **Network Optimization**: Use wired connection for better stability

---

## Code Modifications

### Changing Buffer Threshold

In `src/Client.py`, line ~66:

```python
self.BUFFER_THRESHOLD = 60  # Change to desired value (e.g., 80, 100)
```

### Adjusting Server Frame Rate

In `src/ServerWorker.py`, line ~154:

```python
self.clientInfo['event'].wait(0.025)  # 25ms = 40 FPS
# Change to 0.033 for 30 FPS, 0.040 for 25 FPS
```

### Modifying MTU Size

In `src/ServerWorker.py`, line ~26:

```python
MAX_PAYLOAD_SIZE = 1400  # Adjust based on network MTU
```

---

## Grading Criteria

This implementation addresses all grading requirements:

| Requirement                 | Points | Status                  |
| --------------------------- | ------ | ----------------------- |
| RTSP protocol in client     | 4.0    | ✅ Complete             |
| RTP packetization in server |        | ✅ Complete             |
| HD Video Streaming          | 3.0    | ✅ Complete             |
| - Fragmentation for MTU     |        | ✅ Implemented          |
| - Smooth HD playback        |        | ✅ With buffering       |
| - Frame loss analysis       |        | ✅ Statistics tracking  |
| - Network usage analysis    |        | ✅ Real-time metrics    |
| Client-Side Caching         | 2.5    | ✅ Complete             |
| - Frame buffer              |        | ✅ Queue implementation |
| - Pre-buffer N frames       |        | ✅ 60 frames            |
| Report                      | 0.5    | 📝 Documentation        |

**Total: 10.0 points**

---

## Contributors

- [Student Name 1]
- [Student Name 2]
- [Student Name 3]

---

## References

- **RFC 2326**: Real Time Streaming Protocol (RTSP)
- **RFC 3550**: RTP: A Transport Protocol for Real-Time Applications
- **RFC 1889**: RTP Profile for Audio and Video Conferences with Minimal Control

---

## License

This project is part of a Socket Programming course assignment.

---

## Additional Notes

- The server runs in a single process but handles multiple clients via threading
- UDP packet ordering is not guaranteed; sequence numbers help detect lost packets
- The implementation prioritizes smooth playback over real-time latency
- For production use, consider implementing RTCP for quality feedback
- The current implementation uses fixed frame timing; adaptive bitrate streaming would require additional development

---

**Last Updated**: 2024

**Version**: 1.0
