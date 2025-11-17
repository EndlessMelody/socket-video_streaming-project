# Main server logic
import socket 

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received data: {data.decode()}")
                conn.sendall(data)  # Echo back the received data

if __name__ == "__main__":
    start_server()