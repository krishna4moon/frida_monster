import subprocess
import time
import sys
import os
import platform
import json
import tempfile
import shutil
import requests
from pathlib import Path
from threading import Thread
import signal
import re

class Colors:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    P = '\033[95m'
    C = '\033[96m'
    W = '\033[97m'
    N = '\033[0m'
    BD = '\033[1m'

def logo():
    krishna_art = f"""
{Colors.C}{Colors.BD}
╔══════════════════════════════════════════════════════════════╗
║                    🕉️  KRISHNA TOOLS 🕉️                      ║
║              Automated Frida Installer for Android           ║
╚══════════════════════════════════════════════════════════════╝{Colors.N}
{Colors.G}
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░  जय श्री कृष्णा  ░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
{Colors.N}
"""
    print(krishna_art)

class FridaInstaller:
    def __init__(self):
        self.arch = None
        self.version = None
        self.device_id = None
        self.has_root = False
        self.pc_version = None
        self.temp_dir = tempfile.mkdtemp()
        signal.signal(signal.SIGINT, self.shutdown)
        self.required_packages = ['requests', 'lzma']
    
    def shutdown(self, sig, frame):
        print(f"\n{Colors.R}[!] Interrupted{Colors.N}")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        sys.exit(0)
    
    def cmd(self, cmd, shell=True, timeout=30):
        try:
            r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
            return r
        except:
            return None
    
    def adb(self, args, desc=""):
        if desc:
            print(f"{Colors.Y}[*] {desc}...{Colors.N}")
        r = self.cmd(f"adb {args}")
        if r and r.returncode != 0 and desc:
            print(f"{Colors.R}[!] Failed: {r.stderr[:100]}{Colors.N}")
        return r
    
    def install_package(self, package):
        print(f"{Colors.Y}[*] Installing {package}...{Colors.N}")
        pip = "pip" if platform.system() == "Windows" else "pip3"
        
        try:
            r = self.cmd(f"{pip} install {package} -q")
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] {package} installed{Colors.N}")
                return True
            else:
                r = self.cmd(f"python -m pip install {package} -q")
                if r and r.returncode == 0:
                    print(f"{Colors.G}[✓] {package} installed{Colors.N}")
                    return True
        except:
            pass
        
        print(f"{Colors.R}[✗] Failed to install {package}{Colors.N}")
        return False
    
    def check_package(self, package):
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    def check_all_packages(self):
        print(f"{Colors.BD}\n╔════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.BD}║     CHECKING REQUIRED PACKAGES             ║{Colors.N}")
        print(f"{Colors.BD}╚════════════════════════════════════════════╝{Colors.N}")
        
        missing = []
        
        for package in self.required_packages:
            if self.check_package(package):
                print(f"{Colors.G}[✓] {package}{Colors.N}")
            else:
                print(f"{Colors.R}[✗] {package}{Colors.N}")
                missing.append(package)
        
        if not missing:
            print(f"{Colors.G}\n[✓] All packages available{Colors.N}")
            return True
        
        print(f"{Colors.Y}\n[*] Installing missing packages...{Colors.N}")
        for package in missing:
            if not self.install_package(package):
                if package == 'lzma':
                    print(f"{Colors.Y}[!] lzma may be built-in in Python 3.3+{Colors.N}")
                else:
                    print(f"{Colors.R}[✗] Could not install {package}{Colors.N}")
                    return False
        
        for package in missing:
            if not self.check_package(package) and package != 'lzma':
                print(f"{Colors.R}[✗] {package} still missing{Colors.N}")
                return False
        
        print(f"{Colors.G}\n[✓] All packages ready{Colors.N}")
        return True
    
    def check_pc_frida(self):
        print(f"{Colors.Y}[*] Checking PC Frida installation...{Colors.N}")
        
        r = self.cmd("frida --version 2>/dev/null")
        if r and r.returncode == 0 and r.stdout.strip():
            self.pc_version = r.stdout.strip()
            print(f"{Colors.G}[✓] PC Frida version: {self.pc_version}{Colors.N}")
            return True
        
        r = self.cmd("frida --version", shell=True)
        if r and r.returncode == 0 and r.stdout.strip():
            self.pc_version = r.stdout.strip()
            print(f"{Colors.G}[✓] PC Frida version: {self.pc_version}{Colors.N}")
            return True
        
        print(f"{Colors.Y}[!] No PC Frida found{Colors.N}")
        return False
    
    def check_adb(self):
        r = self.cmd("adb version")
        if not r or r.returncode != 0:
            print(f"{Colors.R}[✗] ADB not found{Colors.N}")
            print(f"{Colors.Y}[*] Please install Android Platform Tools{Colors.N}")
            return False
        print(f"{Colors.G}[✓] ADB ready{Colors.N}")
        return True
    
    def get_device(self):
        r = self.adb("devices", "Scanning devices")
        if not r:
            return False
        
        lines = r.stdout.strip().split('\n')[1:]
        for line in lines:
            if 'device' in line and 'unauthorized' not in line:
                self.device_id = line.split('\t')[0]
                print(f"{Colors.G}[✓] Device: {self.device_id}{Colors.N}")
                return True
        
        print(f"{Colors.R}[✗] No device{Colors.N}")
        return False
    
    def check_root(self):
        r = self.cmd(f"adb -s {self.device_id} shell 'su -c \"id -u\"' 2>/dev/null")
        if r and r.stdout.strip() == '0':
            self.has_root = True
            print(f"{Colors.G}[✓] Root access{Colors.N}")
        else:
            print(f"{Colors.Y}[!] No root (limited){Colors.N}")
        return self.has_root
    
    def get_arch(self):
        cmds = [
            f"adb -s {self.device_id} shell getprop ro.product.cpu.abi",
            f"adb -s {self.device_id} shell uname -m"
        ]
        
        for cmd in cmds:
            r = self.cmd(cmd)
            if r and r.stdout:
                out = r.stdout.strip().lower()
                if 'arm64' in out or 'aarch64' in out:
                    self.arch = 'arm64'
                elif 'armv7' in out or 'armeabi' in out:
                    self.arch = 'arm'
                elif 'x86_64' in out:
                    self.arch = 'x86_64'
                elif 'i686' in out or 'x86' in out:
                    self.arch = 'x86'
                if self.arch:
                    print(f"{Colors.G}[✓] Arch: {self.arch}{Colors.N}")
                    return True
        
        self.arch = 'arm64'
        print(f"{Colors.Y}[!] Arch: {self.arch} (default){Colors.N}")
        return True
    
    def get_version_selection(self):
        self.check_pc_frida()
        
        if self.pc_version:
            print(f"\n{Colors.C}╔════════════════════════════════════════╗{Colors.N}")
            print(f"{Colors.C}║  Frida version on PC: {self.pc_version}{' ' * (18 - len(self.pc_version))}║{Colors.N}")
            print(f"{Colors.C}╚════════════════════════════════════════╝{Colors.N}")
            print(f"{Colors.Y}[?] Use this version for Android?{Colors.N}")
            print(f"{Colors.G}  1{Colors.N}. Yes, use PC version ({self.pc_version})")
            print(f"{Colors.G}  2{Colors.N}. No, let me enter version")
            print(f"{Colors.G}  3{Colors.N}. Install latest version")
            print(f"{Colors.G}  4{Colors.N}. Install default version (16.1.11)")
            
            choice = input(f"\n{Colors.C}krishna@tools~# {Colors.N}").strip()
            
            if choice == '1':
                self.version = self.pc_version
                print(f"{Colors.G}[✓] Using PC version: {self.version}{Colors.N}")
                return True
            elif choice == '2':
                ver = input(f"{Colors.C}Enter version (e.g., 16.1.11, 15.2.2): {Colors.N}").strip()
                if ver and re.match(r'^\d+\.\d+\.\d+$', ver):
                    self.version = ver
                    print(f"{Colors.G}[✓] Using: {self.version}{Colors.N}")
                    return True
                else:
                    print(f"{Colors.R}[!] Invalid format. Using default{Colors.N}")
                    self.version = '16.1.11'
                    return True
            elif choice == '3':
                return self.fetch_latest_version()
            else:
                self.version = '16.1.11'
                print(f"{Colors.G}[✓] Using default: {self.version}{Colors.N}")
                return True
        else:
            print(f"\n{Colors.Y}[?] No PC Frida found. Choose version:{Colors.N}")
            print(f"{Colors.G}  1{Colors.N}. Enter version manually")
            print(f"{Colors.G}  2{Colors.N}. Install latest version")
            print(f"{Colors.G}  3{Colors.N}. Install default version (16.1.11)")
            
            choice = input(f"\n{Colors.C}krishna@tools~# {Colors.N}").strip()
            
            if choice == '1':
                ver = input(f"{Colors.C}Enter version (e.g., 16.1.11): {Colors.N}").strip()
                if ver and re.match(r'^\d+\.\d+\.\d+$', ver):
                    self.version = ver
                    print(f"{Colors.G}[✓] Using: {self.version}{Colors.N}")
                else:
                    print(f"{Colors.R}[!] Invalid. Using default{Colors.N}")
                    self.version = '16.1.11'
                return True
            elif choice == '2':
                return self.fetch_latest_version()
            else:
                self.version = '16.1.11'
                print(f"{Colors.G}[✓] Using default: {self.version}{Colors.N}")
                return True
    
    def fetch_latest_version(self):
        print(f"{Colors.Y}[*] Fetching latest version...{Colors.N}")
        try:
            r = requests.get('https://api.github.com/repos/frida/frida/releases/latest', timeout=5)
            if r.status_code == 200:
                self.version = r.json()['tag_name'].lstrip('v')
                print(f"{Colors.G}[✓] Latest: {self.version}{Colors.N}")
                return True
        except:
            pass
        
        self.version = '16.1.11'
        print(f"{Colors.Y}[!] Using default: {self.version}{Colors.N}")
        return True
    
    def list_versions(self):
        print(f"{Colors.Y}[*] Fetching available versions...{Colors.N}")
        try:
            r = requests.get('https://api.github.com/repos/frida/frida/releases?per_page=20', timeout=10)
            if r.status_code == 200:
                releases = r.json()
                print(f"{Colors.G}\n[+] Recent Frida versions:{Colors.N}")
                for i, release in enumerate(releases[:15], 1):
                    ver = release['tag_name'].lstrip('v')
                    print(f"{Colors.C}{i:2}. {ver}{Colors.N}")
                return True
        except:
            print(f"{Colors.R}[!] Failed to fetch versions{Colors.N}")
        return False
    
    def download_server(self):
        arch_map = {
            'arm64': 'android-arm64',
            'arm': 'android-arm',
            'x86_64': 'android-x86_64',
            'x86': 'android-x86'
        }
        
        frida_arch = arch_map.get(self.arch)
        if not frida_arch:
            print(f"{Colors.R}[✗] Bad arch{Colors.N}")
            return None
        
        filename = f"frida-server-{self.version}-{frida_arch}.xz"
        url = f"https://github.com/frida/frida/releases/download/v{self.version}/{filename}"
        output = os.path.join(self.temp_dir, filename)
        
        print(f"{Colors.Y}[*] Downloading {self.version} for {self.arch}...{Colors.N}")
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(output, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = (downloaded / total) * 100
                        sys.stdout.write(f"\r{Colors.C}[+] Progress: {percent:.1f}%{Colors.N}")
                        sys.stdout.flush()
            print(f"\n{Colors.G}[✓] Downloaded{Colors.N}")
            return output
        except Exception as e:
            print(f"\n{Colors.R}[✗] Download failed: {str(e)[:50]}{Colors.N}")
            return None
    
    def extract(self, compressed):
        extracted = compressed.replace('.xz', '')
        print(f"{Colors.Y}[*] Extracting...{Colors.N}")
        
        try:
            import lzma
            with lzma.open(compressed, 'rb') as f_in:
                with open(extracted, 'wb') as f_out:
                    data = f_in.read()
                    f_out.write(data)
            print(f"{Colors.G}[✓] Extracted{Colors.N}")
            return extracted
        except:
            print(f"{Colors.R}[✗] Extract failed{Colors.N}")
            return None
    
    def push(self, local):
        remote = "/data/local/tmp/frida-server"
        print(f"{Colors.Y}[*] Pushing to device...{Colors.N}")
        
        r = self.cmd(f"adb -s {self.device_id} push {local} {remote}")
        if not r or r.returncode != 0:
            print(f"{Colors.R}[✗] Push failed{Colors.N}")
            return False
        
        self.cmd(f"adb -s {self.device_id} shell 'chmod 755 {remote}'")
        print(f"{Colors.G}[✓] Installed to {remote}{Colors.N}")
        return True
    
    def install_host_tools(self):
        print(f"{Colors.Y}[*] Installing/Upgrading PC Frida tools...{Colors.N}")
        pip = "pip" if platform.system() == "Windows" else "pip3"
        
        if self.version:
            print(f"{Colors.Y}[*] Installing frida=={self.version} and frida-tools=={self.version}{Colors.N}")
            r = self.cmd(f"{pip} install frida=={self.version} frida-tools=={self.version} --upgrade -q")
        else:
            r = self.cmd(f"{pip} install --upgrade frida-tools -q")
        
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] PC tools version: {self.version if self.version else 'latest'}{Colors.N}")
            return True
        
        print(f"{Colors.Y}[!] Manual: {pip} install frida-tools{Colors.N}")
        return False
    
    def check_device_frida(self):
        r = self.cmd(f"adb -s {self.device_id} shell 'ls -la /data/local/tmp/frida-server' 2>/dev/null")
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] Device has Frida server installed{Colors.N}")
            return True
        return False
    
    def start_server(self):
        print(f"{Colors.Y}[*] Starting frida-server...{Colors.N}")
        
        r = self.cmd(f"adb -s {self.device_id} shell 'pidof frida-server'")
        if r and r.stdout.strip():
            print(f"{Colors.G}[✓] Already running (PID: {r.stdout.strip()}){Colors.N}")
            return True
        
        if self.has_root:
            self.cmd(f"adb -s {self.device_id} shell 'su -c \"/data/local/tmp/frida-server --daemon\"'")
        else:
            self.cmd(f"adb -s {self.device_id} shell '/data/local/tmp/frida-server --daemon'")
        
        time.sleep(2)
        
        r = self.cmd(f"adb -s {self.device_id} shell 'ps -A | grep frida-server'")
        if r and r.stdout.strip():
            print(f"{Colors.G}[✓] Server running{Colors.N}")
            return True
        
        print(f"{Colors.R}[✗] Start failed{Colors.N}")
        return False
    
    def stop_server(self):
        print(f"{Colors.Y}[*] Stopping frida-server...{Colors.N}")
        self.cmd(f"adb -s {self.device_id} shell 'killall frida-server' 2>/dev/null")
        time.sleep(1)
        print(f"{Colors.G}[✓] Stopped{Colors.N}")
    
    def status(self):
        print(f"{Colors.Y}[*] Frida Status:{Colors.N}")
        
        pc_check = self.cmd("frida --version 2>/dev/null")
        if pc_check and pc_check.stdout.strip():
            print(f"{Colors.G}[✓] PC Frida: {pc_check.stdout.strip()}{Colors.N}")
        else:
            print(f"{Colors.R}[✗] PC Frida: Not installed{Colors.N}")
        
        device_check = self.cmd(f"adb -s {self.device_id} shell 'ls /data/local/tmp/frida-server' 2>/dev/null")
        if device_check and device_check.returncode == 0:
            print(f"{Colors.G}[✓] Device: Frida server present{Colors.N}")
        else:
            print(f"{Colors.R}[✗] Device: No Frida server{Colors.N}")
        
        running = self.cmd(f"adb -s {self.device_id} shell 'pidof frida-server' 2>/dev/null")
        if running and running.stdout.strip():
            print(f"{Colors.G}[✓] Server: Running (PID: {running.stdout.strip()}){Colors.N}")
        else:
            print(f"{Colors.R}[✗] Server: Not running{Colors.N}")
        
        return True
    
    def uninstall(self):
        print(f"{Colors.R}[*] Uninstalling from device...{Colors.N}")
        self.stop_server()
        self.cmd(f"adb -s {self.device_id} shell 'rm -f /data/local/tmp/frida-server'")
        print(f"{Colors.G}[✓] Removed from device{Colors.N}")
        
        confirm = input(f"{Colors.Y}[?] Remove PC Frida tools? (y/N): {Colors.N}")
        if confirm.lower() == 'y':
            pip = "pip" if platform.system() == "Windows" else "pip3"
            self.cmd(f"{pip} uninstall frida frida-tools -y -q")
            print(f"{Colors.G}[✓] PC tools removed{Colors.N}")
    
    def list_apps(self):
        print(f"{Colors.Y}[*] Listing applications via Frida...{Colors.N}")
        r = self.cmd("frida-ps -Uai 2>/dev/null")
        if r and r.stdout:
            lines = r.stdout.strip().split('\n')
            print(f"{Colors.G}[+] Applications:{Colors.N}")
            for i, line in enumerate(lines[:25], 1):
                if 'identifier' in line.lower() or 'name' in line.lower():
                    continue
                print(f"{Colors.C}{i:2}. {line[:80]}{Colors.N}")
        else:
            print(f"{Colors.R}[!] Failed. Is frida-server running?{Colors.N}")
    
    def interactive_shell(self):
        print(f"{Colors.G}[*] Interactive Frida shell (Ctrl+D to exit){Colors.N}")
        os.system("frida -U" if platform.system() != "Windows" else "frida -U")
    
    def full_install(self):
        if not self.check_all_packages():
            print(f"{Colors.R}[✗] Required packages missing{Colors.N}")
            return False
        
        if not self.check_adb():
            return False
        if not self.get_device():
            return False
        
        self.check_root()
        self.get_arch()
        
        device_has_frida = self.check_device_frida()
        if device_has_frida:
            print(f"{Colors.Y}[?] Device already has Frida server{Colors.N}")
            choice = input(f"{Colors.Y}Reinstall? (y/N): {Colors.N}")
            if choice.lower() != 'y':
                print(f"{Colors.G}[✓] Skipping installation{Colors.N}")
                self.start_server()
                return True
        
        if not self.get_version_selection():
            return False
        
        file = self.download_server()
        if not file:
            return False
        
        extracted = self.extract(file)
        if not extracted:
            return False
        
        if not self.push(extracted):
            return False
        
        self.install_host_tools()
        self.start_server()
        
        print(f"{Colors.G}\n╔════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.G}║  ✓ Installation Complete!                  ║{Colors.N}")
        print(f"{Colors.G}║  Version: {self.version}{' ' * (31 - len(self.version))}║{Colors.N}")
        print(f"{Colors.G}╚════════════════════════════════════════════╝{Colors.N}")
        return True
    
    def menu(self):
        while True:
            logo()
            print(f"""
{Colors.BD}╔════════════════════════════════════════════════════════╗
║  {Colors.G}1{Colors.N} . Full Installation (Auto-detect PC version)   {Colors.BD}║
║  {Colors.G}2{Colors.N} . Install Specific Version                    {Colors.BD}║
║  {Colors.G}3{Colors.N} . List Available Versions                     {Colors.BD}║
║  {Colors.G}4{Colors.N} . Start Frida Server                          {Colors.BD}║
║  {Colors.G}5{Colors.N} . Stop Frida Server                           {Colors.BD}║
║  {Colors.G}6{Colors.N} . Check Status (PC + Device)                  {Colors.BD}║
║  {Colors.G}7{Colors.N} . List Applications via Frida                 {Colors.BD}║
║  {Colors.G}8{Colors.N} . Interactive Frida Shell                     {Colors.BD}║
║  {Colors.G}9{Colors.N} . Uninstall Frida                             {Colors.BD}║
║  {Colors.G}0{Colors.N} . Exit                                        {Colors.BD}║
╚════════════════════════════════════════════════════════╝{Colors.N}
            """)
            choice = input(f"{Colors.C}krishna@tools~# {Colors.N}").strip()
            
            if choice == '1':
                if self.full_install():
                    input(f"{Colors.Y}[*] Press Enter{Colors.N}")
                else:
                    input(f"{Colors.R}[*] Failed. Press Enter{Colors.N}")
            
            elif choice == '2':
                if not self.check_all_packages():
                    input(f"{Colors.R}[*] Packages missing. Press Enter{Colors.N}")
                    continue
                
                print(f"{Colors.Y}[*] Enter version (e.g., 16.1.11, 16.0.8){Colors.N}")
                ver = input(f"{Colors.C}version~# {Colors.N}").strip()
                if ver and re.match(r'^\d+\.\d+\.\d+$', ver):
                    self.version = ver
                    if self.check_adb() and self.get_device():
                        self.check_root()
                        self.get_arch()
                        file = self.download_server()
                        if file:
                            extracted = self.extract(file)
                            if extracted and self.push(extracted):
                                self.install_host_tools()
                                self.start_server()
                                print(f"{Colors.G}[✓] Version {self.version} installed{Colors.N}")
                    input(f"{Colors.Y}[*] Press Enter{Colors.N}")
                else:
                    print(f"{Colors.R}[!] Invalid version{Colors.N}")
                    time.sleep(1)
            
            elif choice == '3':
                self.list_versions()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '4':
                if self.get_device():
                    self.start_server()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '5':
                if self.get_device():
                    self.stop_server()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '6':
                if self.get_device():
                    self.status()
                else:
                    self.check_pc_frida()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '7':
                self.list_apps()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '8':
                self.interactive_shell()
            
            elif choice == '9':
                if self.get_device():
                    confirm = input(f"{Colors.R}[!] Confirm uninstall? (y/N): {Colors.N}")
                    if confirm.lower() == 'y':
                        self.uninstall()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '0':
                print(f"{Colors.G}\n[✓] Jay Shri Krishna 🙏{Colors.N}")
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                sys.exit(0)
            
            os.system('cls' if platform.system() == 'Windows' else 'clear')

if __name__ == "__main__":
    installer = FridaInstaller()
    installer.menu()
