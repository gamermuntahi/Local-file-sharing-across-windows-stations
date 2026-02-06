import socket
import sys
import os
import threading
import struct
import time

PORT = 5001
BUFFER = 65536
TIMEOUT = 3
LAN_SCAN_RANGE = range(0, 51)
hostname = socket.gethostname()

stop_server = False


# ================== UTILS ==================

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def normalize_ip(ip):
    if ip.lower() == "local":
        return "local"

    if ip.isdigit():
        base = ".".join(get_local_ip().split(".")[:-1])
        return f"{base}.{ip}"

    return ip


def progress(done, total):
    if total == 0:
        return
    p = int(done * 100 / total)
    bar = "█" * (p // 5) + "-" * (20 - p // 5)
    print(f"\r[{bar}] {p}%", end="", flush=True)


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Connection lost")
        data += part
    return data


# ================== SENDER ==================

def send_file(conn, path):
    if os.path.isfile(path):
        conn.send(b"FILE")
        filesize = os.path.getsize(path)
        name = os.path.basename(path)

        conn.send(struct.pack("Q", filesize))
        conn.send(struct.pack("H", len(name)))
        conn.send(name.encode())

        sent = 0
        with open(path, "rb") as f:
            while chunk := f.read(BUFFER):
                conn.sendall(chunk)
                sent += len(chunk)
                progress(sent, filesize)
        print()

    else:
        conn.send(b"DIR")
        for root, _, files in os.walk(path):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, path)

                conn.send(b"FILE")
                conn.send(struct.pack("H", len(rel)))
                conn.send(rel.encode())

                size = os.path.getsize(full)
                conn.send(struct.pack("Q", size))

                sent = 0
                with open(full, "rb") as f:
                    while chunk := f.read(BUFFER):
                        conn.sendall(chunk)
                        sent += len(chunk)
                        progress(sent, size)
                print()

        conn.send(b"END")


def client_handler(conn, path, code, password):
    try:
        conn.settimeout(TIMEOUT)

        auth = conn.recv(128).decode()
        if auth != f"{code}:{password}":
            conn.send(b"NO")
            return

        conn.send(b"OK")
        send_file(conn, path)

    except Exception as e:
        print("✖ Client error:", e)
    finally:
        conn.close()


def send_mode(path, code, password):
    global stop_server

    if not os.path.exists(path):
        print("❌ File or folder not found")
        return

    ip = get_local_ip()
    print(f"📡 Sharing on {ip}:{PORT}")
    print("🛑 Type 'exit' to stop sharing")

    s = socket.socket()
    s.bind(("", PORT))
    s.listen(5)

    def console_watch():
        global stop_server
        while input().lower() != "exit":
            pass
        stop_server = True
        s.close()

    threading.Thread(target=console_watch, daemon=True).start()

    while not stop_server:
        try:
            conn, _ = s.accept()
            threading.Thread(
                target=client_handler,
                args=(conn, path, code, password),
                daemon=True
            ).start()
        except:
            break

    print("🛑 Sharing stopped")


# ================== CLIENT ==================

def discover_sender(code, password):
    print("🔍 Scanning LAN for sender...")
    base = ".".join(get_local_ip().split(".")[:-1])
    found = None
    lock = threading.Lock()

    def try_ip(ip):
        nonlocal found
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((ip, PORT))
            s.send(f"{code}:{password}".encode())
            if s.recv(2) == b"OK":
                with lock:
                    if not found:
                        found = ip
            s.close()
        except:
            pass

    threads = []
    for i in LAN_SCAN_RANGE:
        ip = f"{base}.{i}"
        t = threading.Thread(target=try_ip, args=(ip,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return found


def receive_files(sock, sender_ip):
    base_folder = f"received_from{sender_ip}"
    os.makedirs(base_folder, exist_ok=True)

    mode = sock.recv(4)
    if mode == b"FILE":
        filesize = struct.unpack("Q", recv_exact(sock, 8))[0]
        name_len = struct.unpack("H", recv_exact(sock, 2))[0]
        name = recv_exact(sock, name_len).decode()

        out = os.path.join(base_folder, (name))
        received = 0

        with open(out, "wb") as f:
            while received < filesize:
                data = sock.recv(BUFFER)
                if not data:
                    break
                f.write(data)
                received += len(data)
                progress(received, filesize)

        print(f"\n✔ Saved {out}")

    elif mode == b"DIR":
        while True:
            tag = sock.recv(4)
            if tag == b"END":
                break

            name_len = struct.unpack("H", recv_exact(sock, 2))[0]
            rel = recv_exact(sock, name_len).decode()
            size = struct.unpack("Q", recv_exact(sock, 8))[0]

            out = os.path.join(base_folder, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)

            received = 0
            with open(out, "wb") as f:
                while received < size:
                    data = sock.recv(BUFFER)
                    f.write(data)
                    received += len(data)
                    progress(received, size)
            print(f"\n✔ Saved {out}")



def get_mode(ip, code, password):
    ip = normalize_ip(ip)

    if ip == "local":
        ip = discover_sender(code, password)
        if not ip:
            print("❌ No sender found on LAN")
            return
        print(f"✔ Found sender at {ip}")

    print(f"📡 Connecting to {ip}:{PORT}")
    s = socket.socket()
    s.settimeout(5)
    s.connect((ip, PORT))

    s.send(f"{code}:{password}".encode())
    if s.recv(2) != b"OK":
        print("❌ Authentication failed")
        return

    receive_files(s, ip)  # pass sender IP here
    s.close()



# ================== MAIN ==================

if __name__ == "__main__":
    print("===== SHRF LAN FILE SHARING =====")

    if len(sys.argv) != 5:
        print("Usage:")
        print("  shrf send <file|folder> <code> <pass>")
        print("  shrf get <ip|local> <code> <pass>")
        sys.exit()

    if sys.argv[1] == "send":
        send_mode(sys.argv[2], sys.argv[3], sys.argv[4])

    elif sys.argv[1] == "get":
        get_mode(sys.argv[2], sys.argv[3], sys.argv[4])
