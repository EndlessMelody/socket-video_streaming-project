# Video Streaming Protocol Specification

## 1. OVERVIEW

This document defines the communication protocol for video streaming over TCP sockets between broadcaster, server, and viewers.

## 2. PROTOCOL LAYERS

### 2.1 Protocol Stack

```
┌─────────────────────────────────┐
│   Application Layer             │
│   (Video Control Messages)      │
├─────────────────────────────────┤
│   Frame Layer                   │
│   (Frame Headers + Payload)     │
├─────────────────────────────────┤
│   Transport Layer               │
│   (TCP Socket)                  │
└─────────────────────────────────┘
```

---

## 3. MESSAGE TYPES

### 3.1 Control Messages (JSON Format)

#### 3.1.1 Session Initialization

**Broadcaster → Server: START_STREAM**

```json
{
  "type": "START_STREAM",
  "broadcaster_id": "user_123",
  "session_name": "My Stream",
  "video_config": {
    "codec": "h264",
    "width": 640,
    "height": 480,
    "fps": 30,
    "quality": "medium"
  },
  "timestamp": 1700000000
}
```

**Server → Broadcaster: STREAM_ACK**

```json
{
  "type": "STREAM_ACK",
  "status": "success",
  "session_id": "sess_abc123",
  "server_buffer_size": 60,
  "max_frame_size": 1048576
}
```

#### 3.1.2 Viewer Connection

**Viewer → Server: JOIN_STREAM**

```json
{
  "type": "JOIN_STREAM",
  "viewer_id": "viewer_456",
  "session_id": "sess_abc123",
  "preferred_quality": "high",
  "buffer_size": 30
}
```

**Server → Viewer: JOIN_ACK**

```json
{
  "type": "JOIN_ACK",
  "status": "success",
  "video_config": {
    "codec": "h264",
    "width": 1280,
    "height": 720,
    "fps": 30
  },
  "current_frame_seq": 1234
}
```

#### 3.1.3 Quality Change Request

**Viewer → Server: CHANGE_QUALITY**

```json
{
  "type": "CHANGE_QUALITY",
  "viewer_id": "viewer_456",
  "requested_quality": "low",
  "reason": "bandwidth_low"
}
```

**Server → Viewer: QUALITY_CHANGED**

```json
{
  "type": "QUALITY_CHANGED",
  "new_quality": "low",
  "new_config": {
    "width": 320,
    "height": 240,
    "fps": 15
  }
}
```

#### 3.1.4 Stream Termination

**Broadcaster → Server: STOP_STREAM**

```json
{
  "type": "STOP_STREAM",
  "session_id": "sess_abc123",
  "reason": "user_stopped"
}
```

**Server → All Viewers: STREAM_ENDED**

```json
{
  "type": "STREAM_ENDED",
  "session_id": "sess_abc123",
  "reason": "broadcaster_disconnected"
}
```

#### 3.1.5 Heartbeat

**Bidirectional: PING/PONG**

```json
{
  "type": "PING",
  "timestamp": 1700000000
}
```

```json
{
  "type": "PONG",
  "timestamp": 1700000000
}
```

---

## 4. FRAME PACKET STRUCTURE

### 4.1 Frame Header (Fixed 32 bytes)

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Magic     │   Version   │  Frame Type │   Codec     │
│  (4 bytes)  │  (2 bytes)  │  (1 byte)   │  (1 byte)   │
├─────────────┼─────────────┼─────────────┼─────────────┤
│         Sequence Number (8 bytes)                      │
├─────────────┼─────────────────────────────────────────┤
│         Timestamp (8 bytes, milliseconds)              │
├─────────────┼─────────────┼─────────────────────────┬─┤
│   Payload Size (4 bytes)  │  Chunk Index (2 bytes) │T│
├───────────────────────────┼────────────────────────┴─┤
│   Checksum (2 bytes)      │    Reserved (2 bytes)    │
└───────────────────────────┴──────────────────────────┘
    Total: 32 bytes
```

### 4.2 Field Descriptions

| Field               | Type   | Description                                                         |
| ------------------- | ------ | ------------------------------------------------------------------- |
| **Magic**           | uint32 | Protocol identifier: `0x56494445` ("VIDE")                          |
| **Version**         | uint16 | Protocol version: `0x0001` (v1.0)                                   |
| **Frame Type**      | uint8  | `0x01` = I-frame (keyframe)<br>`0x02` = P-frame<br>`0x03` = B-frame |
| **Codec**           | uint8  | `0x01` = H.264<br>`0x02` = MJPEG<br>`0x03` = VP8                    |
| **Sequence Number** | uint64 | Monotonically increasing frame counter                              |
| **Timestamp**       | uint64 | Unix timestamp in milliseconds                                      |
| **Payload Size**    | uint32 | Size of frame data in bytes (max 1MB)                               |
| **Chunk Index**     | uint16 | For fragmented frames: chunk number<br>`0x0000` = not chunked       |
| **Total Chunks**    | uint8  | Total chunks for this frame (in Reserved)                           |
| **Checksum**        | uint16 | CRC16 of payload data                                               |
| **Reserved**        | uint16 | Future use / total chunks                                           |

### 4.3 Frame Payload

```
┌────────────────────────────────────────────────────┐
│                Frame Data                          │
│          (Variable length, max 1MB)                │
│                                                    │
│  For H.264: NAL units                              │
│  For MJPEG: JPEG compressed image                  │
└────────────────────────────────────────────────────┘
```

---

## 5. TRANSMISSION PROTOCOL

### 5.1 Frame Transmission

1. **Single Frame (< 32KB)**

   ```
   [32-byte Header] + [Frame Data]
   ```

2. **Chunked Frame (> 32KB)**
   ```
   [Header Chunk 0] + [Data Chunk 0]
   [Header Chunk 1] + [Data Chunk 1]
   ...
   [Header Chunk N] + [Data Chunk N]
   ```

### 5.2 Sequence Flow

```
Broadcaster                Server                  Viewer
    |                         |                       |
    |--- START_STREAM ------->|                       |
    |<--- STREAM_ACK ---------|                       |
    |                         |<--- JOIN_STREAM ------|
    |                         |---- JOIN_ACK -------->|
    |                         |                       |
    |=== Frame 0 (I-frame) ==>|                       |
    |                         |==== Frame 0 =========>|
    |=== Frame 1 (P-frame) ==>|                       |
    |                         |==== Frame 1 =========>|
    |=== Frame 2 (P-frame) ==>|                       |
    |                         |==== Frame 2 =========>|
    |         ...             |          ...          |
    |                         |                       |
    |                         |<-- CHANGE_QUALITY ----|
    |<-- QUALITY_ADJUST ------|                       |
    |                         |--- QUALITY_CHANGED -->|
    |                         |                       |
    |=== Frame N (adjusted) =>|                       |
    |                         |==== Frame N =========>|
    |                         |                       |
    |--- STOP_STREAM -------->|                       |
    |                         |---- STREAM_ENDED ---->|
```

---

## 6. ERROR HANDLING

### 6.1 Error Codes

```json
{
  "type": "ERROR",
  "error_code": 1001,
  "error_message": "Frame too large",
  "details": {
    "frame_seq": 12345,
    "frame_size": 2097152,
    "max_allowed": 1048576
  }
}
```

### 6.2 Error Code List

| Code | Name              | Description                  |
| ---- | ----------------- | ---------------------------- |
| 1001 | FRAME_TOO_LARGE   | Frame exceeds MAX_FRAME_SIZE |
| 1002 | INVALID_CODEC     | Unsupported codec specified  |
| 1003 | CORRUPT_FRAME     | Checksum mismatch            |
| 1004 | SEQUENCE_GAP      | Missing frames detected      |
| 1005 | BUFFER_OVERFLOW   | Server buffer full           |
| 1006 | SESSION_NOT_FOUND | Invalid session_id           |
| 1007 | UNAUTHORIZED      | Viewer not permitted         |
| 2001 | NETWORK_TIMEOUT   | Connection timeout           |
| 2002 | CONNECTION_LOST   | Socket disconnected          |

---

## 7. QUALITY ADAPTATION

### 7.1 Quality Levels

| Quality | Resolution | FPS | Bitrate  | Use Case          |
| ------- | ---------- | --- | -------- | ----------------- |
| LOW     | 320x240    | 15  | 500 Kbps | Poor network      |
| MEDIUM  | 640x480    | 24  | 1.5 Mbps | Standard          |
| HIGH    | 1280x720   | 30  | 3 Mbps   | Good network      |
| ULTRA   | 1920x1080  | 30  | 6 Mbps   | Excellent network |

### 7.2 Adaptation Triggers

- **Latency > 500ms:** Downgrade quality
- **Frame drops > 10%:** Reduce resolution
- **Bandwidth stable:** Attempt upgrade after 30s
- **Manual request:** Immediate change

---

## 8. SYNCHRONIZATION

### 8.1 Clock Synchronization

```json
{
  "type": "TIME_SYNC",
  "server_time": 1700000000123,
  "client_time": 1700000000100
}
```

### 8.2 Frame Timestamp Handling

- All timestamps in **milliseconds since Unix epoch**
- Broadcaster sets initial timestamp
- Server relays without modification
- Viewer uses for frame ordering and playout timing

---

## 9. BUFFERING STRATEGY

### 9.1 Server Buffer

- **Capacity:** 60 frames (2 seconds at 30 FPS)
- **Drop policy:** Drop oldest P-frames first
- **Keyframe retention:** Always keep last keyframe

### 9.2 Client Buffer

- **Capacity:** 30 frames (1 second)
- **Initial buffering:** Wait for 10 frames before playback
- **Underrun handling:** Freeze frame, request quality downgrade

---

## 10. SECURITY CONSIDERATIONS

### 10.1 Authentication (Future)

```json
{
  "type": "AUTH",
  "token": "jwt_token_here",
  "user_id": "user_123"
}
```

### 10.2 Encryption (Future)

- Consider TLS for production
- Frame payload encryption optional

---

## 11. IMPLEMENTATION NOTES

### 11.1 Python Struct Format

```python
import struct

# Pack frame header
header = struct.pack(
    '!IHBBQQIHHBx',  # Network byte order (big-endian)
    0x56494445,      # Magic
    0x0001,          # Version
    frame_type,      # Frame type
    codec,           # Codec
    seq_num,         # Sequence
    timestamp,       # Timestamp
    payload_size,    # Payload size
    chunk_index,     # Chunk index
    checksum,        # Checksum
    total_chunks     # Total chunks (in reserved byte)
)
```

### 11.2 Sample Usage

```python
# Sending a frame
frame_data = encode_frame(raw_frame)
header = create_frame_header(seq, timestamp, len(frame_data))
socket.sendall(header + frame_data)

# Receiving a frame
header = socket.recv(32)
magic, version, ftype, codec, seq, ts, size, chunk, crc, _ = parse_header(header)
payload = socket.recv(size)
if verify_checksum(payload, crc):
    process_frame(payload)
```

---

## 12. TESTING PROTOCOL

### 12.1 Test Scenarios

1. **Single viewer, no packet loss**
2. **Multiple viewers, varied quality**
3. **Simulated packet loss (5%, 10%, 20%)**
4. **Bandwidth throttling**
5. **Broadcaster disconnect**
6. **Viewer late join**

### 12.2 Performance Metrics

- **End-to-end latency:** < 500ms target
- **Frame drop rate:** < 5% acceptable
- **CPU usage:** < 50% per client
- **Memory:** < 100MB per stream

---

## APPENDIX A: CONSTANTS

```python
# Protocol constants
MAGIC_NUMBER = 0x56494445  # "VIDE"
PROTOCOL_VERSION = 0x0001
HEADER_SIZE = 32
MAX_FRAME_SIZE = 1_048_576  # 1MB
CHUNK_SIZE = 32_768  # 32KB

# Frame types
FRAME_TYPE_I = 0x01
FRAME_TYPE_P = 0x02
FRAME_TYPE_B = 0x03

# Codecs
CODEC_H264 = 0x01
CODEC_MJPEG = 0x02
CODEC_VP8 = 0x03
```

---

## APPENDIX B: CHANGE LOG

| Version | Date       | Changes                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2025-11-17 | Initial protocol specification |
