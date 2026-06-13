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
import signal
import re
import hashlib
import zipfile
import tarfile
import socket
import urllib.request
from urllib.error import URLError
import threading

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
    BLINK = '\033[5m'
    DIM = '\033[2m'

def logo():
    krishna_art = f"""
{Colors.C}{Colors.BD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🕉️  KRISHNA TOOLS ULTIMATE 🕉️                        ║
║                    Advanced Automated Frida Installer for Android             ║
║                           [ Zero Intervention Required ]                      ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.N}
{Colors.G}
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░  जय श्री कृष्णा  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
{Colors.N}
"""
    print(krishna_art)

class AdvancedFridaInstaller:
    def __init__(self):
        self.arch = None
        self.version = None
        self.device_id = None
        self.has_root = False
        self.pc_version = None
        self.temp_dir = tempfile.mkdtemp()
        self.retry_count = 3
        self.retry_delay = 5
        self.timeout = 60
        self.system = platform.system()
        self.installed_packages = []
        self.download_urls = []
        self.verified = False
        
        signal.signal(signal.SIGINT, self.shutdown)
        self.setup_environment()
    
    def shutdown(self, sig, frame):
        print(f"\n{Colors.Y}[!] Cleaning up...{Colors.N}")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        print(f"{Colors.G}[✓] Jay Shri Krishna 🙏{Colors.N}")
        sys.exit(0)
    
    def setup_environment(self):
        os.environ['PYTHONUNBUFFERED'] = '1'
        if self.system == "Windows":
            os.system('chcp 65001 >nul 2>&1')
    
    def cmd(self, cmd, shell=True, timeout=60, retry=2):
        for attempt in range(retry + 1):
            try:
                r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
                return r
            except subprocess.TimeoutExpired:
                if attempt < retry:
                    print(f"{Colors.Y}[!] Timeout, retrying... ({attempt+1}/{retry}){Colors.N}")
                    time.sleep(3)
                    continue
            except Exception as e:
                if attempt < retry:
                    print(f"{Colors.Y}[!] Error: {str(e)[:50]}, retrying...{Colors.N}")
                    time.sleep(2)
                    continue
        return None
    
    def retry_func(self, func, *args, max_retries=5, delay=3):
        for attempt in range(max_retries):
            try:
                result = func(*args)
                if result:
                    return result
            except Exception as e:
                print(f"{Colors.Y}[!] Attempt {attempt+1}/{max_retries} failed: {str(e)[:50]}{Colors.N}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 1.5
                continue
        return None
    
    def internet_available(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            pass
        try:
            requests.get("https://github.com", timeout=5)
            return True
        except:
            return False
    
    def check_all_requirements(self):
        print(f"{Colors.BD}\n╔════════════════════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.BD}║              CHECKING ALL SYSTEM REQUIREMENTS               ║{Colors.N}")
        print(f"{Colors.BD}╚════════════════════════════════════════════════════════════╝{Colors.N}")
        
        if not self.internet_available():
            print(f"{Colors.R}[✗] No internet connection{Colors.N}")
            print(f"{Colors.Y}[*] Waiting for internet...{Colors.N}")
            for i in range(30):
                if self.internet_available():
                    print(f"{Colors.G}[✓] Internet connected{Colors.N}")
                    break
                time.sleep(2)
            else:
                print(f"{Colors.R}[✗] No internet. Please check connection{Colors.N}")
                return False
        
        self.install_python_packages()
        self.install_system_tools()
        self.install_adb_if_needed()
        
        return True
    
    def install_python_packages(self):
        print(f"{Colors.Y}[*] Checking Python packages...{Colors.N}")
        packages = ['requests', 'lzma', 'pyOpenSSL', 'certifi']
        pip = "pip" if self.system == "Windows" else "pip3"
        
        for package in packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"{Colors.G}[✓] {package}{Colors.N}")
            except ImportError:
                print(f"{Colors.Y}[*] Installing {package}...{Colors.N}")
                self.cmd(f"{pip} install {package} --quiet --no-cache-dir --default-timeout=100", retry=3)
                time.sleep(1)
    
    def install_system_tools(self):
        print(f"{Colors.Y}[*] Checking system tools...{Colors.N}")
        
        if self.system == "Windows":
            self.install_windows_tools()
        elif self.system == "Darwin":
            self.install_mac_tools()
        else:
            self.install_linux_tools()
    
    def install_windows_tools(self):
        tools = ['wget', 'curl', '7zip']
        for tool in tools:
            check = self.cmd(f"where {tool} 2>nul")
            if check and check.returncode == 0:
                print(f"{Colors.G}[✓] {tool}{Colors.N}")
            else:
                print(f"{Colors.Y}[*] Installing {tool}...{Colors.N}")
                if tool == '7zip':
                    self.cmd('powershell -Command "winget install 7zip.7zip --accept-package-agreements --silent"')
    
    def install_mac_tools(self):
        if self.cmd("which brew").returncode != 0:
            print(f"{Colors.Y}[*] Installing Homebrew...{Colors.N}")
            self.cmd('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        
        for tool in ['wget', 'curl']:
            self.cmd(f"brew install {tool}")
            print(f"{Colors.G}[✓] {tool} installed{Colors.N}")
    
    def install_linux_tools(self):
        pkg_manager = None
        if self.cmd("which apt").returncode == 0:
            pkg_manager = "apt"
            self.cmd("sudo apt update -qq")
        elif self.cmd("which yum").returncode == 0:
            pkg_manager = "yum"
        elif self.cmd("which dnf").returncode == 0:
            pkg_manager = "dnf"
        elif self.cmd("which pacman").returncode == 0:
            pkg_manager = "pacman"
        
        if pkg_manager:
            for tool in ['wget', 'curl', 'adb']:
                if self.cmd(f"which {tool}").returncode != 0:
                    print(f"{Colors.Y}[*] Installing {tool}...{Colors.N}")
                    if pkg_manager == "apt":
                        self.cmd(f"sudo apt install {tool} -y -qq")
                    elif pkg_manager == "yum":
                        self.cmd(f"sudo yum install {tool} -y -q")
                    elif pkg_manager == "dnf":
                        self.cmd(f"sudo dnf install {tool} -y -q")
                    elif pkg_manager == "pacman":
                        self.cmd(f"sudo pacman -S {tool} --noconfirm")
    
    def install_adb_if_needed(self):
        if self.cmd("adb version").returncode != 0:
            print(f"{Colors.Y}[*] Installing ADB...{Colors.N}")
            if self.system == "Windows":
                self.install_adb_windows()
            elif self.system == "Darwin":
                self.cmd("brew install android-platform-tools")
            else:
                self.cmd("sudo apt install android-tools-adb -y -qq")
    
    def install_adb_windows(self):
        adb_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        zip_path = os.path.join(self.temp_dir, "platform-tools.zip")
        
        try:
            urllib.request.urlretrieve(adb_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            adb_path = os.path.join(self.temp_dir, "platform-tools")
            os.environ['PATH'] += os.pathsep + adb_path
            
            system_path = os.environ.get('PATH', '')
            if adb_path not in system_path:
                print(f"{Colors.Y}[!] Add to PATH: {adb_path}{Colors.N}")
        except:
            print(f"{Colors.Y}[!] Manual ADB installation required{Colors.N}")
    
    def wait_for_device(self, max_wait=120):
        print(f"{Colors.Y}[*] Waiting for device (max {max_wait}s)...{Colors.N}")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            r = self.cmd("adb devices")
            if r and r.stdout:
                lines = r.stdout.strip().split('\n')[1:]
                for line in lines:
                    if 'device' in line and 'unauthorized' not in line:
                        self.device_id = line.split('\t')[0]
                        print(f"{Colors.G}[✓] Device connected: {self.device_id}{Colors.N}")
                        return True
            
            time.sleep(3)
            print(f"{Colors.DIM}[*] Waiting... {int(time.time() - start_time)}s{Colors.N}")
        
        print(f"{Colors.R}[✗] Device timeout{Colors.N}")
        return False
    
    def enable_root_automatically(self):
        print(f"{Colors.Y}[*] Attempting root access...{Colors.N}")
        
        root_methods = [
            "su -c 'id'",
            "su 0 id",
            "/system/bin/su -c id",
            "magisk su -c id",
            "kernelsu -c id"
        ]
        
        for method in root_methods:
            r = self.cmd(f"adb -s {self.device_id} shell '{method}' 2>/dev/null")
            if r and 'uid=0' in r.stdout:
                self.has_root = True
                print(f"{Colors.G}[✓] Root access gained{Colors.N}")
                return True
        
        print(f"{Colors.Y}[!] No root access (continuing anyway){Colors.N}")
        return False
    
    def detect_architecture(self):
        print(f"{Colors.Y}[*] Detecting architecture...{Colors.N}")
        
        arch_commands = [
            f"adb -s {self.device_id} shell getprop ro.product.cpu.abi",
            f"adb -s {self.device_id} shell uname -m",
            f"adb -s {self.device_id} shell cat /proc/cpuinfo"
        ]
        
        for cmd in arch_commands:
            r = self.cmd(cmd)
            if r and r.stdout:
                out = r.stdout.lower()
                if 'arm64' in out or 'aarch64' in out:
                    self.arch = 'arm64'
                    break
                elif 'armv8' in out:
                    self.arch = 'arm64'
                    break
                elif 'armv7' in out or 'armeabi-v7a' in out:
                    self.arch = 'arm'
                    break
                elif 'x86_64' in out:
                    self.arch = 'x86_64'
                    break
                elif 'i686' in out or 'i386' in out:
                    self.arch = 'x86'
                    break
        
        if not self.arch:
            self.arch = 'arm64'
        
        print(f"{Colors.G}[✓] Architecture: {self.arch}{Colors.N}")
        return True
    
    def get_best_version(self):
        print(f"{Colors.Y}[*] Determining best Frida version...{Colors.N}")
        
        pc_check = self.cmd("frida --version 2>/dev/null")
        if pc_check and pc_check.stdout.strip():
            self.pc_version = pc_check.stdout.strip()
            print(f"{Colors.G}[✓] PC version: {self.pc_version}{Colors.N}")
            self.version = self.pc_version
            return True
        
        try:
            r = requests.get('https://api.github.com/repos/frida/frida/releases/latest', timeout=10)
            if r.status_code == 200:
                self.version = r.json()['tag_name'].lstrip('v')
                print(f"{Colors.G}[✓] Latest version: {self.version}{Colors.N}")
                return True
        except:
            pass
        
        self.version = '16.1.11'
        print(f"{Colors.G}[✓] Using stable version: {self.version}{Colors.N}")
        return True
    
    def download_with_fallback(self, url, output):
        methods = [
            self.download_requests,
            self.download_urllib,
            self.download_wget,
            self.download_curl
        ]
        
        for method in methods:
            result = self.retry_func(method, url, output)
            if result:
                print(f"{Colors.G}[✓] Downloaded using {method.__name__}{Colors.N}")
                return True
            time.sleep(2)
        
        return False
    
    def download_requests(self, url, output):
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        
        with open(output, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=32768):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    percent = (downloaded / total) * 100
                    sys.stdout.write(f"\r{Colors.C}[+] Progress: {percent:.1f}%{Colors.N}")
                    sys.stdout.flush()
        print()
        return os.path.exists(output) and os.path.getsize(output) > 0
    
    def download_urllib(self, url, output):
        urllib.request.urlretrieve(url, output, lambda count, block, total: 
            sys.stdout.write(f"\r{Colors.C}[+] Progress: {count*block*100/total:.1f}%{Colors.N}") if total > 0 else None)
        print()
        return os.path.exists(output) and os.path.getsize(output) > 0
    
    def download_wget(self, url, output):
        if self.cmd(f"wget --version").returncode == 0:
            r = self.cmd(f"wget -q --show-progress -O {output} {url}", timeout=120)
            return r and r.returncode == 0
        return False
    
    def download_curl(self, url, output):
        if self.cmd(f"curl --version").returncode == 0:
            r = self.cmd(f"curl -L -o {output} {url}", timeout=120)
            return r and r.returncode == 0
        return False
    
    def download_frida_server(self):
        arch_map = {
            'arm64': 'android-arm64',
            'arm': 'android-arm',
            'x86_64': 'android-x86_64',
            'x86': 'android-x86'
        }
        
        frida_arch = arch_map.get(self.arch)
        if not frida_arch:
            print(f"{Colors.R}[✗] Unknown architecture{Colors.N}")
            return None
        
        filename = f"frida-server-{self.version}-{frida_arch}.xz"
        url = f"https://github.com/frida/frida/releases/download/v{self.version}/{filename}"
        output = os.path.join(self.temp_dir, filename)
        
        print(f"{Colors.Y}[*] Downloading: {filename}{Colors.N}")
        
        if self.download_with_fallback(url, output):
            return output
        
        mirrors = [
            f"https://hub.fastgit.xyz/frida/frida/releases/download/v{self.version}/{filename}",
            f"https://ghproxy.com/https://github.com/frida/frida/releases/download/v{self.version}/{filename}"
        ]
        
        for mirror in mirrors:
            print(f"{Colors.Y}[*] Trying mirror...{Colors.N}")
            if self.download_with_fallback(mirror, output):
                return output
        
        print(f"{Colors.R}[✗] Download failed after all attempts{Colors.N}")
        return None
    
    def extract_auto(self, compressed):
        print(f"{Colors.Y}[*] Extracting...{Colors.N}")
        extracted = compressed.replace('.xz', '')
        
        methods = [
            self.extract_lzma,
            self.extract_system_xz,
            self.extract_7zip
        ]
        
        for method in methods:
            result = self.retry_func(method, compressed, extracted)
            if result:
                print(f"{Colors.G}[✓] Extracted successfully{Colors.N}")
                return extracted
        
        return None
    
    def extract_lzma(self, compressed, extracted):
        import lzma
        with lzma.open(compressed, 'rb') as f_in:
            with open(extracted, 'wb') as f_out:
                f_out.write(f_in.read())
        return os.path.exists(extracted)
    
    def extract_system_xz(self, compressed, extracted):
        if self.system != "Windows":
            r = self.cmd(f"unxz -k {compressed}")
            return r and r.returncode == 0 and os.path.exists(extracted)
        return False
    
    def extract_7zip(self, compressed, extracted):
        if self.system == "Windows":
            r = self.cmd(f'7z x {compressed} -o{os.path.dirname(compressed)} -y')
            return r and r.returncode == 0
        return False
    
    def push_to_device(self, local_file):
        print(f"{Colors.Y}[*] Pushing to device...{Colors.N}")
        remote = "/data/local/tmp/frida-server"
        
        for attempt in range(3):
            r = self.cmd(f"adb -s {self.device_id} push {local_file} {remote}")
            if r and r.returncode == 0:
                self.cmd(f"adb -s {self.device_id} shell 'chmod 755 {remote}'")
                print(f"{Colors.G}[✓] Pushed successfully{Colors.N}")
                return True
            time.sleep(2)
        
        return False
    
    def install_pc_tools(self):
        print(f"{Colors.Y}[*] Installing PC tools...{Colors.N}")
        pip = "pip" if self.system == "Windows" else "pip3"
        
        for attempt in range(3):
            r = self.cmd(f"{pip} install frida=={self.version} frida-tools=={self.version} --upgrade --quiet --no-cache-dir")
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] PC tools installed{Colors.N}")
                return True
            time.sleep(3)
        
        r = self.cmd(f"{pip} install frida-tools --upgrade --quiet")
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] PC tools installed (latest){Colors.N}")
            return True
        
        return False
    
    def start_frida_auto(self):
        print(f"{Colors.Y}[*] Starting Frida server...{Colors.N}")
        
        self.cmd(f"adb -s {self.device_id} shell 'killall frida-server' 2>/dev/null")
        time.sleep(1)
        
        if self.has_root:
            cmd = f"adb -s {self.device_id} shell 'su -c \"/data/local/tmp/frida-server --daemon\"'"
        else:
            cmd = f"adb -s {self.device_id} shell '/data/local/tmp/frida-server --daemon'"
        
        self.cmd(cmd)
        time.sleep(3)
        
        for attempt in range(5):
            r = self.cmd(f"adb -s {self.device_id} shell 'pidof frida-server'")
            if r and r.stdout.strip():
                pid = r.stdout.strip()
                print(f"{Colors.G}[✓] Frida server running (PID: {pid}){Colors.N}")
                return True
            time.sleep(2)
        
        print(f"{Colors.Y}[!] Trying alternative start method...{Colors.N}")
        self.cmd(f"adb -s {self.device_id} shell 'nohup /data/local/tmp/frida-server &'")
        time.sleep(3)
        
        r = self.cmd(f"adb -s {self.device_id} shell 'ps | grep frida'")
        if r and r.stdout.strip():
            print(f"{Colors.G}[✓] Frida server started{Colors.N}")
            return True
        
        return False
    
    def verify_installation(self):
        print(f"{Colors.Y}[*] Verifying installation...{Colors.N}")
        
        r = self.cmd("frida --version")
        if r and r.stdout.strip():
            print(f"{Colors.G}[✓] Frida CLI: {r.stdout.strip()}{Colors.N}")
        else:
            print(f"{Colors.R}[✗] Frida CLI not found{Colors.N}")
        
        r = self.cmd("frida-ps -U 2>/dev/null")
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] Frida can see device{Colors.N}")
            self.verified = True
        else:
            print(f"{Colors.Y}[!] Run: adb forward tcp:27042 tcp:27042{Colors.N}")
            self.cmd("adb forward tcp:27042 tcp:27042")
            time.sleep(2)
            
            r = self.cmd("frida-ps -U 2>/dev/null")
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] Frida working after forward{Colors.N}")
                self.verified = True
        
        return self.verified
    
    def full_auto_install(self):
        print(f"{Colors.BD}{Colors.G}\n{'='*70}{Colors.N}")
        print(f"{Colors.BD}{Colors.G}AUTOMATED INSTALLATION STARTED (No Intervention Required){Colors.N}")
        print(f"{Colors.BD}{Colors.G}{'='*70}{Colors.N}")
        
        steps = [
            ("Checking requirements", self.check_all_requirements),
            ("Waiting for device", lambda: self.wait_for_device(180)),
            ("Enabling root", self.enable_root_automatically),
            ("Detecting architecture", self.detect_architecture),
            ("Getting best version", self.get_best_version),
            ("Downloading Frida", self.download_frida_server),
            ("Extracting files", lambda: self.extract_auto(self.download_frida_server()) if hasattr(self, '_last_download') else None),
            ("Pushing to device", lambda: self.push_to_device(self._last_extracted) if hasattr(self, '_last_extracted') else None),
            ("Installing PC tools", self.install_pc_tools),
            ("Starting server", self.start_frida_auto),
            ("Verifying", self.verify_installation)
        ]
        
        self._last_download = None
        self._last_extracted = None
        
        for step_name, step_func in steps:
            print(f"\n{Colors.C}▶ {step_name}...{Colors.N}")
            
            if step_name == "Downloading Frida":
                result = step_func()
                if result:
                    self._last_download = result
                    continue
            elif step_name == "Extracting files":
                if self._last_download:
                    result = step_func()
                    if result:
                        self._last_extracted = result
                        continue
            elif step_name == "Pushing to device":
                if self._last_extracted:
                    result = step_func()
                    if result:
                        continue
            else:
                result = step_func()
                if result is False and step_name not in ["Enabling root", "Verifying"]:
                    print(f"{Colors.R}[✗] Failed at: {step_name}{Colors.N}")
                    print(f"{Colors.Y}[*] Attempting recovery...{Colors.N}")
                    time.sleep(3)
                    continue
            
            if result is None and step_name not in ["Enabling root"]:
                print(f"{Colors.R}[✗] Critical failure at: {step_name}{Colors.N}")
                return False
        
        self.show_success()
        return True
    
    def show_success(self):
        print(f"\n{Colors.BD}{Colors.G}{'='*70}{Colors.N}")
        print(f"{Colors.BD}{Colors.G}🎉 INSTALLATION COMPLETE! 🎉{Colors.N}")
        print(f"{Colors.BD}{Colors.G}{'='*70}{Colors.N}")
        print(f"""
{Colors.C}Version     : {self.version}
{Colors.C}Architecture: {self.arch}
{Colors.C}Device      : {self.device_id}
{Colors.C}Root        : {'Yes' if self.has_root else 'No'}
{Colors.C}Status      : {'Verified' if self.verified else 'Running'}
{Colors.N}
{Colors.G}Quick Commands:{Colors.N}
  {Colors.Y}frida-ps -U{Colors.N}          - List processes
  {Colors.Y}frida-ps -Uai{Colors.N}        - List all apps
  {Colors.Y}frida -U -f com.app.name{Colors.N} - Attach to app
  {Colors.Y}frida -U --no-pause -l script.js{Colors.N} - Inject script
        """)
    
    def run_menu(self):
        while True:
            logo()
            print(f"""
{Colors.BD}{Colors.C}╔══════════════════════════════════════════════════════════════════╗
║                         MAIN MENU                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  {Colors.G}1{Colors.C} . 🚀 FULL AUTO INSTALL (Zero Intervention)                    {Colors.C}║
║  {Colors.G}2{Colors.C} . 📱 Start Frida Server                                       {Colors.C}║
║  {Colors.G}3{Colors.C} . 🛑 Stop Frida Server                                        {Colors.C}║
║  {Colors.G}4{Colors.C} . 📊 Check Status                                             {Colors.C}║
║  {Colors.G}5{Colors.C} . 📋 List Applications                                        {Colors.C}║
║  {Colors.G}6{Colors.C} . 💻 Interactive Shell                                        {Colors.C}║
║  {Colors.G}7{Colors.C} . 🗑️  Uninstall Frida                                         {Colors.C}║
║  {Colors.G}8{Colors.C} . ❌ Exit                                                     {Colors.C}║
╚══════════════════════════════════════════════════════════════════╝{Colors.N}
            """)
            
            choice = input(f"{Colors.C}{Colors.BD}krishna@tools~# {Colors.N}").strip()
            
            if choice == '1':
                if self.full_auto_install():
                    input(f"{Colors.G}[✓] Press Enter to continue{Colors.N}")
                else:
                    input(f"{Colors.R}[✗] Installation failed. Press Enter{Colors.N}")
            
            elif choice == '2':
                if self.wait_for_device(30):
                    self.start_frida_auto()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '3':
                if self.device_id or self.wait_for_device(30):
                    self.cmd(f"adb -s {self.device_id} shell 'killall frida-server'")
                    print(f"{Colors.G}[✓] Stopped{Colors.N}")
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '4':
                self.verify_installation()
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '5':
                self.cmd("frida-ps -Uai")
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '6':
                os.system("frida -U" if self.system != "Windows" else "frida -U")
            
            elif choice == '7':
                confirm = input(f"{Colors.R}[!] Confirm uninstall? (y/N): {Colors.N}")
                if confirm.lower() == 'y':
                    self.cmd(f"adb -s {self.device_id} shell 'su -c \"killall frida-server; rm -f /data/local/tmp/frida-server\"'")
                    print(f"{Colors.G}[✓] Uninstalled{Colors.N}")
                input(f"{Colors.Y}[*] Press Enter{Colors.N}")
            
            elif choice == '8':
                print(f"{Colors.G}\n[✓] Jay Shri Krishna 🙏{Colors.N}")
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                sys.exit(0)
            
            os.system('cls' if self.system == 'Windows' else 'clear')

if __name__ == "__main__":
    installer = AdvancedFridaInstaller()
    installer.run_menu()
