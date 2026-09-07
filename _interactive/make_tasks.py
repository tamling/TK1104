#!/usr/bin/env python3
"""Generate the interactive self-check snippets under chapters/_tasks/.

Each task below is rendered as a raw-HTML block whose JSON config is read
by includes/interactive.html. Answers are stored as djb2 hashes of
normalised strings (lowercase, all whitespace removed) and the reveal
text of the "Show solution" button is base64-encoded, so the rendered
pages never carry the correct answers in plain text. This file is the
single source of truth for the tasks - edit here and re-run:

    python3 _interactive/make_tasks.py
"""
import base64
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "chapters" / "_tasks"


def djb2(s: str) -> int:
    h = 5381
    for c in s:
        h = ((h * 33) + ord(c)) & 0xFFFFFFFF
    return h


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.lower())


def b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def sort_task(title, prompt, buckets, placements, done=None):
    """placements: list of (chip, bucket_index)."""
    chips = [c for c, _ in placements]
    key = sorted(djb2(f"{norm(c)}|{i}") for c, i in placements)
    lines = []
    for i, bucket in enumerate(buckets):
        members = [c for c, j in placements if j == i]
        lines.append(f"{bucket}: {'; '.join(members)}")
    cfg = {"type": "sort", "title": title, "prompt": prompt,
           "buckets": buckets, "chips": chips, "key": key,
           "_sol": "\n".join(lines)}
    if done:
        cfg["done"] = done
    return cfg


def order_task(title, prompt, steps, done=None):
    key = sorted(djb2(f"{norm(c)}|{i}") for i, c in enumerate(steps))
    sol = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))
    cfg = {"type": "order", "title": title, "prompt": prompt,
           "chips": steps, "key": key, "_sol": sol}
    if done:
        cfg["done"] = done
    return cfg


def input_task(title, prompt, fields, done=None):
    """fields: list of (label, [accepted answers]) or
    (label, [accepted answers], display)."""
    out, lines = [], []
    for f in fields:
        label, answers = f[0], f[1]
        display = f[2] if len(f) > 2 else answers[0]
        out.append({"label": label,
                    "answers": sorted(djb2(norm(a)) for a in answers)})
        lines.append(f"{label} {display}")
    cfg = {"type": "input", "title": title, "prompt": prompt,
           "fields": out, "_sol": "\n".join(lines)}
    if done:
        cfg["done"] = done
    return cfg


def gate_task(title, prompt, tt, correct, options, done=None):
    """Mystery-gate lab: tt is the truth table [00, 01, 10, 11] of the
    hidden gate that drives the lamp; the student flips the switches and
    names the gate."""
    states = ["A=0 B=0", "A=0 B=1", "A=1 B=0", "A=1 B=1"]
    lines = [f"{s} → lamp {'ON' if v else 'off'}"
             for s, v in zip(states, tt)]
    lines.append(f"That behaviour is {correct}.")
    cfg = {"type": "gate", "title": title, "prompt": prompt,
           "tt": tt, "options": options,
           "key": [djb2(f"{norm(correct)}|gate")],
           "_sol": "\n".join(lines)}
    if done:
        cfg["done"] = done
    return cfg


TASKS = {
    # ── Chapter 1 ────────────────────────────────────────────────────────
    "01-byte": input_task(
        "One byte, your call",
        "Read the byte <code>01001010</code> two ways, exactly as in the "
        "worked exercise.",
        [("As an unsigned integer:", ["74"]),
         ("As an ASCII character:", ["j"], "J")],
        done="Same bits, two readings - the convention decides."),
    "01-hw-sw": sort_task(
        "Hardware or software?",
        "Every system has two halves - sort these eight into theirs.",
        ["Hardware", "Software"],
        [("CPU", 0), ("RAM", 0), ("SSD", 0), ("GPU", 0),
         ("operating system", 1), ("device driver", 1),
         ("web browser", 1), ("your Python script", 1)]),
    "01-ipos": sort_task(
        "The IPOS model",
        "Place each device where it belongs in the "
        "Input–Processing–Output–Storage loop.",
        ["Input", "Processing", "Output", "Storage"],
        [("keyboard", 0), ("mouse", 0), ("sensor", 0),
         ("CPU", 1), ("GPU", 1),
         ("screen", 2), ("printer", 2),
         ("SSD", 3), ("RAM", 3)]),
    "01-milestones": order_task(
        "Eighty years in six milestones",
        "Put the milestones in chronological order.",
        ["ENIAC - the first general-purpose electronic computer",
         "The microprocessor - Intel's 4004",
         "The IBM PC reaches businesses and homes",
         "The World Wide Web launches at CERN",
         "The iPhone takes the smartphone mainstream",
         "ChatGPT puts generative AI in everyone's hands"]),
    "01-volatile": sort_task(
        "Gone at power-off?",
        "Sort the memory levels: which forget at power-off, which survive?",
        ["Volatile (contents vanish)", "Persistent (survives power-off)"],
        [("registers", 0), ("cache", 0), ("RAM", 0),
         ("SSD", 1), ("HDD", 1)],
        done="That is why unsaved work dies with the power - it lived in RAM."),
    "01-units": input_task(
        "The small family of units",
        "Three numbers everyone in this course knows cold.",
        [("Bits in one byte:", ["8", "eight"]),
         ("Distinct values of one byte:", ["256"]),
         ("Word size of a modern PC, in bits:", ["64"])]),

    # ── Chapter 2 ────────────────────────────────────────────────────────
    "02-convert": input_task(
        "Both directions",
        "Convert - weights for one direction, subtraction or division for "
        "the other.",
        [("1101 0110₂ in decimal:", ["214"]),
         ("77₁₀ in binary:",
          ["1001101", "01001101", "100 1101", "0100 1101"], "100 1101")]),
    "02-twoscomp": input_task(
        "Two's complement",
        "Invert and add 1 - then read a pattern back.",
        [("−13 in 8-bit two's complement:",
          ["11110011", "1111 0011"], "1111 0011"),
         ("1111 1111 read as a signed 8-bit value:", ["-1", "−1"], "−1")]),
    "02-nibbles": sort_task(
        "Hex digits are nibbles",
        "Each hex digit is exactly four bits - match each bit group to "
        "its digit.",
        ["A", "5", "F", "3"],
        [("1010", 0), ("0101", 1), ("1111", 2), ("0011", 3)],
        done="Grouping, not arithmetic - that is the whole trick."),
    "02-hexdec": input_task(
        "Hex both ways",
        "One conversion in each direction.",
        [("F3₁₆ in decimal:", ["243"]),
         ("42₁₀ in hexadecimal:", ["2a", "0x2a"], "2A")]),
    "02-bases": sort_task(
        "Spot the base",
        "Source-code prefixes mark the base - sort the literals.",
        ["Binary", "Octal", "Hexadecimal"],
        [("0b1011", 0), ("0b0001", 0),
         ("0o755", 1), ("0o644", 1),
         ("0xA39F", 2), ("0xFF", 2)],
        done="0b, 0o, 0x - the prefix is the convention, spelled out."),
    "02-shift": input_task(
        "Shifting is arithmetic",
        "Start from <code>0000 0110</code> (decimal 6).",
        [("Shifted left one place, as decimal:", ["12"]),
         ("Shifted right one place, as decimal:", ["3"])],
        done="Left doubles, right halves - cheaper than multiplication."),

    # ── Chapter 3 ────────────────────────────────────────────────────────
    "03-compression": sort_task(
        "Lossless or lossy?",
        "Sort the formats by their compression family.",
        ["Lossless", "Lossy"],
        [("PNG", 0), ("FLAC", 0), ("GIF", 0),
         ("JPEG", 1), ("MP3", 1), ("AAC", 1), ("H.264", 1)]),
    "03-magic": sort_task(
        "Magic numbers",
        "The first bytes say what a file really is - match each magic "
        "number to its format.",
        ["PDF", "JPEG", "ZIP", "GIF", "Linux executable"],
        [("%PDF-", 0), ("FF D8 FF", 1), ("50 4B (“PK”)", 2),
         ("GIF89a", 3), ("7F 45 4C 46 (“ELF”)", 4)],
        done="The extension is convention; the magic number is reality."),
    "03-utf8": input_task(
        "UTF-8 byte counts",
        "How many bytes does UTF-8 spend on each character?",
        [("A plain A (U+0041):", ["1", "one"]),
         ("The Norwegian å (U+00E5):", ["2", "two"]),
         ("The emoji 😀 (U+1F600):", ["4", "four"])],
        done="Same “length” in characters is not the same length in bytes."),
    "03-raster-vector": sort_task(
        "Pixels or instructions?",
        "Raster stores the result, vector stores the recipe - sort the "
        "formats.",
        ["Raster (pixels)", "Vector (instructions)"],
        [("JPEG", 0), ("PNG", 0), ("GIF", 0), ("WebP", 0),
         ("SVG", 1), ("PDF drawing instructions", 1)]),
    "03-format-job": sort_task(
        "The right format for the job",
        "Match each format to the job it fits best.",
        ["Screenshot of a table", "Holiday photo",
         "Logo from favicon to billboard", "Music archive"],
        [("PNG", 0), ("JPEG", 1), ("SVG", 2), ("FLAC", 3)],
        done="Crisp text, small photos, infinite scaling, bit-perfect audio."),
    "03-nyquist": input_task(
        "Nyquist on the spec sheet",
        "Human hearing reaches about 20 kHz.",
        [("The Nyquist minimum sample rate, in kHz:", ["40"]),
         ("The CD's actual sample rate, in kHz:", ["44.1", "44,1"], "44.1")],
        done="The CD is the minimum plus a small engineering margin."),

    # ── Chapter 4 ────────────────────────────────────────────────────────
    "04-hidas": order_task(
        "The HIDAS cycle",
        "Put the five steps of the CPU's cycle in order.",
        ["Holen - fetch the instruction into IR",
         "Inkrementieren - increment the PC",
         "Dekodieren - decode the instruction",
         "Ausführen - execute the operation",
         "Speichern - store the result"]),
    "04-bitwise": input_task(
        "Bitwise, by hand",
        "Apply the operations column by column - no carries.",
        [("1100 AND 1010:", ["1000"]),
         ("1100 XOR 1010:", ["0110", "110"], "0110")]),
    "04-hierarchy": order_task(
        "The memory hierarchy",
        "Order the levels from fastest (top) to slowest (bottom).",
        ["Registers", "Cache (L1/L2/L3)", "RAM", "SSD", "HDD"],
        done="Each level is faster, smaller and costlier than the one below."),
    "04-lamp-and": gate_task(
        "Mystery gate I",
        "Two switches, one lamp, one hidden gate.",
        [0, 0, 0, 1], "AND", ["AND", "OR", "XOR", "NAND"],
        done="The lamp lights only when both switches are on - that is AND."),
    "04-lamp-xor": gate_task(
        "Mystery gate II",
        "Same wiring, different box.",
        [0, 1, 1, 0], "XOR", ["AND", "OR", "XOR", "NAND"],
        done="Exactly one switch on lights the lamp - the inputs must differ."),
    "04-lamp-nand": gate_task(
        "Mystery gate III",
        "One more - and this one can build all the others.",
        [1, 1, 1, 0], "NAND", ["AND", "OR", "XOR", "NAND", "NOR"],
        done="AND, then inverted - and NAND alone can build every other gate."),
    "04-bus": input_task(
        "The address bus",
        "An N-bit bus reaches 2^N locations.",
        [("Locations a 16-bit address bus reaches:", ["65536", "65 536"]),
         ("Where 32-bit systems topped out, in GB:", ["4", "4gb"], "4 GB")]),
    "04-components": sort_task(
        "The five Von Neumann components",
        "Which of these belong to the five hardware components - and "
        "which do not?",
        ["One of the five components", "Not one of them"],
        [("control unit", 0), ("ALU", 0), ("memory", 0),
         ("input", 0), ("output", 0),
         ("the operating system", 1), ("the compiler", 1)],
        done="The OS and the compiler are software - not hardware components."),

    # ── Chapter 5 ────────────────────────────────────────────────────────
    "05-states": sort_task(
        "Name the state",
        "Classify each situation as running, ready or blocked.",
        ["Running", "Ready", "Blocked"],
        [("crunching frames on core 3 right now", 0),
         ("runnable, but all cores are busy", 1),
         ("time slice just ended, queued again", 1),
         ("waiting for a disk read to finish", 2),
         ("waiting for data from the network card", 2)]),
    "05-boot": order_task(
        "The boot chain",
        "Put the power-on hand-over in order.",
        ["Firmware (BIOS/UEFI) checks the hardware",
         "The boot loader starts",
         "The kernel is loaded into memory",
         "The rest of the system starts, up to the login screen"]),
    "05-modes": sort_task(
        "User mode or kernel mode?",
        "Where does each of these run?",
        ["User mode", "Kernel mode"],
        [("an application's own code", 0),
         ("a game's rendering loop", 0),
         ("the scheduler", 1),
         ("a context switch", 1),
         ("direct access to the disk hardware", 1)]),
    "05-scheduling": sort_task(
        "Scheduling strategies",
        "Match each statement to the strategy it describes.",
        ["Round-robin", "First-come-first-served", "Priority"],
        [("a fixed time slice for each process, in turn", 0),
         ("the workhorse of interactive systems", 0),
         ("processes run in arrival order", 1),
         ("one long job delays all the rest", 1),
         ("the important processes first", 2)]),
    "05-chmod": input_task(
        "Permissions in octal",
        "Read–write–execute are three bits, and three bits are one octal "
        "digit (Chapter 2 pays off).",
        [("rwx as one octal digit:", ["7"]),
         ("r-x as one octal digit:", ["5"])],
        done="chmod 755: rwx for the owner, r-x for group and everyone."),
    "05-views": sort_task(
        "The two views of an OS",
        "Sort each phrase under the view it belongs to.",
        ["Abstraction (top-down)", "Resource management (bottom-up)"],
        [("files instead of disk blocks", 0),
         ("windows instead of pixels", 0),
         ("a simpler “virtual machine” for programs", 0),
         ("scheduling CPU time", 1),
         ("allocating memory to processes", 1),
         ("deciding who runs next", 1)]),

    # ── Chapter 6 ────────────────────────────────────────────────────────
    "06-units": sort_task(
        "Hear the word, know the layer",
        "Match each data unit to its layer.",
        ["Application", "Transport", "Network", "Link"],
        [("message", 0), ("segment", 1), ("datagram", 2), ("frame", 3)]),
    "06-tools": sort_task(
        "Choose the right tool",
        "Which command answers which question?",
        ["ping", "traceroute", "nslookup / dig", "netstat"],
        [("Is the host reachable, and how fast?", 0),
         ("Where along the path does it stop?", 1),
         ("What IP address is behind this name?", 2),
         ("Which connections are open right now?", 3)]),
    "06-history": order_task(
        "How the internet grew",
        "Put the milestones in chronological order.",
        ["ARPANET - the first packet-switched network",
         "TCP/IP - the common protocol that let networks join",
         "DNS - names instead of raw addresses",
         "The World Wide Web opens to everyone",
         "The always-on mobile-and-cloud era"]),
    "06-reach": sort_task(
        "Networks by reach",
        "PAN, LAN, MAN or WAN - sort the examples.",
        ["PAN", "LAN", "MAN", "WAN"],
        [("Bluetooth earbuds on your desk", 0),
         ("your home Wi-Fi", 1),
         ("an office or campus network", 1),
         ("a network spanning a city", 2),
         ("the internet - the largest of all", 3)]),
    "06-delays": sort_task(
        "Four sources of delay",
        "Every hop charges four kinds of delay - match the descriptions.",
        ["Processing", "Queuing", "Transmission", "Propagation"],
        [("the router reads the header and decides the next hop", 0),
         ("waiting behind other packets on the link", 1),
         ("the one that grows as the link gets busy", 1),
         ("pushing all the bits onto the link", 2),
         ("the signal physically travelling the distance", 3)]),
    "06-performance": input_task(
        "Three numbers of a connection",
        "Name the performance measure each phrase describes.",
        [("The pipe's width - the maximum rate a link could carry:",
          ["bandwidth"]),
         ("What you actually get, after overhead and sharing:",
          ["throughput"]),
         ("The delay there and back - what ping reports (abbrev.):",
          ["rtt"], "RTT")]),

    # ── Chapter 7 ────────────────────────────────────────────────────────
    "07-dns": order_task(
        "Resolving a name",
        "Put the steps of a fresh DNS lookup in order.",
        ["Your PC asks the local resolver",
         "The resolver asks the root server",
         "The resolver asks the TLD server",
         "The resolver asks the authoritative server",
         "The answer comes back - and is cached"]),
    "07-url": sort_task(
        "Take a URL apart",
        "Assign each piece of "
        "<code>https://api.campus.no:8080/kurs/tk1104?week=3#plan</code> "
        "to its component.",
        ["Scheme", "Host", "Port", "Path", "Query", "Fragment"],
        [("https", 0), ("api.campus.no", 1), ("8080", 2),
         ("/kurs/tk1104", 3), ("week=3", 4), ("plan", 5)],
        done="DNS resolves the host; the request line carries path and query."),
    "07-status": sort_task(
        "Status codes",
        "Sort the responses by their category - the first digit decides.",
        ["Success (2xx)", "Redirection (3xx)", "Client error (4xx)",
         "Server error (5xx)"],
        [("200 OK", 0), ("301 Moved Permanently", 1),
         ("404 Not Found", 2), ("403 Forbidden", 2),
         ("500 Internal Server Error", 3), ("502 Bad Gateway", 3)]),
    "07-records": sort_task(
        "DNS record types",
        "Match each job to its record type.",
        ["A", "AAAA", "CNAME", "MX", "NS"],
        [("name → IPv4 address", 0),
         ("name → IPv6 address", 1),
         ("an alias for another name", 2),
         ("the domain's mail server", 3),
         ("the authoritative name server", 4)]),
    "07-methods": sort_task(
        "HTTP methods",
        "The first word of the request is the verb - match each meaning.",
        ["GET", "POST", "HEAD", "DELETE"],
        [("fetch the resource", 0),
         ("send data to the server", 1),
         ("only the headers, please", 2),
         ("remove the resource", 3)]),
    "07-mail": sort_task(
        "The mail protocols",
        "Push or pull, and for whom - sort the statements.",
        ["SMTP", "IMAP", "POP3"],
        [("pushes mail towards the recipient", 0),
         ("also carries mail server-to-server", 0),
         ("keeps mail on the server, in sync across devices", 1),
         ("downloads to one client, often removing it from the server", 2)],
        done="SMTP pushes; IMAP and POP3 pull - different lifestyles."),

    # ── Chapter 8 ────────────────────────────────────────────────────────
    "08-tcp-udp": sort_task(
        "TCP or UDP?",
        "Pick the transport protocol each application would choose.",
        ["TCP", "UDP"],
        [("downloading a software update", 0),
         ("loading a web page over HTTPS", 0),
         ("sending an e-mail", 0),
         ("the voice channel of an online game", 1),
         ("a DNS lookup", 1),
         ("a live video stream", 1)]),
    "08-handshake": order_task(
        "The three-way handshake",
        "Put the packets that open a TCP connection in order.",
        ["SYN - the client's opening move",
         "SYN+ACK - the server answers",
         "ACK - the client confirms; the connection is open"]),
    "08-controls": sort_task(
        "Flow or congestion control?",
        "Two different protections - sort the statements.",
        ["Flow control", "Congestion control"],
        [("protects the receiver's buffer", 0),
         ("reacts to the advertised window", 0),
         ("protects the network's shared links", 1),
         ("reacts to packet loss", 1),
         ("slow start and the sawtooth", 1)]),
    "08-ports": input_task(
        "Well-known ports",
        "Three port numbers that recur in every lab and exam.",
        [("HTTPS:", ["443"]),
         ("SSH:", ["22"]),
         ("DNS:", ["53"])]),
    "08-headers": sort_task(
        "Whose property is it?",
        "TCP or UDP - sort the statements.",
        ["TCP", "UDP"],
        [("a three-way handshake before any data", 0),
         ("sequence numbers order every byte", 0),
         ("a FIN closes each direction", 0),
         ("an 8-byte header - four small fields", 1),
         ("“fire and forget”", 1),
         ("the base that QUIC builds on", 1)]),
    "08-loss": order_task(
        "Fast retransmit",
        "A segment is lost - put the recovery in order.",
        ["A segment goes missing on the way",
         "The receiver keeps ACKing the last in-order byte",
         "The sender sees three duplicate ACKs",
         "The sender retransmits at once, without waiting for the timer"]),

    # ── Chapter 9 ────────────────────────────────────────────────────────
    "09-subnet": input_task(
        "Which network, how many hosts",
        "Host <code>192.168.40.77</code> has the mask "
        "<code>255.255.255.224</code> (a /27). AND the fourth octets, "
        "then count the host bits.",
        [("Network address:", ["192.168.40.64", "192.168.40.64/27"]),
         ("Usable hosts:", ["30"])],
        done="Only the mask's 1-bits survive the AND; 2⁵ − 2 = 30."),
    "09-dora": order_task(
        "The DHCP lease",
        "Put the four DORA steps in order.",
        ["Discover - the client broadcasts, having no address yet",
         "Offer - the server proposes an address",
         "Request - the client asks for it",
         "Acknowledge - the server confirms the lease"]),
    "09-private": sort_task(
        "Private or public?",
        "Which of these IPv4 addresses can appear on the public internet?",
        ["Private (LAN only)", "Public (routable)"],
        [("10.0.0.5", 0), ("192.168.1.7", 0), ("172.16.3.9", 0),
         ("8.8.8.8", 1), ("158.36.10.4", 1), ("100.4.2.1", 1)]),
    "09-planes": sort_task(
        "Forwarding or routing?",
        "The data plane and the control plane - sort the statements.",
        ["Forwarding", "Routing"],
        [("the data plane", 0),
         ("per packet, in nanoseconds", 0),
         ("moves the packet to the right outgoing link", 0),
         ("the control plane", 1),
         ("network-wide, in the background", 1),
         ("computes which paths the tables should hold", 1)]),
    "09-icmp": input_task(
        "ICMP by the numbers",
        "The network talking about itself.",
        [("ICMP type of an echo request (ping):", ["8"]),
         ("ICMP type of “time exceeded”:", ["11"]),
         ("The TTL that reveals the third router on a path:", ["3"])],
        done="traceroute is the TTL safeguard, repurposed as a measuring tape."),
    "09-ipv6": sort_task(
        "IPv4 or IPv6?",
        "Sort the properties.",
        ["IPv4", "IPv6"],
        [("32-bit addresses", 0),
         ("dotted decimal, four bytes", 0),
         ("needs NAT to stretch its space", 0),
         ("128-bit addresses", 1),
         ("hex groups, with :: abbreviating zeros", 1),
         ("removes the need for NAT", 1)]),

    # ── Chapter 10 ───────────────────────────────────────────────────────
    "10-boxes": sort_task(
        "Hub, switch, router",
        "Three boxes, three layers - sort the statements.",
        ["Hub", "Switch", "Router"],
        [("physical layer - reads nothing", 0),
         ("repeats every bit to all ports", 0),
         ("link layer - reads MAC addresses", 1),
         ("isolates collision domains, port by port", 1),
         ("network layer - reads IP addresses", 2),
         ("connects networks; needs configuration", 2)]),
    "10-addresses": input_task(
        "Addresses along a path",
        "A packet crosses four links from your laptop to a server. How "
        "many times does each address change?",
        [("IP source and destination change … times:", ["0", "zero", "never"], "0"),
         ("The MAC pair changes … times:", ["4", "four"], "4")],
        done="IP is end-to-end; MAC has per-link scope only."),
    "10-arp": order_task(
        "The ARP exchange",
        "Host A knows only neighbour B's IP - put the exchange in order.",
        ["A broadcasts: “who has this IP? Tell me your MAC”",
         "Only B, the owner of the IP, replies with its MAC",
         "A caches the IP→MAC mapping",
         "A sends the frame to B"]),
    "10-access": sort_task(
        "Sharing the medium",
        "Three families of access rules - sort the examples.",
        ["Channel partitioning", "Taking turns", "Random access"],
        [("TDMA, FDMA, CDMA", 0),
         ("wasteful for bursty traffic", 0),
         ("a circulating token", 1),
         ("a polling controller", 1),
         ("CSMA/CD on classic Ethernet", 2),
         ("CSMA/CA on Wi-Fi", 2)]),
    "10-mac": input_task(
        "MAC anatomy",
        "The hardware address, by the numbers.",
        [("Bits in a MAC address:", ["48"]),
         ("Bytes of the manufacturer's OUI prefix:", ["3", "three"], "3"),
         ("The broadcast MAC address:",
          ["ff:ff:ff:ff:ff:ff", "ff-ff-ff-ff-ff-ff", "ffffffffffff"],
          "FF:FF:FF:FF:FF:FF")]),
    "10-checks": order_task(
        "Catching corrupted bits",
        "Order the error checks from weakest to strongest.",
        ["Parity bit - one extra bit, catches a single flip",
         "Checksum - a sum over the data, as UDP and TCP use",
         "CRC - the polynomial code in the Ethernet trailer"],
        done="Detection below, recovery above - TCP rebuilds reliability."),

    # ── Chapter 11 ───────────────────────────────────────────────────────
    "11-journey": order_task(
        "One click, whole course",
        "Put the five stages of a page load in order - if you can narrate "
        "this unaided, you are ready.",
        ["DNS resolves the name to an IP address",
         "TCP opens a reliable connection",
         "IP routes the packets, hop by hop",
         "ARP and the link layer carry each frame across each hop",
         "HTTP returns the page and the browser renders it"]),
    "11-layers": sort_task(
        "Keyword to layer",
        "Sort each keyword into the layer where it lives.",
        ["Application", "Transport", "Network", "Link", "Physical"],
        [("HTTP", 0), ("DNS", 0),
         ("port number", 1), ("TCP", 1),
         ("IP address", 2), ("routing", 2),
         ("MAC address", 3), ("ARP", 3),
         ("fibre cable", 4), ("radio signal", 4)]),
    "11-binary": input_task(
        "Block-1 warm-up",
        "The core skill, one more time - place values "
        "128–64–32–16–8–4–2–1.",
        [("0001 1010₂ in decimal:", ["26"]),
         ("45₁₀ in binary:",
          ["101101", "00101101", "10 1101", "0010 1101"], "10 1101")]),
    "11-entropy": input_task(
        "Password entropy",
        "Strength is entropy in bits: log₂(alphabet^length).",
        [("Four random words from a 2000-word list give ≈ … bits:", ["44"]),
         ("Password strength is measured as … in bits:", ["entropy"])],
        done="Length adds entropy faster than exotic symbols."),
    "11-models": sort_task(
        "OSI or TCP/IP?",
        "Two reference models - sort the statements.",
        ["OSI model", "TCP/IP five-layer model"],
        [("seven layers", 0),
         ("the teaching reference", 0),
         ("five layers", 1),
         ("what the internet actually runs", 1)]),
    "11-blocks": sort_task(
        "The revision map",
        "Sort each concept into its revision block.",
        ["Block 1 - data & numbers", "Block 2 - logic & the computer",
         "Blocks 3–5 - networking"],
        [("two's complement", 0), ("UTF-8", 0),
         ("the HIDAS cycle", 1), ("virtual memory", 1),
         ("the three-way handshake", 2), ("ARP", 2), ("CIDR", 2)]),
}


# Per-task reference and short explanation for the solution reveal:
# task id -> (same-page anchor, link label, one-line explanation).
REFS = {
    "01-byte": ("exm-byte3ways", "Example “One byte, three meanings”",
                "The bits never change; the reading convention assigns the meaning."),
    "01-hw-sw": ("sec-01-ipos", "Hardware, software, and the IPOS loop",
                 "Hardware is the physical parts; software is the instructions that run on them."),
    "01-ipos": ("sec-01-ipos", "Hardware, software, and the IPOS loop",
                "Input flows into processing, which produces output, with storage under the loop."),
    "01-milestones": ("sec-01-milestones", "Eighty years in six milestones",
                      "1945, 1971, 1981, 1991, 2007, 2022 - the arc from ENIAC to everyday AI."),
    "01-volatile": ("sec-01-vonneumann", "Inside the machine: Von Neumann",
                    "RAM and everything above it forget at power-off; SSD and HDD persist."),
    "01-units": ("def-bit", "Definition “Bit, byte, word”",
                 "8 bits make a byte, 2⁸ = 256 values; modern machines use 64-bit words."),
    "02-convert": ("sec-02-converting", "Binary numbers: Converting in both directions",
                   "Sum the weights of the 1s one way; subtract powers of two or divide by two the other."),
    "02-twoscomp": ("def-twoscomp", "Definition “Two's complement”",
                    "Invert every bit and add 1; all-ones is therefore −1."),
    "02-nibbles": ("sec-02-hex", "Hexadecimal and octal",
                   "16 = 2⁴, so each hex digit maps cleanly onto four bits."),
    "02-hexdec": ("sec-02-hex", "Hexadecimal and octal",
                  "F3 = 15·16 + 3 = 243; 42 = 2·16 + 10 = 2A."),
    "02-bases": ("sec-02-positional", "Positional number systems",
                 "The prefixes 0b, 0o and 0x mark the base in source code."),
    "02-shift": ("sec-02-arithmetic", "Binary arithmetic and two's complement",
                 "A left shift multiplies by two, a right shift divides by two."),
    "03-compression": ("def-compression", "Definition “Lossless and lossy compression”",
                       "Lossless reconstructs bit for bit; lossy discards what humans miss."),
    "03-magic": ("sec-03-magic", "Text files, binary files, and magic numbers",
                 "Software identifies formats by the first bytes, not the file name."),
    "03-utf8": ("exm-utf8", "Example “Encoding Å by hand”",
                "ASCII stays one byte; Latin letters with diacritics take two; emoji take four."),
    "03-raster-vector": ("sec-03-images", "Images: Pixels or instructions",
                         "Raster stores the pixels; vector stores drawing instructions that scale."),
    "03-format-job": ("sec-03-compression", "Compression",
                      "Crisp text needs lossless; photos hide lossy artefacts; logos must scale; archives must be bit-perfect."),
    "03-nyquist": ("def-nyquist", "Definition “Nyquist's theorem”",
                   "Sample at least twice the highest frequency: 2 × 20 kHz, plus a margin."),
    "04-lamp-and": ("def-gates", "Definition “Logic gates”",
                    "AND outputs 1 only if both inputs are 1."),
    "04-lamp-xor": ("def-gates", "Definition “Logic gates”",
                    "XOR outputs 1 if exactly one input is 1 - the inputs must differ."),
    "04-lamp-nand": ("sec-04-gates", "From the switch to the gate",
                     "NAND is AND followed by NOT - and it alone can build every other gate."),
    "04-bitwise": ("sec-04-gates", "From the switch to the gate",
                   "AND keeps only shared 1s; XOR keeps the positions where the inputs differ."),
    "04-hidas": ("def-hidas", "Definition “The HIDAS cycle”",
                 "Fetch, increment, decode, execute, store - incrementing early lets jumps override the PC."),
    "04-hierarchy": ("sec-04-memaddr", "Memory and addressing",
                     "Registers sit inside the CPU; each level below is larger, slower and cheaper."),
    "04-bus": ("sec-04-memaddr", "Memory and addressing",
               "An N-bit bus reaches 2^N cells: 2¹⁶ = 65 536, and 2³² ≈ 4 GB."),
    "04-components": ("sec-04-vonneumann", "The Von Neumann architecture, properly",
                      "Control unit, ALU, memory, input and output are hardware; the OS is software."),
    "05-states": ("sec-05-processes", "Processes and scheduling",
                  "Running holds a core; ready waits for the scheduler; blocked waits for I/O."),
    "05-scheduling": ("sec-05-processes", "Processes and scheduling",
                      "Round-robin slices time; FCFS queues by arrival; priority runs the important first."),
    "05-boot": ("sec-05-users-view", "The user's view",
                "Firmware starts the boot loader, which loads the kernel, which starts the system."),
    "05-modes": ("sec-05-processes", "Processes and scheduling",
                 "Applications are boxed into user mode; privileged work runs in kernel mode."),
    "05-chmod": ("sec-05-files", "Files and storage",
                 "rwx are three bits: 4 + 2 + 1 = 7; r-x is 4 + 1 = 5 - chmod 755."),
    "05-views": ("def-os", "Definition “Operating system”",
                 "Top-down the OS abstracts; bottom-up it manages and shares resources."),
    "06-units": ("sec-06-encapsulation", "Encapsulation",
                 "Message, segment, datagram, frame - the unit's name tells you the layer."),
    "06-tools": ("sec-06-tools", "Seeing the network",
                 "ping tests reachability, traceroute the path, dig the name, netstat the connections."),
    "06-reach": ("sec-06-internet-web", "The internet and the web",
                 "PAN, LAN, MAN, WAN - classified by reach, and the internet is the largest WAN."),
    "06-delays": ("sec-06-layers", "Layered models",
                  "Processing, queuing, transmission, propagation - queuing grows with load."),
    "06-performance": ("sec-06-layers", "Layered models",
                       "Bandwidth is the pipe's width, throughput what you get, latency the delay - RTT is there and back."),
    "06-history": ("sec-06-internet-web", "The internet and the web",
                   "1969 ARPANET, 1974-83 TCP/IP, 1983 DNS, 1991 the Web, then mobile and cloud."),
    "07-dns": ("exm-dnsresolve", "Example “Resolving a name, step by step”",
               "The resolver walks root, TLD and authoritative server, then caches the answer."),
    "07-records": ("sec-07-dns", "DNS: Names to addresses",
                   "A and AAAA map names to addresses, CNAME aliases, MX names the mail server, NS the name server."),
    "07-url": ("sec-07-http", "The web and HTTP",
               "Scheme, host, port, path, query, fragment - DNS resolves only the host."),
    "07-methods": ("sec-07-http", "The web and HTTP",
                   "GET fetches, POST sends, HEAD asks for headers only, DELETE removes."),
    "07-status": ("sec-07-http", "The web and HTTP",
                  "2xx success, 3xx redirection, 4xx client error, 5xx server error."),
    "07-mail": ("sec-07-email", "E-mail",
                "SMTP pushes towards the recipient; IMAP syncs on the server; POP3 downloads to one client."),
    "08-tcp-udp": ("sec-08-ports", "Transport basics: Ports and sockets",
                   "No loss allowed → TCP; a glitch beats a stall → UDP."),
    "08-ports": ("def-port", "Definition “Port, socket”",
                 "Well-known ports 0-1023 name standard services: 443 HTTPS, 22 SSH, 53 DNS."),
    "08-handshake": ("def-handshake", "Definition “The three-way handshake”",
                     "SYN, SYN+ACK, ACK - sequence numbers exchanged, connection open."),
    "08-headers": ("sec-08-udp", "UDP: The minimal option",
                   "TCP carries the machinery of reliability; UDP is the 8-byte minimum."),
    "08-controls": ("sec-08-congestion", "Congestion, fairness, and QUIC",
                    "Flow control protects the receiver; congestion control protects the network."),
    "08-loss": ("sec-08-relflow", "TCP: Reliability and flow",
                "Three duplicate ACKs signal a missing segment - resend without waiting for the timer."),
    "09-planes": ("def-forwarding", "Definition “Forwarding and routing”",
                  "Forwarding is the per-packet data plane; routing is the background control plane."),
    "09-subnet": ("exm-cidr", "Example “Which network?”",
                  "77 AND 224 = 64, so the network is 192.168.40.64/27 with 2⁵ − 2 = 30 usable hosts."),
    "09-dora": ("sec-09-diag", "Getting an address, and reading the network",
                "Discover, Offer, Request, Acknowledge - the first step must broadcast."),
    "09-private": ("sec-09-ip", "IP addresses",
                   "10.*, 172.16-31.* and 192.168.* are private - routers drop them; the rest route."),
    "09-icmp": ("exm-traceroute", "Example “How traceroute really works”",
                "Echo request is type 8; time exceeded is type 11; TTL 3 expires at the third router."),
    "09-ipv6": ("sec-09-ip", "IP addresses",
                "IPv4 is 32 bits in dotted decimal; IPv6 is 128 bits in hex groups and needs no NAT."),
    "10-boxes": ("sec-10-ethernet", "Ethernet and switches",
                 "Hub repeats blindly; the switch reads MACs and isolates ports; the router reads IPs."),
    "10-access": ("sec-10-sharing", "Sharing the medium",
                  "Partition the channel, take turns, or embrace random access with back-off."),
    "10-addresses": ("sec-10-arp", "Link addresses and ARP",
                     "IP addresses are end-to-end; the MAC pair is renewed on every hop."),
    "10-mac": ("def-mac", "Definition “MAC address”",
               "48 bits: a 3-byte IEEE OUI plus 3 manufacturer bytes; all-ones is broadcast."),
    "10-arp": ("exm-arp", "Example “ARP in action”",
               "Broadcast the question; only the owner answers; cache the mapping; send."),
    "10-checks": ("sec-10-wireless", "Wireless - and the whole journey",
                  "Parity catches one flip, checksums sum the data, the CRC catches almost everything."),
    "11-journey": ("sec-11-block5", "Block 5: The link layer, and the whole journey",
                   "DNS, TCP, IP, ARP + frame, HTTP - the whole course in one click."),
    "11-layers": ("sec-11-block3", "Block 3: The internet and the application layer",
                  "Each keyword lives at exactly one layer of the five-layer stack."),
    "11-binary": ("sec-11-block1", "Block 1: Data and numbers",
                  "Place values 128-64-32-16-8-4-2-1: sum the 1s, or subtract powers of two."),
    "11-entropy": ("sec-11-big-picture", "The big picture - and one closing note",
                   "log₂(2000⁴) ≈ 44 bits - length beats exotic symbols."),
    "11-models": ("sec-11-block3", "Block 3: The internet and the application layer",
                  "OSI's seven layers are the teaching reference; the internet runs the five-layer TCP/IP stack."),
    "11-blocks": ("sec-11-repetition", "Repetition",
                  "Blocks 1-2 cover data and the machine; blocks 3-5 cover the network stack."),
}


def main():
    import html as _html
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.qmd"):
        old.unlink()
    missing = [n for n in TASKS if n not in REFS]
    assert not missing, f"tasks without REFS entry: {missing}"
    for name, cfg in TASKS.items():
        anchor, label, explain = REFS[name]
        sol = _html.escape(cfg.pop("_sol"))
        sol += "\n" + _html.escape(explain)
        sol += f'\nSee: <a href="#{anchor}">{_html.escape(label)}</a>.'
        cfg["sol"] = b64(sol)
        payload = json.dumps(cfg, ensure_ascii=False, indent=1)
        snippet = (
            "```{=html}\n"
            '<div class="tk-task">\n'
            '<script type="application/json">\n'
            f"{payload}\n"
            "</script>\n"
            "</div>\n"
            "```\n"
        )
        (OUT / f"{name}.qmd").write_text(snippet)
    print(f"wrote {len(TASKS)} task snippets to {OUT}")
    write_quizzes()




# ── Session quizzes ─────────────────────────────────────────────────────
# One exam-style quiz per session, on its own page under quizzes/.
# Question tuples: (question_html, [options] with the CORRECT one FIRST
# (the engine shuffles), explanation, chapter_nn, anchor, link label).

CHAPTER_FILES = {
    "01": "01-introduction-everything-is-bits",
    "02": "02-binary-hex-twos-complement",
    "03": "03-text-and-multimedia",
    "04": "04-how-the-machine-computes",
    "05": "05-operating-systems",
    "06": "06-the-internet",
    "07": "07-the-application-layer",
    "08": "08-the-transport-layer",
    "09": "09-the-network-layer",
    "10": "10-the-link-layer",
    "11": "11-repetition",
}

QUIZZES = {
    "01": ("Everything is bits", [
        ("What turns data into information?",
         ["A shared convention for reading it",
          "A larger amount of data",
          "Storing it on a disk",
          "Converting it to decimal"],
         "Data are raw symbols; information is data plus a shared rule for reading it.",
         "01", "def-data-info", "Definition “Data and information”"),
        ("The byte <code>01000001</code> read as an ASCII character is:",
         ["A", "a", "Z", "@"],
         "01000001 is 65, and ASCII assigns the letter A to the value 65.",
         "01", "exm-byte3ways", "Example “One byte, three meanings”"),
        ("The stored-program principle says that:",
         ["Instructions and data share the same memory",
          "Programs are wired into the CPU",
          "Data is kept only in registers",
          "Programs cannot be modified once loaded"],
         "A program is data in memory - loading different bits reprograms the same hardware.",
         "01", "def-vonneumann", "Definition “The Von Neumann architecture”"),
        ("How many distinct values can 3 bits represent?",
         ["8", "3", "6", "16"],
         "2³ = 8 - and every additional bit doubles the range.",
         "01", "sec-01-encoding", "Everything is bits: The idea of encoding"),
        ("Which of these is <em>system</em> software?",
         ["The operating system", "A web browser", "A game", "A spreadsheet"],
         "System software manages the hardware and serves other programs; the rest are applications.",
         "01", "sec-01-ipos", "Hardware, software, and the IPOS loop"),
        ("The program counter holds:",
         ["The address of the next instruction",
          "The result of the last addition",
          "The number of running programs",
          "The current screen contents"],
         "The PC keeps the fetch-decode-execute cycle on track - jumps work by changing it.",
         "01", "exm-fde", "Example “The heartbeat”"),
        ("Moore's Law observes that:",
         ["Transistor counts double roughly every two years",
          "Clock speeds double every year",
          "RAM prices halve every month",
          "Every CPU doubles its cores annually"],
         "Gordon Moore's 1965 observation - exponential growth, now slowing as heat and atomic scales bite.",
         "01", "sec-01-milestones", "Eighty years in six milestones"),
        ("“Volatile” memory means:",
         ["Its contents vanish at power-off",
          "It is unreliable and often corrupts data",
          "It cannot be written twice",
          "It explodes under load"],
         "RAM is volatile - which is why unsaved work dies with the power.",
         "01", "sec-01-vonneumann", "Inside the machine: Von Neumann"),
    ]),
    "02": ("Binary, hex and two's complement", [
        ("Why do computers use binary rather than decimal?",
         ["Two voltage states can be told apart reliably",
          "Binary numbers are shorter",
          "Decimal circuits are patented",
          "Programmers prefer it"],
         "Ten states in one voltage range leave no safety margin; two survive noise and heat.",
         "02", "sec-02-why-binary", "Why binary?"),
        ("What is $1011_2$ in decimal?",
         ["11", "9", "13", "7"],
         "8 + 2 + 1 = 11.",
         "02", "sec-02-converting", "Converting in both directions"),
        ("What is $25_{10}$ in binary?",
         ["11001", "10101", "11011", "10011"],
         "16 + 8 + 1 = 25, so 1 1001.",
         "02", "sec-02-converting", "Converting in both directions"),
        ("One hexadecimal digit corresponds to exactly:",
         ["4 bits", "2 bits", "8 bits", "16 bits"],
         "16 = 2⁴ - each hex digit is one nibble.",
         "02", "sec-02-hex", "Hexadecimal and octal"),
        ("What is $\\mathrm{FF}_{16}$ in decimal?",
         ["255", "240", "155", "256"],
         "15·16 + 15 = 255 - the largest value of one byte.",
         "02", "sec-02-hex", "Hexadecimal and octal"),
        ("−1 in 8-bit two's complement is:",
         ["1111 1111", "1000 0001", "1111 1110", "0000 0001"],
         "+1 = 0000 0001; invert to 1111 1110, add 1: 1111 1111.",
         "02", "def-twoscomp", "Definition “Two's complement”"),
        ("Two's complement won over the other schemes mainly because:",
         ["Subtraction becomes just another addition",
          "It stores larger numbers",
          "It has two representations of zero",
          "It needs fewer bits"],
         "A − B is computed as A + (−B), so one adder circuit does both operations.",
         "02", "sec-02-arithmetic", "Binary arithmetic and two's complement"),
        ("In unsigned 8-bit arithmetic, 255 + 1 equals:",
         ["0 - the value wraps around silently",
          "256",
          "An error is raised",
          "−128"],
         "The result exceeds the range and wraps, with no warning - the classic overflow bug.",
         "02", "sec-02-arithmetic", "Binary arithmetic and two's complement"),
    ]),
    "03": ("Text and multimedia", [
        ("ASCII is:",
         ["A 7-bit code with 128 values",
          "A 16-bit code covering all scripts",
          "An image format",
          "A compression method"],
         "7 bits give 2⁷ = 128 values - enough for English only, hence code pages and Unicode.",
         "03", "sec-03-ascii", "Text: From ASCII to code pages"),
        ("The ASCII codes of <code>'a'</code> and <code>'A'</code>:",
         ["Differ by 32 - a single bit",
          "Differ by 1",
          "Are identical",
          "Differ by 100"],
         "'a' = 'A' + 32, so upper and lower case differ in exactly one bit.",
         "03", "sec-03-ascii", "Text: From ASCII to code pages"),
        ("Unicode itself fixes:",
         ["Each character's identity as a code point - not its bytes",
          "Exactly how every character is stored as bytes",
          "The font used to display text",
          "The maximum length of a text file"],
         "One catalogue, several encodings - UTF-8/16/32 turn code points into bytes.",
         "03", "def-unicode", "Definition “Unicode”"),
        ("How many bytes does UTF-8 use for the Norwegian å (U+00E5)?",
         ["2", "1", "3", "4"],
         "Beyond 7 bits, the two-byte pattern 110xxxxx 10xxxxxx applies.",
         "03", "exm-utf8", "Example “Encoding Å by hand”"),
        ("A file's “magic number” is:",
         ["Its first bytes, identifying the format regardless of the name",
          "Its size in bytes",
          "A checksum of its contents",
          "The number of files in the same folder"],
         "Rename a PDF to .jpg and the first bytes still say %PDF- - extension is convention.",
         "03", "sec-03-magic", "Text files, binary files, and magic numbers"),
        ("The best format for a logo that must scale from favicon to billboard:",
         ["SVG", "JPEG", "PNG", "GIF"],
         "Vector graphics store drawing instructions, so they scale without blockiness.",
         "03", "sec-03-images", "Images: Pixels or instructions"),
        ("Lossy compression:",
         ["Discards detail humans do not notice and is never bit-identical",
          "Reconstructs the original bit for bit",
          "Only works on text",
          "Always halves the file size exactly"],
         "That is the JPEG/MP3/H.264 family - 90-99 % savings at the price of invisible artefacts.",
         "03", "def-compression", "Definition “Lossless and lossy compression”"),
        ("CDs sample at 44.1 kHz because:",
         ["Nyquist demands at least twice the 20 kHz hearing limit",
          "It is a round number in binary",
          "Older tape ran at that speed",
          "Higher rates are impossible"],
         "2 × 20 kHz = 40 kHz minimum, plus a small engineering margin.",
         "03", "def-nyquist", "Definition “Nyquist's theorem”"),
    ]),
    "04": ("How the machine computes", [
        ("Which gate outputs 1 only when <em>both</em> inputs are 1?",
         ["AND", "OR", "XOR", "NAND"],
         "AND is the “both” gate - and, chained with XOR, half of a half-adder.",
         "04", "def-gates", "Definition “Logic gates”"),
        ("Which single gate type can build all the others?",
         ["NAND", "AND", "OR", "XOR"],
         "NOT, AND and OR can each be wired from NANDs alone - one building block per chip.",
         "04", "sec-04-gates", "From the switch to the gate"),
        ("A half-adder consists of:",
         ["An XOR gate (sum) and an AND gate (carry)",
          "Two OR gates",
          "A NOT gate and a flip-flop",
          "Eight full adders"],
         "Sum = XOR, carry = AND; the full adder adds a carry-in on top.",
         "04", "exm-adder", "Example “The half-adder and the full adder”"),
        ("The Von Neumann bottleneck is:",
         ["The single bus all instructions and data share",
          "The limited number of registers",
          "The speed of the fan",
          "The size of the screen"],
         "CPU and memory meet on one bus - which the caches exist to relieve.",
         "04", "sec-04-vonneumann", "The Von Neumann architecture, properly"),
        ("In the HIDAS cycle, the PC is incremented <em>before</em> execute because:",
         ["A jump may overwrite the PC during execute",
          "Incrementing later is slower",
          "The PC would otherwise overflow",
          "Decode needs the new value"],
         "Increment first makes “next instruction” the default that a jump may then override.",
         "04", "exm-hidastrace", "Example “Tracing LOAD 256”"),
        ("A little-endian machine stores the 32-bit value <code>0x12345678</code> with:",
         ["78 at the lowest address", "12 at the lowest address",
          "The bytes in random order", "Only the low 16 bits"],
         "Least-significant byte first; network protocols transmit the opposite, big-endian.",
         "04", "exm-endian", "Example “Endianness”"),
        ("Caches achieve 90-99 % hit rates because of:",
         ["Locality - programs reuse the same and nearby data",
          "Their enormous size",
          "Compression of the stored data",
          "Random luck"],
         "Temporal and spatial locality concentrate accesses on a small working set.",
         "04", "sec-04-memaddr", "Memory and addressing"),
        ("Around 2005, clock speeds stopped rising mainly because of:",
         ["Heat", "Marketing", "Software licences", "A transistor shortage"],
         "Rising heat capped the clocks - designers added cores instead.",
         "04", "sec-04-trends", "Performance and trends"),
    ]),
    "05": ("Operating systems", [
        ("The two views of an operating system are:",
         ["Abstraction (top-down) and resource management (bottom-up)",
          "Hardware and firmware",
          "Compiler and interpreter",
          "Client and server"],
         "It makes the machine usable (abstraction) and shareable (resource management).",
         "05", "def-os", "Definition “Operating system”"),
        ("A system call is:",
         ["A program's request to the OS for a privileged service",
          "A phone call between two servers",
          "A CPU instruction that draws a window",
          "An error message"],
         "The CPU switches into kernel mode, the OS does the work and checks permissions.",
         "05", "def-syscall", "Definition “System call”"),
        ("A process is:",
         ["A program in execution, together with its resources",
          "A file on disk",
          "A CPU core",
          "A user account"],
         "The program on disk is passive; the process is that program running.",
         "05", "def-process", "Definition “Process, thread, resource”"),
        ("How does the OS get the CPU back from a running program?",
         ["A hardware timer interrupt fires unconditionally",
          "The program is asked politely",
          "The user presses a key",
          "It waits for the program to finish"],
         "No program is asked - the timer interrupt is wired below anything software can prevent.",
         "05", "sec-05-processes", "Processes and scheduling"),
        ("When a blocked process's disk read completes, the process becomes:",
         ["Ready - it still has to be dispatched",
          "Running immediately",
          "Terminated",
          "A thread"],
         "The interrupt moves it to ready; only the scheduler dispatches it to running.",
         "05", "sec-05-processes", "Processes and scheduling"),
        ("Two threads updating the same counter lose updates. The OS remedy is:",
         ["Locks around the critical section",
          "A faster CPU",
          "More RAM",
          "Restarting the machine"],
         "A race condition - locks let only one thread into the critical section at a time.",
         "05", "sec-05-processes", "Processes and scheduling"),
        ("“Thrashing” means:",
         ["Heavy swapping between RAM and disk dominating the runtime",
          "A virus scanning files",
          "Two programs printing at once",
          "The fan spinning up"],
         "Virtual memory pushed too far - disk is orders of magnitude slower than RAM.",
         "05", "def-virtualmem", "Definition “Virtual memory”"),
        ("In <code>chmod 755</code>, the 7 grants the owner:",
         ["Read, write and execute", "Read only", "Write only", "No access"],
         "rwx = 4 + 2 + 1 = 7 - three permission bits as one octal digit.",
         "05", "sec-05-files", "Files and storage"),
    ]),
    "06": ("The Internet", [
        ("The internet is best described as:",
         ["A network of networks cooperating through shared protocols",
          "One big computer",
          "A service owned by one company",
          "Another name for the web"],
         "Independent networks joined together, with no central owner.",
         "06", "def-internet", "Definition “The internet”"),
        ("The internet chose packet switching because data traffic is:",
         ["Bursty", "Steady", "Encrypted", "Small"],
         "Links are shared on demand, so nobody holds idle capacity.",
         "06", "sec-06-internet-web", "The internet and the web"),
        ("The relationship between the internet and the web:",
         ["The web is one service running on the internet",
          "They are the same thing",
          "The internet runs on the web",
          "The web replaced the internet"],
         "The internet is the infrastructure; the web moves pages over HTTP on top of it.",
         "06", "sec-06-internet-web", "The internet and the web"),
        ("A protocol's three classic ingredients are:",
         ["Syntax, semantics and timing",
          "Speed, cost and distance",
          "Copper, fibre and radio",
          "Client, server and router"],
         "The form, the meaning, and the when - get any one wrong and communication breaks.",
         "06", "def-protocol", "Definition “Protocol”"),
        ("The five layers, top to bottom, are:",
         ["Application, transport, network, link, physical",
          "Physical, link, network, transport, application",
          "Application, network, transport, physical, link",
          "Transport, application, network, link, physical"],
         "Each layer serves the one above and converses with its peer opposite.",
         "06", "def-stack", "Definition “The five-layer stack”"),
        ("The data unit at the transport layer is called a:",
         ["Segment", "Message", "Datagram", "Frame"],
         "Message, segment, datagram, frame - the unit's name tells you the layer.",
         "06", "sec-06-encapsulation", "Encapsulation"),
        ("<code>ping</code> reports:",
         ["Whether a host answers, and the round-trip time",
          "The routers along the path",
          "The IP behind a name",
          "Your open connections"],
         "It sends an echo and measures the RTT - the first tool when “the internet is down”.",
         "06", "sec-06-tools", "Seeing the network"),
        ("A satellite link has huge bandwidth but video calls feel sluggish. The culprit:",
         ["Propagation delay - the signal's physical travel time",
          "Too little bandwidth",
          "A broken cable",
          "The video codec"],
         "Latency, not capacity: the trip to a satellite and back approaches half a second.",
         "06", "sec-06-layers", "Layered models"),
    ]),
    "07": ("The application layer", [
        ("The first step of almost every connection is:",
         ["A DNS lookup turning the name into an address",
          "A TCP handshake",
          "An ARP broadcast",
          "An HTTP request"],
         "People remember names; machines route by numbers - DNS bridges the two.",
         "07", "def-dns", "Definition “DNS”"),
        ("How long may a resolver cache a DNS answer?",
         ["As long as the record's TTL allows",
          "Forever",
          "One second",
          "Until the browser closes"],
         "Every record carries a time-to-live - why changed records take a while to “spread”.",
         "07", "exm-dnsresolve", "Example “Resolving a name, step by step”"),
        ("An MX record names:",
         ["The mail server for a domain",
          "An IPv6 address",
          "An alias for another name",
          "The web server's port"],
         "DNS does more than addresses - MX is how e-mail finds the right server.",
         "07", "sec-07-dns", "DNS: Names to addresses"),
        ("HTTP status 404 means:",
         ["The client asked for something the server does not have",
          "The server crashed",
          "The request was redirected",
          "Authentication succeeded"],
         "4xx = client error; 5xx would be the server's fault.",
         "07", "sec-07-http", "The web and HTTP"),
        ("Cookies exist because HTTP is:",
         ["Stateless - each request is independent by default",
          "Encrypted",
          "Slow",
          "Text-based"],
         "The server forgets you between requests; the cookie carries the state back.",
         "07", "sec-07-http", "The web and HTTP"),
        ("HTTPS is:",
         ["Ordinary HTTP carried over a TLS-encrypted connection",
          "A completely different page format",
          "HTTP with compression",
          "A faster DNS"],
         "Same conversation, encrypted transport - port 443 and the padlock.",
         "07", "sec-07-http", "The web and HTTP"),
        ("The division of labour in e-mail:",
         ["SMTP pushes mail towards the recipient; IMAP/POP3 pull it back",
          "IMAP pushes and SMTP pulls",
          "HTTP carries all mail",
          "FTP delivers to the inbox"],
         "Push towards the recipient's server, pull from there to the devices.",
         "07", "sec-07-email", "E-mail"),
        ("SFTP is:",
         ["File transfer over SSH - a different protocol, not “FTP with an S”",
          "FTP with a longer password",
          "A graphical FTP client",
          "FTP over UDP"],
         "Plain FTP sends even your password in the clear; SFTP encrypts end to end.",
         "07", "sec-07-ftp", "File transfer, and the security lesson"),
    ]),
    "08": ("The transport layer", [
        ("The transport layer reaches the right ___ on a host:",
         ["Process, via port numbers",
          "Cable",
          "Router",
          "User"],
         "IP finds the machine; the port finds the program.",
         "08", "sec-08-ports", "Transport basics: Ports and sockets"),
        ("A socket is:",
         ["An IP address plus a port number",
          "A physical plug",
          "A CPU register",
          "A DNS record"],
         "One endpoint of a conversation - a socket pair names a TCP connection.",
         "08", "def-port", "Definition “Port, socket”"),
        ("The UDP header is:",
         ["8 bytes - four small fields",
          "20+ bytes like TCP's",
          "64 bytes",
          "Variable, up to 1500 bytes"],
         "Source port, destination port, length, checksum - the whole point is the small cost.",
         "08", "sec-08-udp", "UDP: The minimal option"),
        ("The three-way handshake runs:",
         ["SYN, SYN+ACK, ACK",
          "ACK, SYN, FIN",
          "HELLO, OK, GO",
          "GET, 200, ACK"],
         "Sequence numbers exchanged, parameters agreed - the connection is open.",
         "08", "def-handshake", "Definition “The three-way handshake”"),
        ("Three duplicate ACKs make the sender:",
         ["Retransmit the missing segment immediately",
          "Close the connection",
          "Wait for the full timeout",
          "Halve the window forever"],
         "Fast retransmit - the ACK pattern reveals the loss sooner than any timer.",
         "08", "sec-08-relflow", "TCP: Reliability and flow"),
        ("Flow control protects:",
         ["The receiver's buffer",
          "The network's shared links",
          "The sender's CPU",
          "The DNS resolver"],
         "It reacts to the advertised window; congestion control protects the network.",
         "08", "sec-08-relflow", "TCP: Reliability and flow"),
        ("TCP reacts to packet loss by:",
         ["Halving its send rate, then climbing again - the sawtooth",
          "Sending faster to compensate",
          "Switching to UDP",
          "Rebooting the router"],
         "Loss signals congestion, so senders back off and re-probe the capacity.",
         "08", "sec-08-congestion", "Congestion, fairness, and QUIC"),
        ("QUIC (the carrier of HTTP/3) is built on:",
         ["UDP", "TCP", "Ethernet", "ICMP"],
         "It rebuilds reliability and congestion control itself, over the leaner UDP.",
         "08", "sec-08-congestion", "Congestion, fairness, and QUIC"),
    ]),
    "09": ("The network layer", [
        ("Forwarding, as opposed to routing, is:",
         ["The per-packet data-plane action inside a router",
          "The background computation of paths",
          "A DNS lookup",
          "An application-layer protocol"],
         "Forwarding moves each packet in nanoseconds; routing fills the tables behind it.",
         "09", "def-forwarding", "Definition “Forwarding and routing”"),
        ("How much of the path does a single router know?",
         ["Only the next hop towards the destination",
          "The complete path",
          "The last three hops",
          "Nothing at all"],
         "Each forwarding table names only the next hop - and that is enough.",
         "09", "sec-09-routing", "Routing packets, hop by hop"),
        ("The TTL field:",
         ["Drops by one per router; the packet is discarded at zero",
          "Counts the packet's bytes",
          "Encrypts the payload",
          "Names the destination port"],
         "A loop safeguard - and, deliberately expired, the trick behind traceroute.",
         "09", "sec-09-routing", "Routing packets, hop by hop"),
        ("An IPv4 address is:",
         ["32 bits, written as four decimal bytes",
          "48 bits, written in hex",
          "128 bits, written in hex groups",
          "64 bits, written in octal"],
         "Four octets of 0-255 - which is why an octet stops at 255: it is one byte.",
         "09", "def-ipv4", "Definition “IPv4 address”"),
        ("Addresses like <code>192.168.1.7</code> are:",
         ["Private - used inside a LAN, not routable on the internet",
          "Reserved for governments",
          "IPv6 addresses",
          "Broadcast addresses"],
         "Routers drop them; NAT is what lets such devices reach the world.",
         "09", "sec-09-ip", "IP addresses"),
        ("A /24 network has how many usable host addresses?",
         ["254", "256", "255", "128"],
         "2⁸ = 256 addresses minus the network and broadcast addresses.",
         "09", "sec-09-cidr", "Subnets and CIDR"),
        ("DHCP's first step is a broadcast because:",
         ["The client has no IP address yet and cannot address anyone",
          "Broadcasts are faster",
          "The server's name is secret",
          "It is more secure"],
         "Discover, Offer, Request, Acknowledge - and Discover must shout to the whole LAN.",
         "09", "sec-09-diag", "Getting an address, and reading the network"),
        ("<code>traceroute</code> discovers routers by:",
         ["Sending packets whose TTL expires on purpose, one hop at a time",
          "Asking each router politely",
          "Reading a global map",
          "Scanning all ports"],
         "Each expiry returns ICMP “time exceeded” - revealing that router's address.",
         "09", "exm-traceroute", "Example “How traceroute really works”"),
    ]),
    "10": ("The link layer", [
        ("The scope of a MAC address is:",
         ["One local link only",
          "The whole internet",
          "One country",
          "One ISP"],
         "Flat and local - unlike the hierarchical, end-to-end IP address.",
         "10", "def-mac", "Definition “MAC address”"),
        ("Over a four-link path, the packet's IP addresses change:",
         ["Never - while the MAC pair changes on every hop",
          "On every hop",
          "Twice",
          "Once, at the middle router"],
         "IP is end-to-end; the frame's MAC pair is renewed link by link.",
         "10", "sec-10-arp", "Link addresses and ARP"),
        ("ARP answers the question:",
         ["Which MAC address belongs to this neighbour's IP?",
          "Which IP belongs to this domain name?",
          "Which port is open on this server?",
          "Which route leads to this network?"],
         "Broadcast the question; only the owner replies; cache the answer.",
         "10", "def-arp", "Definition “ARP”"),
        ("Wi-Fi uses collision <em>avoidance</em> (CSMA/CA) because:",
         ["A radio cannot listen while it transmits",
          "Wi-Fi is faster than Ethernet",
          "The air has no capacity limit",
          "Access points forbid collisions"],
         "It cannot detect its own collisions, so it must avoid them - sense, back off, send.",
         "10", "sec-10-wireless", "Wireless - and the whole journey"),
        ("A switch differs from a hub in that it:",
         ["Forwards each frame only to the destination's port",
          "Repeats every bit to all ports",
          "Works at the network layer",
          "Requires no power"],
         "Each port becomes its own collision domain - everyone can send at once.",
         "10", "sec-10-ethernet", "Ethernet and switches"),
        ("A switch fills its MAC table by:",
         ["Reading the source address of every arriving frame",
          "Downloading it from the router",
          "Manual configuration",
          "Asking DNS"],
         "Self-learning: unknown destinations are flooded once, then learned from the reply.",
         "10", "exm-switch", "Example “Switch self-learning”"),
        ("A router operates at the ___ layer and reads ___:",
         ["Network layer - IP addresses",
          "Link layer - MAC addresses",
          "Physical layer - nothing",
          "Application layer - URLs"],
         "Hub: physical, reads nothing. Switch: link, MACs. Router: network, IPs.",
         "10", "sec-10-ethernet", "Ethernet and switches"),
        ("Ethernet's CRC trailer:",
         ["Detects corrupted frames so they can be dropped early",
          "Retransmits lost frames",
          "Encrypts the payload",
          "Compresses the frame"],
         "Detection below, recovery above - reliability is rebuilt by TCP.",
         "10", "sec-10-wireless", "Wireless - and the whole journey"),
    ]),
    "11": ("Repetition - the whole course", [
        ("Loading a page runs, in order:",
         ["DNS, TCP, IP routing, ARP + frames, HTTP",
          "HTTP, TCP, DNS, ARP, IP",
          "ARP, DNS, HTTP, TCP, IP",
          "TCP, DNS, IP, HTTP, ARP"],
         "Resolve the name, open the connection, route, cross each hop, render the page.",
         "11", "sec-11-block5", "Block 5: The link layer, and the whole journey"),
        ("Port numbers live at the ___ layer:",
         ["Transport", "Network", "Link", "Physical"],
         "Ports name processes - IP plus port is a socket.",
         "11", "sec-11-block4", "Block 4: Transport and network"),
        ("Which gate outputs 1 only when its two inputs differ?",
         ["XOR", "AND", "OR", "NAND"],
         "1 for 01 and 10, 0 for 00 and 11.",
         "11", "sec-11-block2", "Block 2: Logic and the computer"),
        ("What is $0001\\,1010_2$ in decimal?",
         ["26", "24", "28", "32"],
         "16 + 8 + 2 = 26.",
         "11", "sec-11-block1", "Block 1: Data and numbers"),
        ("ARP is used to find a node's ___ when you know its ___:",
         ["MAC / IP", "IP / MAC", "port / IP", "name / IP"],
         "ARP maps a known IP to the matching hardware MAC on the local link.",
         "11", "sec-11-block5", "Block 5: The link layer, and the whole journey"),
        ("Which transport protocol is connectionless and best for live video?",
         ["UDP", "TCP", "IP", "ARP"],
         "No handshake, tolerates loss - a glitch beats a stall.",
         "11", "sec-11-block4", "Block 4: Transport and network"),
        ("NAT keeps replies to different inside devices apart using:",
         ["A translation table keyed by ports",
          "Different cables",
          "The devices' MAC addresses",
          "Random guessing"],
         "Each inside socket maps to its own public port; replies are rewritten back.",
         "11", "sec-11-block4", "Block 4: Transport and network"),
        ("The strongest password below, by entropy:",
         ["Four random words from a large list",
          "P@ss1",
          "Your birthday backwards",
          "The word “password” with a 9"],
         "Length adds entropy faster than exotic symbols - log₂(2000⁴) ≈ 44 bits.",
         "11", "sec-11-big-picture", "The big picture - and one closing note"),
    ]),
}


def write_quizzes():
    import html as _html
    qdir = Path(__file__).resolve().parent.parent / "quizzes"
    qdir.mkdir(exist_ok=True)
    for old in qdir.glob("quiz-*.qmd"):
        old.unlink()
    for nn, (title, questions) in QUIZZES.items():
        qs = []
        seen_correct = set()
        for i, (q, options, expl, ch, anchor, label) in enumerate(questions):
            correct = options[0]
            assert norm(correct) not in seen_correct or True
            key = [djb2(f"{norm(correct)}|q{i}")]
            href = f"../chapters/{CHAPTER_FILES[ch]}.html#{anchor}"
            sol = (_html.escape(expl) +
                   f'\nSee: <a href="{href}">{_html.escape(label)}</a>.')
            qs.append({"q": q, "options": options, "key": key,
                       "sol": b64(sol)})
        cfg = {"type": "quiz", "title": f"Quiz {int(nn)}", "questions": qs}
        payload = json.dumps(cfg, ensure_ascii=False, indent=1)
        page = (
            f"# Quiz {int(nn)} - {title} {{.unnumbered}}\n\n"
            f"Eight questions on Session {int(nn)}, in the exam's own format:\n"
            "Four options, exactly one correct. As in the exam, there is no\n"
            "penalty for guessing - answer everything, then grade. Wrong\n"
            "answers get an explanation and a link into the script.\n\n"
            "```{=html}\n"
            '<div class="tk-task">\n'
            '<script type="application/json">\n'
            f"{payload}\n"
            "</script>\n"
            "</div>\n"
            "```\n"
        )
        (qdir / f"quiz-{nn}.qmd").write_text(page)
    # landing page for the "Session quizzes" part, so the sidebar entry
    # is a real link rather than a collapse-only toggle
    rows = "\n".join(
        f"* [Quiz {int(nn)} - {title}](quiz-{nn}.qmd)"
        for nn, (title, _) in QUIZZES.items())
    (qdir / "index.qmd").write_text(
        "# Session quizzes {.unnumbered}\n\n"
        "One quiz per session, in the exam's own format: Eight questions,\n"
        "four options each, exactly one correct. Graded in your browser -\n"
        "nothing is recorded - with explanations and links back into the\n"
        "script. As in the exam, there is no penalty for guessing: Answer\n"
        "everything.\n\n" + rows + "\n")
    print(f"wrote {len(QUIZZES)} quiz pages + index to {qdir}")

if __name__ == "__main__":
    main()
