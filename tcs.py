import logging.config
import logging.handlers

logging.config.fileConfig('stack.conf')
logger = logging.getLogger('Stack')

# Windows版本需要安装库：
# pip install win_inet_pton
# pip install hexdump
import argparse
import os
import platform
import pprint
import random
import signal
import socket
import struct
import time
import sys
from pathlib import Path
import uiautomator2 as u2

import frida

try:
    if os.name == 'nt':
        import win_inet_pton
except ImportError:
    # win_inet_pton import error
    pass

try:
    import hexdump  # pylint: disable=g-import-not-at-top
except ImportError:
    pass

ssl_sessions = {}

def ssl_log(process, pcap=None, host=False, verbose=True, isUsb=True, ssllib="", isSpawn=True, wait=0):
    logger.debug("entering ssl_log...")
    logger.debug("r0capture pid: %s" % os.getpid())
    def log_pcap(pcap_file, ssl_session_id, function, src_addr, src_port,
                 dst_addr, dst_port, data):
        t = time.time()

        if ssl_session_id not in ssl_sessions:
            ssl_sessions[ssl_session_id] = (random.randint(0, 0xFFFFFFFF),
                                            random.randint(0, 0xFFFFFFFF))
        client_sent, server_sent = ssl_sessions[ssl_session_id]

        if function == "SSL_read":
            seq, ack = (server_sent, client_sent)
        else:
            seq, ack = (client_sent, server_sent)

        for writes in (
                # PCAP record (packet) header
                ("=I", int(t)),  # Timestamp seconds
                ("=I", int((t * 1000000) % 1000000)),  # Timestamp microseconds
                ("=I", 40 + len(data)),  # Number of octets saved
                ("=i", 40 + len(data)),  # Actual length of packet
                # IPv4 header
                (">B", 0x45),  # Version and Header Length
                (">B", 0),  # Type of Service
                (">H", 40 + len(data)),  # Total Length
                (">H", 0),  # Identification
                (">H", 0x4000),  # Flags and Fragment Offset
                (">B", 0xFF),  # Time to Live
                (">B", 6),  # Protocol
                (">H", 0),  # Header Checksum
                (">I", src_addr),  # Source Address
                (">I", dst_addr),  # Destination Address
                # TCP header
                (">H", src_port),  # Source Port
                (">H", dst_port),  # Destination Port
                (">I", seq),  # Sequence Number
                (">I", ack),  # Acknowledgment Number
                (">H", 0x5018),  # Header Length and Flags
                (">H", 0xFFFF),  # Window Size
                (">H", 0),  # Checksum
                (">H", 0)):  # Urgent Pointer
            pcap_file.write(struct.pack(writes[0], writes[1]))
        pcap_file.write(data)

        if function == "SSL_read":
            server_sent += len(data)
        else:
            client_sent += len(data)

        ssl_sessions[ssl_session_id] = (client_sent, server_sent)

    def on_message(message, data):
        if message["type"] == "error":
            logger.debug(message)
            os.kill(os.getpid(), signal.SIGTERM)
            return
        if len(data) == 1:
            logger.debug(process)
            logger.debug(message["payload"]["function"])
            logger.debug(message["payload"]["stack"])
            return
        p = message["payload"]        
        if verbose:
            src_addr = socket.inet_ntop(socket.AF_INET,
                                        struct.pack(">I", p["src_addr"]))
            dst_addr = socket.inet_ntop(socket.AF_INET,
                                        struct.pack(">I", p["dst_addr"]))
            logger.debug(process)
            logger.debug("SSL Session: " + p["ssl_session_id"])
            logger.debug("[%s] %s:%d --> %s:%d" % (
                p["function"],
                src_addr,
                p["src_port"],
                dst_addr,
                p["dst_port"]))
            logger.debug(p["stack"])
        if pcap:
            log_pcap(pcap_file, p["ssl_session_id"], p["function"], p["src_addr"],
                     p["src_port"], p["dst_addr"], p["dst_port"], data)

    if isUsb:
        try:
            device = frida.get_usb_device()
        except:
            device = frida.get_remote_device()
    else:
        if host:
            manager = frida.get_device_manager()
            device = manager.add_remote_device(host)
        else:
            device = frida.get_local_device()

    if isSpawn:
        pid = device.spawn([process])
        time.sleep(1)
        session = device.attach(pid)
        time.sleep(1)
        device.resume(pid)
    else:
        logger.debug("attaching the process: %s", process)
        session = device.attach(process)
    if wait > 0:
        logger.debug("wait for {} seconds".format(wait))
        time.sleep(wait)

    if pcap:
        pcap_file = open(pcap, "wb", 0)
        for writes in (
                ("=I", 0xa1b2c3d4),
                ("=H", 2),
                ("=H", 4),
                ("=i", time.timezone),
                ("=I", 0),
                ("=I", 65535),
                ("=I", 228)):
            pcap_file.write(struct.pack(writes[0], writes[1]))

    with open(Path(__file__).resolve().parent.joinpath("./hook.js"), encoding="utf-8") as f:
       hook_script = f.read()

    script = session.create_script(hook_script)
    script.on("message", on_message)
    script.load()

    if ssllib != "":
        script.exports.setssllib(ssllib)

    def stoplog(signum, frame):
        logger.debug('received signal %s', signum)
        logger.debug('stop logging...')

        if pcap:
            pcap_file.flush()
            logger.debug("pcap_file flushed")
            pcap_file.close()
            logger.debug("pcap_file closed")

        session.detach()
        logger.debug('session.detached')
        #session.on('detached', print('detached successful'))
        os._exit(0)

    signal.signal(signal.SIGINT, stoplog)
    signal.signal(signal.SIGTERM, stoplog)
    #signal.signal(signal.SIGALRM, stoplog)
    #signal.signal(signal.CTRL_C_EVENT, stoplog)

    #logger.debug("set alarm 60s")
    #signal.alarm(60)

    sys.stdin.read()

if __name__ == "__main__":
    class ArgParser(argparse.ArgumentParser):

        def error(self, message):
            print("Modified by BigFaceCat")
            print("Error: " + message)
            print()
            print(self.format_help().replace("usage:", "Usage:"))
            self.exit(0)


    parser = ArgParser(
        add_help=False,
        description="Decrypts and logs a process's SSL traffic and HTTP traffic.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
    %(prog)s -pcap ssl.pcap openssl
    %(prog)s -verbose 31337
    %(prog)s -pcap log.pcap -verbose wget
    %(prog)s -pcap log.pcap -ssl "*libssl.so*" com.bigfacecat.testdemo
""")

    args = parser.add_argument_group("Arguments")
    args.add_argument("-pcap", '-p', metavar="<path>", required=False,
                      help="Name of PCAP file to write")
    args.add_argument("-host", '-H', metavar="<192.168.1.1:27042>", required=False,
                      help="connect to remote frida-server on HOST")
    args.add_argument("-verbose", "-v",  required=False, action="store_const", default=True,
                      const=True, help="Show verbose output")
    args.add_argument("process", metavar="<process name | process id>",
                      help="Process whose SSL calls to log")
    args.add_argument("-ssl", default="", metavar="<lib>",
                      help="SSL library to hook")
    args.add_argument("--isUsb", "-U", default=True, action="store_true",
                      help="connect to USB device")
    args.add_argument("--isSpawn", "-f", default=True, action="store_true",
                      help="if spawned app")
    args.add_argument("-wait", "-w", type=int, metavar="<seconds>", default=0,
                      help="Time to wait for the process")

    parsed = parser.parse_args()
    ssl_log(
        int(parsed.process) if parsed.process.isdigit() else parsed.process, 
    parsed.pcap, 
    parsed.host,
    parsed.verbose, 
    isUsb=parsed.isUsb, 
    isSpawn=parsed.isSpawn, 
    ssllib=parsed.ssl, 
    wait=parsed.wait
    )
