# Socket Programming - RTSP/RTP Video Streaming

This project implements a Video Streaming application using the **Client-Server** model. It utilizes **RTSP** (Real Time Streaming Protocol) for session control and **RTP** (Real-time Transport Protocol) for data transmission over UDP.

## Project Structure

The project is organized as follows:

- **`src/`**: Contains the Python source code.
  - `Server.py`: The server application that streams video frames.
  - `ServerWorker.py`: Handles client requests and RTP packetization.
  - `Client.py`: The client application with a GUI to control playback.
  - `ClientLauncher.py`: Entry point to launch the client.
  - `RtpPacket.py`: Class for handling RTP packets.
  - `VideoStream.py`: Helper class to read video frames from MJPEG files.
- **`video_stream/`**: Contains media files.
  - `movie.Mjpeg`: The sample video file used for streaming.
- **`docs/`**: Documentation and assignment requirements.

## Prerequisites

- **Python 3.x**
- **Libraries**:
  - `tkinter` (usually included with Python)
  - `Pillow` (PIL)

To install Pillow:
```bash
pip install Pillow
```

## How to Run

### 1. Start the Server

Open a terminal, navigate to the `src` directory, and run the server on a specific port (e.g., 8554):

```powershell
cd src
python Server.py 8554
```

### 2. Start the Client

Open a **new** terminal, navigate to the `src` directory, and launch the client. You need to specify the server address, server port, RTP port (for receiving video), and the video file path.

```powershell
cd src
python ClientLauncher.py localhost 8554 5008 ../video_stream/movie.Mjpeg
```

- **Server_name**: `localhost` (or IP address of the server)
- **Server_port**: `8554` (must match the port used for the server)
- **RTP_port**: `5008` (any free port on the client)
- **Video_file**: `../video_stream/movie.Mjpeg` (relative path to the video file)

## Usage

Once the Client GUI opens:

1.  **Setup**: Click to establish an RTSP session with the server.
2.  **Play**: Click to start receiving and playing the video stream.
3.  **Pause**: Click to pause the video.
4.  **Teardown**: Click to stop the session and close the application.

## Protocol Details

- **RTSP**: Used for `SETUP`, `PLAY`, `PAUSE`, and `TEARDOWN` requests over TCP.
- **RTP**: Used to encapsulate MJPEG video frames over UDP. The implementation includes a custom `RtpPacket` class to handle header construction.

## Contributors

- [Student Name 1]
- [Student Name 2]
- [Student Name 3]
