# 🛡️ Advanced Multi-Layer Cyber-Security Framework
### High-Performance Stress Testing, Protocol Analysis & AI-Adversary Suite
![Python](https://img.shields.io/badge/python-3.12-blue.svg) ![Security](https://img.shields.io/badge/Security-Red%20Teaming-red.svg) ![Research](https://img.shields.io/badge/Focus-Educational-green.svg)

> **⚠️ Legal Disclaimer:** This framework is developed strictly for **Educational Research** and **Authorized Stress Testing**. Unauthorized use against third-party infrastructure is illegal. The author assumes no liability for misuse.

---

## 🌌 Project Overview
This repository is a sophisticated technical suite designed to simulate high-concurrency traffic patterns and adversarial machine learning vectors. It explores the intersection of **Layer 4 Transport exhaustion**, **Layer 7 Application bypass**, and **Stochastic Gradient Descent (A-SGD)** poisoning.

---

## 🧬 Understanding the Attack Surface

### 1. DDoS (Distributed Denial of Service)
A DDoS attack aims to render a service unavailable by overwhelming the target with a flood of orchestrated traffic.

#### 🔴 Layer 4: SYN Flood (Transport Layer)
**The Mechanism:** Exploits the **TCP Three-Way Handshake**. 
1. The attacker sends a `SYN` packet.
2. The server responds with `SYN-ACK` and reserves resources (TCB).
3. The attacker **never** sends the final `ACK`.
**Result:** The server’s connection table stays "Half-Open" until it exhausts all RAM/CPU, refusing legitimate users.

#### 🟠 Layer 7: HTTP Flood (Application Layer)
**The Mechanism:** Mimics real human behavior by sending `GET` or `POST` requests. 
* Uses **Asynchronous I/O (`asyncio`)** to manage 10,000+ concurrent connections from a single node.
* Implements **Header Rotation** (User-Agent, Referer) to bypass Web Application Firewalls (WAF).
**Result:** Overwhelms the backend processing logic and database query pools.
<img width="685" height="395" alt="image" src="https://github.com/user-attachments/assets/e3e225c5-0b93-4820-b3a3-4031413f810b" />
<img width="2910" height="1747" alt="image" src="https://github.com/user-attachments/assets/8b5cea27-c70e-4a1b-a7b7-212f3484be98" />

---

### 2. Brute Force Attacks
**The Mechanism:** A trial-and-error method used to decode encrypted data or hidden directories.
* **Dictionary Attack:** Systematically testing millions of common passwords from a wordlist.
* **Credential Stuffing:** Using leaked data to attempt unauthorized access.
* **Mechanism:** The script iterates through a `wordlist.txt` at high speed, analyzing HTTP response codes (e.g., `200 OK` vs `401 Unauthorized`) to identify successful breaches.
<img width="742" height="357" alt="image" src="https://github.com/user-attachments/assets/39a99120-6838-421e-8ef4-85ed946916ba" />

---

### 3. A-SGD (Asynchronous Stochastic Gradient Descent) Adversary
As an **LLM Engineer**, this module explores the frontier of **Adversarial Machine Learning**.
**The Mechanism:** In distributed AI training, nodes share "Gradients" to update a global model.
* **The Attack:** This script injects **malicious mathematical noise** (poisoned gradients) into the update stream.
* **Result:** The AI model becomes "poisoned," leading to intentional misclassification or the creation of a model "backdoor."
<img width="540" height="321" alt="image" src="https://github.com/user-attachments/assets/2e6640d4-f929-4a2f-86e2-610689cc73f5" />

---
### AsyncRAT malware attack
#### 1. The Delivery & Dropper Phase (Initial Access)
Malware rarely arrives as a raw .py file. Instead, it is "compiled" or "packed."
The Dropper: Usually a small Batch or PowerShell script. Its only job is to download the main payload and a "portable" Python interpreter (since most victims don't have Python installed).
Obfuscation: The code is often "Base64 encoded" or "AES encrypted" within the dropper to hide from basic Anti-Virus (AV) string scanning.

#### 🛡️ 2. The Persistence Mechanism (Survival)
A RAT is useless if it disappears when the user restarts their computer. AsyncRAT uses several Windows-specific tricks:
Registry Injection: It adds a path to itself in HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run.
Scheduled Tasks: It creates a task that triggers every time the user logs in or every 10 minutes if the process is killed.
Process Ghosting: It might try to inject its code into a legitimate process like svchost.exe or explorer.exe so that when you look at Task Manager, everything looks normal.

#### 🎹 3. The I/O Hooking (Keylogging & Surveillance)
Using the pynput library you mentioned, the RAT sets up a Hook.
The Hook: It listens to the Operating System's keyboard buffer. Every time a key is pressed, the OS sends a message; the RAT intercepts this message, records the character, and stores it in a hidden local log file or a memory variable.
Stealth: Professional RATs wait for the user to open specific windows (like "PayPal" or "Gmail") before they start logging, to save space and remain undetected.

#### 📡 4. The Asynchronous Beaconing (C2 Communication)
This is the "Async" part of AsyncRAT. Traditional "Bind Shells" are easy to find because they leave a port open. AsyncRAT uses a Reverse Connection.
The Beacon: The infected machine (Client) initiates the connection to the attacker (Server).
The "Heartbeat": Instead of staying connected 24/7, it sends a small encrypted packet every 60 seconds. This "asynchronous" behavior mimics normal web browsing, making it very hard for firewalls to distinguish from a person checking their email.
The Payload: If the attacker has a command waiting (e.g., "Take Screenshot"), the server sends it back in the response to the beacon.
<img width="876" height="455" alt="image" src="https://github.com/user-attachments/assets/91a85509-801d-483f-93d2-d9d22ba35b7b" />

---

## 🛠️ Framework Logic & Architecture

| Module | Protocol | Core Logic |
| :--- | :--- | :--- |
| **L4 Engine** | TCP/UDP | Raw Sockets & Scapy Packet Crafting |
| **L7 Engine** | HTTP/HTTPS | `Aiohttp` Non-blocking Concurrency |
| **Brute Engine** | Auth/API | Multi-threaded Wordlist Iteration |
| **AI Engine** | A-SGD | Gradient Noise Injection & Model Poisoning |

---

## 📂 Repository Structure
```text
├── modules/            
│   ├── l4_transport/   # SYN/UDP/ICMP flood scripts
│   ├── l7_app/         # HTTP Get/Post bypass scripts
│   └── ml_adversary/   # A-SGD Poisoning & Gradient tools
├── utils/              # Proxy rotators & Wordlist handlers
├── .gitignore          # Environment & VENV protection
└── README.md           # Technical Documentation
