# 📁 Local File Sharing Across Windows Stations

A lightweight **Windows-only LAN file sharing tool** built with Python.  
It enables fast and reliable sharing of **files and folders** between Windows machines on the same local network using simple command-line commands.

No internet required. No encryption overhead. No third-party servers.

---

## ✨ Features

- Share **files and folders**
- Works over **local network (LAN)**
- Automatic sender discovery using `local`
- Short IP support (`13` → `192.168.x.13`)
- Multi-client support
- Real-time transfer progress bar
- Receiver-side folder organization by sender IP
- Sender can stop sharing by typing `exit`
- High-speed transfer using large buffers
- No encryption (maximum speed)

---

## 🖥 Platform Support

- **Windows only**
- Windows 10 / Windows 11
- Not designed for Linux, macOS, or internet use

---

## 📦 Requirements

- Python **3.8+**
- Local network connection (same LAN)

### Python Modules Used

All modules are from the Python standard library:

socket
os
sys
threading
struct
time


No external dependencies required.

---

## 📥 Installation

1. Install Python for Windows  
   https://www.python.org/downloads/windows/  
   *(Make sure **Add Python to PATH** is checked)*

2. Clone or download this repository:
git clone https://github.com/yourname/shrf


3. Keep `app.py` and `shrf.bat` in the same folder.

---

## ⚙ Use From Any Directory (ENV PATH Setup)

You can use `shrf` from **any directory** by adding its folder to the system PATH.

1. Press `Win + R` → type `sysdm.cpl`
2. Go to **Advanced → Environment Variables**
3. Under **System variables**, edit `Path`
4. Add the folder containing `shrf.bat`
5. Click **OK** and restart the terminal

Now you can run:
shrf send ...
shrf get ...

from anywhere.

---

## 🚀 Usage

### ▶ Send (File or Folder)

shrf send <file_or_folder> <code> <password>


**Example:**
shrf send hello.py 123 123


or:
shrf send myFolder 123 123


You will see:
Sharing on 192.168.0.14:5001
Type 'exit' to stop sharing


---

### ⬇ Receive

shrf get <ip | local | short-ip> <code> <password>


**Examples:**

Auto discovery:
shrf get local 123 123


Short IP:
shrf get 13 123 123


Full IP:
shrf get 192.168.0.14 123 123


---

## 📂 Received Files

Received files are stored automatically in:

received_from<SENDER_IP>/


Example:
received_from192.168.0.14/


Folder structure from the sender is preserved.

---

## 🔐 Authentication

A simple **code + password** handshake is used:

<code>:<password>


This is **not encryption** and is intended only to prevent accidental connections.

---

## 🧠 How `local` Discovery Works

- Scans the local subnet
- Only IP range **0–50** is checked
- Automatically authenticates sender
- Connects to the first valid match

---

## ⚠ Firewall Notice

Windows Defender Firewall may block Python.

If connections fail:
- Allow `python.exe` through **Private Networks**
- Or temporarily disable firewall for testing

---

## 🧪 Troubleshooting

**Stuck at “Connecting…”**
- Sender not running
- Firewall blocking Python
- Different network/subnet

**“No sender found on LAN”**
- Sender not running
- Wrong code/password
- Sender outside IP range 0–50

---

## 📁 Project Structure

shrf/
├── app.py
├── shrf.bat
├── README.md
└── received_from*/

---

## ⭐ Author

**"Dev. MUNTAHI"**
