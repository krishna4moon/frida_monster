import subprocess
import time
import sys
import os
import platform
import tempfile
import shutil
import socket
import warnings
import urllib3
import glob
import signal
import threading
from datetime import datetime

warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except:
    pass

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
    DIM = '\033[2m'

def signal_handler(sig, frame):
    print(f"\n{Colors.Y}[!] Ctrl+C detected!{Colors.N}")
    print(f"{Colors.G}[✓] Cleaning up and exiting gracefully...{Colors.N}")
    print(f"{Colors.C}{Colors.BD}जय श्री कृष्णा 🙏{Colors.N}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def logo():
    krishna_art = f"""
{Colors.C}{Colors.BD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    KRISHNA TOOLS - Ultimate Frida Installer                  ║
║                         [ 100% Success Guaranteed ]                          ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.N}
{Colors.G}
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░ ME HI KRISHNA   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

{Colors.N}
"""
    print(krishna_art)

class WindowsFridaInstaller:
    def __init__(self):
        self.arch = None
        self.version = None
        self.device_id = None
        self.has_root = False
        self.pc_version = None
        self.temp_dir = tempfile.mkdtemp()
        self.system = platform.system()
        self.is_windows = True
        self.verified = False
        self.compatible_versions = []
        self.frida_process = None
        self.current_frida_session = None
        self.output_dir = "frida_outputs"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_output_filename(self, package_name, script_name=None):
        """Generate unique filename for output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if script_name:
            script_base = os.path.splitext(os.path.basename(script_name))[0]
            filename = f"{package_name}_{script_base}_{timestamp}.txt"
        else:
            filename = f"{package_name}_{timestamp}.txt"
        
        # Sanitize filename
        filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
        return os.path.join(self.output_dir, filename)
    
    def save_output_to_file(self, output, filename):
        """Save output to text file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Frida Analysis Report\n")
                f.write(f"{'='*60}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                f.write(output)
            print(f"{Colors.G}[✓] Output saved to: {filename}{Colors.N}")
            return True
        except Exception as e:
            print(f"{Colors.R}[✗] Failed to save output: {e}{Colors.N}")
            return False
    
    def cmd(self, cmd, shell=True, timeout=60):
        try:
            if self.is_windows:
                if 'grep' in cmd:
                    cmd = cmd.replace('grep', 'findstr')
                if 'ps -A' in cmd:
                    cmd = cmd.replace('ps -A', 'tasklist')
                if '2>/dev/null' in cmd:
                    cmd = cmd.replace('2>/dev/null', '2>nul')
                if '2>&1' in cmd:
                    cmd = cmd.replace('2>&1', '2>nul')
            
            startupinfo = None
            if self.is_windows:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, 
                             timeout=timeout, startupinfo=startupinfo)
            return r
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def adb(self, args, desc=""):
        if desc:
            print(f"{Colors.Y}[*] {desc}...{Colors.N}")
        r = self.cmd(f"adb {args}")
        if r and r.returncode != 0 and desc:
            error_msg = r.stderr[:100] if r.stderr else ""
            if error_msg:
                print(f"{Colors.DIM}[!] {error_msg}{Colors.N}")
        return r
    
    def check_adb(self):
        print(f"{Colors.Y}[*] Checking ADB...{Colors.N}")
        
        r = self.cmd("where adb")
        if not r or r.returncode != 0:
            print(f"{Colors.R}[✗] ADB not found in PATH{Colors.N}")
            print(f"{Colors.Y}[*] Looking for ADB in common locations...{Colors.N}")
            
            common_paths = [
                r"C:\Platform-Tools\adb.exe",
                r"C:\adb\adb.exe",
                r"C:\Android\platform-tools\adb.exe",
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools\adb.exe")
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    adb_dir = os.path.dirname(path)
                    os.environ['PATH'] = adb_dir + os.pathsep + os.environ['PATH']
                    print(f"{Colors.G}[✓] Found ADB at: {path}{Colors.N}")
                    break
            else:
                print(f"{Colors.R}[✗] Please install Android Platform Tools{Colors.N}")
                print(f"{Colors.C}Download: https://developer.android.com/studio/releases/platform-tools{Colors.N}")
                return False
        
        r = self.cmd("adb version")
        if r and r.returncode == 0:
            version_line = r.stdout.split('\n')[0] if r.stdout else ""
            print(f"{Colors.G}[✓] {version_line}{Colors.N}")
            return True
        
        return False
    
    def wait_for_device(self, max_wait=120):
        print(f"{Colors.Y}[*] Waiting for Android device...{Colors.N}")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                r = self.adb("devices")
                if r and r.stdout:
                    lines = r.stdout.strip().split('\n')[1:]
                    for line in lines:
                        if line.strip() and 'device' in line and 'unauthorized' not in line:
                            self.device_id = line.split('\t')[0].strip()
                            print(f"{Colors.G}[✓] Device connected: {self.device_id}{Colors.N}")
                            return True
            except:
                pass
            
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                print(f"{Colors.DIM}[*] Waiting... {elapsed}s (Press Ctrl+C to exit){Colors.N}")
            time.sleep(2)
        
        print(f"{Colors.R}[✗] No device found after {max_wait}s{Colors.N}")
        print(f"{Colors.Y}[!] Ensure USB debugging is enabled{Colors.N}")
        return False
    
    def check_root(self):
        print(f"{Colors.Y}[*] Checking root access...{Colors.N}")
        
        r = self.cmd(f"adb -s {self.device_id} shell \"su -c 'echo test'\" 2>nul")
        if r and r.returncode == 0:
            self.has_root = True
            print(f"{Colors.G}[✓] Root access available{Colors.N}")
            return True
        
        print(f"{Colors.Y}[!] No root access (limited functionality){Colors.N}")
        return False
    
    def detect_architecture(self):
        print(f"{Colors.Y}[*] Detecting architecture...{Colors.N}")
        
        r = self.cmd(f"adb -s {self.device_id} shell getprop ro.product.cpu.abi")
        if r and r.stdout:
            out = r.stdout.strip().lower()
            if 'arm64' in out:
                self.arch = 'arm64'
            elif 'armv7' in out or 'armeabi' in out:
                self.arch = 'arm'
            elif 'x86_64' in out:
                self.arch = 'x86_64'
            elif 'x86' in out:
                self.arch = 'x86'
        
        if not self.arch:
            r = self.cmd(f"adb -s {self.device_id} shell uname -m")
            if r and r.stdout:
                out = r.stdout.strip().lower()
                if 'aarch64' in out:
                    self.arch = 'arm64'
                elif 'arm' in out:
                    self.arch = 'arm'
                elif 'x86_64' in out:
                    self.arch = 'x86_64'
                else:
                    self.arch = 'arm64'
            else:
                self.arch = 'arm64'
        
        print(f"{Colors.G}[✓] Architecture: {self.arch}{Colors.N}")
        return True
    
    def get_all_versions(self):
        versions = []
        
        try:
            print(f"{Colors.Y}[*] Fetching versions from GitHub API...{Colors.N}")
            r = requests.get('https://api.github.com/repos/frida/frida/releases?per_page=100', 
                           timeout=10, verify=False)
            if r.status_code == 200:
                releases = r.json()
                for release in releases:
                    ver = release['tag_name'].lstrip('v')
                    versions.append(ver)
                print(f"{Colors.G}[✓] Found {len(versions)} versions from API{Colors.N}")
                return versions
        except:
            pass
        
        print(f"{Colors.Y}[*] Using comprehensive version list...{Colors.N}")
        for major in range(17, 13, -1):
            for minor in range(20, 0, -1):
                for patch in range(20, 0, -1):
                    versions.append(f"{major}.{minor}.{patch}")
        
        for major in range(16, 14, -1):
            for minor in range(20, 0, -1):
                for patch in range(20, 0, -1):
                    versions.append(f"{major}.{minor}.{patch}")
        
        for major in range(15, 13, -1):
            for minor in range(20, 0, -1):
                for patch in range(20, 0, -1):
                    versions.append(f"{major}.{minor}.{patch}")
        
        print(f"{Colors.G}[✓] Generated {len(versions)} versions to check{Colors.N}")
        return versions
    
    def check_version_compatibility(self, version):
        arch_map = {
            'arm64': 'android-arm64',
            'arm': 'android-arm',
            'x86_64': 'android-x86_64',
            'x86': 'android-x86'
        }
        
        frida_arch = arch_map.get(self.arch)
        url = f"https://github.com/frida/frida/releases/download/{version}/frida-server-{version}-{frida_arch}.xz"
        
        try:
            response = requests.head(url, timeout=5, verify=False, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def remove_pc_frida(self):
        print(f"{Colors.Y}[*] Removing old PC Frida version...{Colors.N}")
        pip = "pip" if self.is_windows else "pip3"
        
        r = self.cmd(f"{pip} uninstall frida frida-tools -y -q")
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] Old Frida version removed{Colors.N}")
            return True
        else:
            print(f"{Colors.Y}[!] Could not remove old version{Colors.N}")
            return False
    
    def find_compatible_version_guaranteed(self):
        print(f"{Colors.BD}{Colors.C}\n╔════════════════════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.BD}{Colors.C}║     SEARCHING FOR COMPATIBLE FRIDA VERSION (WILL NOT STOP)    ║{Colors.N}")
        print(f"{Colors.BD}{Colors.C}╚════════════════════════════════════════════════════════════╝{Colors.N}")
        
        r = self.cmd("frida --version 2>nul")
        if r and r.stdout and r.stdout.strip():
            self.pc_version = r.stdout.strip()
            print(f"{Colors.G}[✓] Current PC Frida: {self.pc_version}{Colors.N}")
            
            print(f"{Colors.Y}[*] Testing PC version compatibility...{Colors.N}")
            if self.check_version_compatibility(self.pc_version):
                print(f"{Colors.G}[✓] Version {self.pc_version} is compatible!{Colors.N}")
                self.version = self.pc_version
                return True
            else:
                print(f"{Colors.R}[✗] Version {self.pc_version} is NOT compatible with {self.arch}{Colors.N}")
                print(f"{Colors.Y}[*] Will remove incompatible PC version...{Colors.N}")
                self.remove_pc_frida()
        
        all_versions = self.get_all_versions()
        
        print(f"{Colors.Y}[*] Total versions to check: {len(all_versions)}{Colors.N}")
        print(f"{Colors.Y}[*] Architecture: {self.arch}{Colors.N}")
        print(f"{Colors.Y}[*] Starting scan (this may take a few minutes)...{Colors.N}\n")
        
        for idx, version in enumerate(all_versions, 1):
            percent = (idx / len(all_versions)) * 100
            bar_len = 40
            filled = int(bar_len * idx // len(all_versions))
            bar = '█' * filled + '░' * (bar_len - filled)
            sys.stdout.write(f"\r{Colors.C}[{bar}] {percent:.1f}% - Checking {version}{' ' * 20}{Colors.N}")
            sys.stdout.flush()
            
            if self.check_version_compatibility(version):
                print(f"\n{Colors.G}[✓] COMPATIBLE VERSION FOUND: {version}{Colors.N}")
                self.version = version
                return True
            
            time.sleep(0.05)
        
        print(f"\n\n{Colors.R}[!] No compatible versions found!{Colors.N}")
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
        output = os.path.join(self.temp_dir, filename)
        
        urls = [
            f"https://github.com/frida/frida/releases/download/{self.version}/{filename}",
            f"https://hub.fastgit.xyz/frida/frida/releases/download/{self.version}/{filename}",
            f"https://ghproxy.com/https://github.com/frida/frida/releases/download/{self.version}/{filename}",
            f"https://download.frida.releases/{self.version}/{filename}"
        ]
        
        for idx, url in enumerate(urls):
            print(f"{Colors.Y}[*] Downloading {self.version}... (Attempt {idx+1}/{len(urls)}){Colors.N}")
            print(f"{Colors.DIM}[*] URL: {url[:80]}{Colors.N}")
            
            try:
                response = requests.get(url, stream=True, timeout=60, verify=False, allow_redirects=True)
                
                if response.status_code == 200:
                    total = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(output, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=65536):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                percent = (downloaded / total) * 100
                                bar_len = 30
                                filled = int(bar_len * downloaded // total)
                                bar = '█' * filled + '░' * (bar_len - filled)
                                sys.stdout.write(f"\r{Colors.C}[{bar}] {percent:.1f}%{Colors.N}")
                                sys.stdout.flush()
                    
                    print(f"\n{Colors.G}[✓] Download complete{Colors.N}")
                    return output
                else:
                    print(f"{Colors.Y}[!] HTTP {response.status_code}{Colors.N}")
                    
            except Exception as e:
                print(f"{Colors.Y}[!] Failed: {str(e)[:40]}{Colors.N}")
            
            time.sleep(2)
        
        print(f"{Colors.R}[✗] All download attempts failed{Colors.N}")
        return None
    
    def extract_frida(self, compressed_file):
        print(f"{Colors.Y}[*] Extracting...{Colors.N}")
        extracted = compressed_file.replace('.xz', '')
        
        try:
            import lzma
            with lzma.open(compressed_file, 'rb') as f_in:
                with open(extracted, 'wb') as f_out:
                    f_out.write(f_in.read())
            print(f"{Colors.G}[✓] Extraction complete{Colors.N}")
            return extracted
        except:
            r = self.cmd(f'7z x "{compressed_file}" -o"{os.path.dirname(compressed_file)}" -y')
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] Extraction complete (7zip){Colors.N}")
                return extracted
        
        print(f"{Colors.R}[✗] Extraction failed{Colors.N}")
        return None
    
    def push_to_device(self, local_file):
        print(f"{Colors.Y}[*] Pushing to device...{Colors.N}")
        remote = "/data/local/tmp/frida-server"
        
        r = self.cmd(f"adb -s {self.device_id} push \"{local_file}\" {remote}")
        if not r or r.returncode != 0:
            print(f"{Colors.R}[✗] Push failed{Colors.N}")
            return False
        
        self.cmd(f"adb -s {self.device_id} shell chmod 755 {remote}")
        print(f"{Colors.G}[✓] Pushed successfully{Colors.N}")
        return True
    
    def install_pc_tools(self):
        print(f"{Colors.Y}[*] Installing compatible PC Frida tools...{Colors.N}")
        pip = "pip" if self.is_windows else "pip3"
        
        print(f"{Colors.Y}[*] Installing Frida {self.version} on PC...{Colors.N}")
        r = self.cmd(f"{pip} install frida=={self.version} frida-tools=={self.version} --upgrade --quiet")
        
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] Frida tools v{self.version} installed on PC{Colors.N}")
            verify = self.cmd("frida --version 2>nul")
            if verify and verify.stdout:
                print(f"{Colors.G}[✓] Verification: Frida {verify.stdout.strip()} installed{Colors.N}")
            return True
        else:
            print(f"{Colors.Y}[*] Trying with latest version...{Colors.N}")
            r = self.cmd(f"{pip} install frida-tools --upgrade --quiet")
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] Latest Frida tools installed{Colors.N}")
                return True
        
        print(f"{Colors.Y}[*] Trying with --user flag...{Colors.N}")
        r = self.cmd(f"{pip} install frida=={self.version} frida-tools=={self.version} --user --upgrade --quiet")
        if r and r.returncode == 0:
            print(f"{Colors.G}[✓] Frida tools installed with --user{Colors.N}")
            return True
        
        return False
    
    def start_frida_server(self):
        print(f"{Colors.Y}[*] Starting Frida server...{Colors.N}")
        
        # Kill existing frida-server processes
        self.cmd(f"adb -s {self.device_id} shell \"killall frida-server\" 2>nul")
        time.sleep(1)
        
        # Start frida-server in background (non-blocking)
        try:
            # Use CREATE_NO_WINDOW flag on Windows to prevent console window
            if self.is_windows:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                startupinfo = None
                creationflags = 0
            
            adb_command = f"adb -s {self.device_id} shell \"/data/local/tmp/frida-server\""
            self.frida_process = subprocess.Popen(
                adb_command, 
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags if self.is_windows else 0
            )
            time.sleep(2)
            
            # Verify it's running without blocking
            if self.check_frida_status():
                print(f"{Colors.G}[✓] Frida server started successfully!{Colors.N}")
                return True
            else:
                print(f"{Colors.R}[✗] Failed to start Frida server{Colors.N}")
                return False
                
        except Exception as e:
            print(f"{Colors.R}[✗] Error starting Frida server: {e}{Colors.N}")
            return False
    
    def check_frida_status(self):
        try:
            r = self.cmd(f"adb -s {self.device_id} shell \"pidof frida-server\" 2>nul", timeout=5)
            if r and r.stdout and r.stdout.strip():
                print(f"{Colors.G}[✓] Frida server is running (PID: {r.stdout.strip()}){Colors.N}")
                return True
        except:
            pass
        
        try:
            r = self.cmd(f"adb -s {self.device_id} shell \"ps | grep -i frida\" 2>nul", timeout=5)
            if r and r.stdout and 'frida' in r.stdout.lower():
                print(f"{Colors.G}[✓] Frida server is running{Colors.N}")
                return True
        except:
            pass
        
        print(f"{Colors.R}[✗] Frida server is not running{Colors.N}")
        return False
    
    def stop_frida_server(self):
        print(f"{Colors.Y}[*] Stopping Frida server...{Colors.N}")
        
        # Kill via ADB
        self.cmd(f"adb -s {self.device_id} shell \"killall frida-server\" 2>nul")
        
        # Terminate local process if exists
        if self.frida_process:
            try:
                self.frida_process.terminate()
                self.frida_process = None
            except:
                pass
        
        time.sleep(1)
        print(f"{Colors.G}[✓] Frida server stopped{Colors.N}")
    
    def verify_installation(self):
        print(f"{Colors.Y}[*] Verifying installation...{Colors.N}")
        
        r = self.cmd("frida --version 2>nul")
        if r and r.stdout:
            print(f"{Colors.G}[✓] Frida CLI: {r.stdout.strip()}{Colors.N}")
        
        self.check_frida_status()
        
        # Test connection (non-blocking)
        try:
            r = self.cmd("frida-ps -U 2>nul", timeout=10)
            if r and r.returncode == 0:
                print(f"{Colors.G}[✓] Frida can communicate with device{Colors.N}")
                self.verified = True
            else:
                # Setup port forwarding
                self.cmd("adb forward tcp:27042 tcp:27042")
                self.cmd("adb forward tcp:27043 tcp:27043")
                time.sleep(2)
                
                r = self.cmd("frida-ps -U 2>nul", timeout=10)
                if r and r.returncode == 0:
                    print(f"{Colors.G}[✓] Frida working after port forward{Colors.N}")
                    self.verified = True
                else:
                    print(f"{Colors.R}[✗] Cannot communicate with device{Colors.N}")
        except:
            print(f"{Colors.R}[✗] Timeout checking Frida connection{Colors.N}")
        
        return self.verified
    
    def get_running_processes(self):
        try:
            frida_ps_command = "frida-ps -Uai"
            output = subprocess.check_output(frida_ps_command, shell=True, timeout=10).decode()
            lines = output.strip().split('\n')[2:]
            processes = [line.split(maxsplit=3) for line in lines if line.strip()]
            processes_with_serial = []
            for process in processes:
                if len(process) >= 4 and process[0] != "-":
                    processes_with_serial.append((process[1], process[2], process[3]))
                elif len(process) >= 3:
                    processes_with_serial.append((process[0], process[1], process[2]))
            return processes_with_serial
        except subprocess.TimeoutExpired:
            print(f"{Colors.R}[✗] Timeout getting processes{Colors.N}")
            return []
        except subprocess.CalledProcessError as e:
            print(f"{Colors.R}[✗] Error executing frida-ps command: {e}{Colors.N}")
            return []
    
    def display_packages_with_serial(self, processes):
        print(f"{Colors.C}{'PID':<8}{'Name':<35}Identifier{Colors.N}")
        print(f"{Colors.DIM}{'-'*70}{Colors.N}")
        for idx, process in enumerate(processes, 1):
            if len(process) >= 3:
                print(f"{Colors.G}{idx:<4}{Colors.Y}{process[0]:<8}{Colors.G}{process[1][:34]:<35}{Colors.C}{process[2]}{Colors.N}")
    
    def select_scripts_advanced(self):
        js_files = glob.glob("*.js")
        
        if not js_files:
            print(f"{Colors.Y}[!] No script files (.js) found in current directory{Colors.N}")
            print(f"{Colors.Y}[*] Continuing without any scripts...{Colors.N}")
            return []
        
        print(f"{Colors.C}╔══════════════════════════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.C}║                    AVAILABLE SCRIPTS                             ║{Colors.N}")
        print(f"{Colors.C}╚══════════════════════════════════════════════════════════════════╝{Colors.N}")
        
        for i, script in enumerate(js_files, 1):
            print(f"{Colors.G}{i}. {Colors.Y}{script}{Colors.N}")
        
        print(f"\n{Colors.G}[?] Select script number (or enter multiple numbers like 1,3,5):{Colors.N}")
        print(f"{Colors.DIM}   Press Enter without selection to run without scripts{Colors.N}")
        print(f"{Colors.DIM}   Press Ctrl+C to cancel{Colors.N}")
        
        try:
            script_choice = input(f"{Colors.C}krishna@tools~# {Colors.N}").strip()
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[!] Cancelled by user{Colors.N}")
            return None
        
        if not script_choice:
            print(f"{Colors.Y}[*] No scripts selected. Running without scripts.{Colors.N}")
            return []
        
        if ',' in script_choice:
            selected_indices = [int(x.strip()) for x in script_choice.split(',') if x.strip().isdigit()]
            selected_scripts = [js_files[i-1] for i in selected_indices if 1 <= i <= len(js_files)]
            if selected_scripts:
                print(f"{Colors.G}[✓] Selected scripts: {', '.join(selected_scripts)}{Colors.N}")
                return selected_scripts
        elif script_choice.isdigit():
            idx = int(script_choice)
            if 1 <= idx <= len(js_files):
                selected_script = js_files[idx-1]
                print(f"{Colors.G}[✓] Selected script: {selected_script}{Colors.N}")
                return [selected_script]
        
        print(f"{Colors.R}[✗] Invalid selection{Colors.N}")
        return []
    
    def run_frida_in_same_window(self, package_identifier, scripts=None):
        """Run Frida in the same window with output saving"""
        if scripts is None:
            scripts = []
        
        # Build the frida command
        frida_command = f"frida -U -f {package_identifier}"
        for script in scripts:
            if os.path.exists(script):
                frida_command += f" -l {script}"
        
        # Generate output filename
        script_names = '_'.join([os.path.splitext(s)[0] for s in scripts]) if scripts else "no_script"
        output_file = self.get_output_filename(package_identifier, script_names)
        
        print(f"{Colors.G}[*] Running: {frida_command}{Colors.N}")
        print(f"{Colors.G}[*] Output will be saved to: {output_file}{Colors.N}")
        print(f"{Colors.Y}[!] Press Ctrl+C to detach from the process{Colors.N}")
        print(f"{Colors.C}{'='*70}{Colors.N}")
        
        # Run frida and capture output
        try:
            # Open file for writing
            with open(output_file, 'w', encoding='utf-8') as outfile:
                # Write header
                outfile.write(f"Frida Analysis Report\n")
                outfile.write(f"{'='*60}\n")
                outfile.write(f"Package: {package_identifier}\n")
                outfile.write(f"Scripts: {', '.join(scripts) if scripts else 'None'}\n")
                outfile.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"{'='*60}\n\n")
                outfile.flush()
                
                # Run process and capture output in real-time
                process = subprocess.Popen(
                    frida_command, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                self.current_frida_session = process
                
                # Capture and display output in real-time
                for line in process.stdout:
                    print(line, end='')  # Display on console
                    outfile.write(line)  # Save to file
                    outfile.flush()
                
                process.wait()
                self.current_frida_session = None
                
            print(f"\n{Colors.G}[✓] Output saved to: {output_file}{Colors.N}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[!] Frida session ended by user{Colors.N}")
            if self.current_frida_session:
                self.current_frida_session.terminate()
                self.current_frida_session = None
            print(f"{Colors.G}[✓] Partial output saved to: {output_file}{Colors.N}")
        except Exception as e:
            print(f"{Colors.R}[✗] Error: {e}{Colors.N}")
            if self.current_frida_session:
                self.current_frida_session = None
    
    def simple_attach_mode(self):
        print(f"{Colors.G}[*] Simple Frida Attach Mode (Runs in Same Window){Colors.N}")
        print(f"{Colors.Y}[!] This will start Frida server and attach to selected app{Colors.N}")
        print(f"{Colors.G}[!] All outputs will be saved to '{self.output_dir}' folder{Colors.N}\n")
        
        # Start server if not running
        if not self.check_frida_status():
            print(f"{Colors.Y}[*] Starting Frida server...{Colors.N}")
            if not self.start_frida_server():
                print(f"{Colors.R}[✗] Failed to start Frida server{Colors.N}")
                return
        
        processes = self.get_running_processes()
        
        if not processes:
            print(f"{Colors.R}[✗] No processes found. Make sure frida-server is running{Colors.N}")
            return
        
        print(f"{Colors.Y}Running processes:{Colors.N}")
        self.display_packages_with_serial(processes)
        
        while True:
            try:
                choice = input(f"\n{Colors.C}Select number (0 to exit): {Colors.N}").strip()
                if choice == '0':
                    print(f"{Colors.G}[✓] Exiting...{Colors.N}")
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(processes):
                    package_identifier = processes[int(choice) - 1][2]
                    print(f"{Colors.G}[*] Attaching to: {package_identifier}{Colors.N}")
                    
                    selected_scripts = self.select_scripts_advanced()
                    if selected_scripts is None:
                        continue
                    
                    self.run_frida_in_same_window(package_identifier, selected_scripts)
                    print(f"\n{Colors.G}[✓] Frida session completed{Colors.N}")
                    break
                else:
                    print(f"{Colors.R}[✗] Invalid number. Please try again.{Colors.N}")
            except KeyboardInterrupt:
                print(f"\n{Colors.Y}[!] Operation cancelled by user{Colors.N}")
                break
            except ValueError:
                print(f"{Colors.R}[✗] Invalid input. Please enter a valid number.{Colors.N}")
    
    def interactive_shell(self):
        print(f"{Colors.G}[*] Interactive Frida Mode (Type 'exit' to return){Colors.N}")
        print(f"{Colors.C}{'='*60}{Colors.N}")
        print(f"{Colors.Y}Quick Commands:{Colors.N}")
        print(f"  frida-ps -U          - List running processes")
        print(f"  frida-ps -Uai        - List all installed apps")
        print(f"  frida -U PID         - Attach to process")
        print(f"  frida -U -f PACKAGE  - Spawn and attach to app")
        print(f"  save_output          - Save last command output to file")
        print(f"  help                 - Show this help")
        print(f"  exit                 - Return to main menu")
        print(f"{Colors.C}{'='*60}{Colors.N}\n")
        
        last_output = ""
        
        while True:
            try:
                cmd = input(f"{Colors.C}{Colors.BD}frida~# {Colors.N}").strip()
                
                if cmd.lower() == 'exit':
                    break
                elif cmd.lower() == 'help':
                    print(f"\n{Colors.Y}Frida Commands:{Colors.N}")
                    print(f"  frida-ps -U                 - List running processes")
                    print(f"  frida-ps -Uai               - List all apps")
                    print(f"  frida -U <PID>              - Attach to process ID")
                    print(f"  frida -U -n <name>          - Attach by process name")
                    print(f"  frida -U -f <package>       - Spawn and attach to app")
                    print(f"  frida -U <PID> -l script.js - Attach with script")
                    print(f"  save_output                 - Save last command output to file")
                    print(f"  exit                        - Return to menu\n")
                    continue
                elif cmd.lower() == 'save_output':
                    if last_output:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = os.path.join(self.output_dir, f"interactive_command_{timestamp}.txt")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"Interactive Frida Command Output\n")
                            f.write(f"{'='*60}\n")
                            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"{'='*60}\n\n")
                            f.write(last_output)
                        print(f"{Colors.G}[✓] Output saved to: {filename}{Colors.N}")
                    else:
                        print(f"{Colors.Y}[!] No output to save. Run a command first.{Colors.N}")
                    continue
                elif not cmd:
                    continue
                
                # Run the command and capture output
                print(f"{Colors.G}[*] Executing: {cmd}{Colors.N}\n")
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                    output = result.stdout + result.stderr
                    print(output)
                    last_output = output
                    
                    # Auto-save if it's a long output or contains important data
                    if len(output) > 1000 or 'key' in output.lower() or 'token' in output.lower():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = os.path.join(self.output_dir, f"auto_save_{timestamp}.txt")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"Command: {cmd}\n")
                            f.write(f"{'='*60}\n")
                            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"{'='*60}\n\n")
                            f.write(output)
                        print(f"{Colors.G}[✓] Output auto-saved to: {filename}{Colors.N}")
                    
                except subprocess.TimeoutExpired:
                    print(f"{Colors.R}[✗] Command timed out after 60 seconds{Colors.N}")
                except Exception as e:
                    print(f"{Colors.R}[✗] Error: {e}{Colors.N}")
                
                print(f"\n{Colors.DIM}[*] Command finished. Type 'save_output' to save last output, or 'exit' to return{Colors.N}\n")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.Y}[!] Use 'exit' to return to menu{Colors.N}")
                continue
            except Exception as e:
                print(f"{Colors.R}[✗] Error: {e}{Colors.N}")
    
    def get_package_name(self):
        print(f"{Colors.Y}[*] Fetching installed packages...{Colors.N}")
        result = self.cmd("frida-ps -Uai")
        packages = []
        if result and result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        package = parts[-1]
                        name = ' '.join(parts[:-1])
                        packages.append((package, name))
        return packages
    
    def get_js_scripts(self):
        js_files = glob.glob("*.js")
        return js_files
    
    def run_frida_bypass(self, package_name, bypass_type, script_path=None):
        print(f"{Colors.G}[*] Running Frida on {package_name} with {bypass_type} bypass{Colors.N}")
        
        if bypass_type == "ssl":
            cmd = f"frida --codeshare fdciabdul/disable-flutter-tls -f {package_name}"
        elif bypass_type == "root":
            cmd = f"frida --codeshare pcipolloni/universal-android-root-detection-bypass -f {package_name}"
        elif bypass_type == "emulator":
            cmd = f"frida --codeshare dzonerzy/fridantiroot -f {package_name}"
        elif bypass_type == "anti":
            cmd = f"frida --codeshare enovella/anti-frida-bypass -f {package_name}"
        elif bypass_type == "custom" and script_path:
            cmd = f"frida -U -f {package_name} -l {script_path}"
        elif bypass_type == "multiple":
            cmd = f"frida --codeshare fdciabdul/frida-multiple-bypass -f {package_name}"
        else:
            cmd = f"frida -U -f {package_name}"
        
        # Generate output filename
        output_file = self.get_output_filename(package_name, bypass_type)
        
        print(f"{Colors.C}[*] Running: {cmd}{Colors.N}")
        print(f"{Colors.G}[*] Output will be saved to: {output_file}{Colors.N}")
        print(f"{Colors.Y}[!] Press Ctrl+C to detach{Colors.N}\n")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write(f"Frida Bypass Analysis Report\n")
                outfile.write(f"{'='*60}\n")
                outfile.write(f"Package: {package_name}\n")
                outfile.write(f"Bypass Type: {bypass_type}\n")
                outfile.write(f"Script: {script_path if script_path else 'None'}\n")
                outfile.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"{'='*60}\n\n")
                outfile.flush()
                
                process = subprocess.Popen(
                    cmd, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                for line in process.stdout:
                    print(line, end='')
                    outfile.write(line)
                    outfile.flush()
                
                process.wait()
            
            print(f"\n{Colors.G}[✓] Output saved to: {output_file}{Colors.N}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[!] Bypass session ended by user{Colors.N}")
            print(f"{Colors.G}[✓] Partial output saved to: {output_file}{Colors.N}")
        except Exception as e:
            print(f"{Colors.R}[✗] Error: {e}{Colors.N}")
    
    def interactive_attach(self):
        print(f"{Colors.G}[*] Advanced Frida Attach Mode (Runs in Same Window){Colors.N}")
        print(f"{Colors.Y}[!] This will help you bypass detection and inject scripts{Colors.N}")
        print(f"{Colors.G}[!] All outputs will be saved to '{self.output_dir}' folder{Colors.N}\n")
        
        if not self.check_frida_status():
            print(f"{Colors.Y}[*] Starting Frida server...{Colors.N}")
            if not self.start_frida_server():
                print(f"{Colors.R}[✗] Failed to start Frida server{Colors.N}")
                return
        
        packages = self.get_package_name()
        if not packages:
            print(f"{Colors.R}[✗] No packages found. Make sure frida-server is running{Colors.N}")
            return
        
        print(f"{Colors.C}╔══════════════════════════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.C}║                    AVAILABLE PACKAGES                            ║{Colors.N}")
        print(f"{Colors.C}╚══════════════════════════════════════════════════════════════════╝{Colors.N}")
        
        for i, (pkg, name) in enumerate(packages[:30], 1):
            print(f"{Colors.G}{i:3}. {Colors.Y}{pkg}{Colors.N}")
            print(f"{Colors.DIM}     {name[:50]}{Colors.N}")
        
        print(f"\n{Colors.G}[?] Select package number (or enter package name):{Colors.N}")
        print(f"{Colors.DIM}Press Ctrl+C to cancel{Colors.N}")
        
        try:
            choice = input(f"{Colors.C}krishna@tools~# {Colors.N}").strip()
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[!] Cancelled by user{Colors.N}")
            return
        
        selected_package = None
        if choice.isdigit() and 1 <= int(choice) <= len(packages):
            selected_package = packages[int(choice)-1][0]
        else:
            selected_package = choice
        
        print(f"{Colors.G}[✓] Selected: {selected_package}{Colors.N}\n")
        
        print(f"{Colors.C}╔══════════════════════════════════════════════════════════════════╗{Colors.N}")
        print(f"{Colors.C}║                    BYPASS OPTIONS                                ║{Colors.N}")
        print(f"{Colors.C}╚══════════════════════════════════════════════════════════════════╝{Colors.N}")
        print(f"{Colors.G}1{Colors.N}. SSL Pinning Bypass (Disable SSL/TLS verification)")
        print(f"{Colors.G}2{Colors.N}. Root Detection Bypass (Hide root from app)")
        print(f"{Colors.G}3{Colors.N}. Emulator Detection Bypass (Hide emulator)")
        print(f"{Colors.G}4{Colors.N}. Anti-Frida Detection Bypass (Hide Frida)")
        print(f"{Colors.G}5{Colors.N}. Multiple Bypass (All in one)")
        print(f"{Colors.G}6{Colors.N}. Custom Script (Use your own .js file)")
        print(f"{Colors.G}7{Colors.N}. Normal Attach (No bypass)")
        
        try:
            bypass_choice = input(f"\n{Colors.C}krishna@tools~# {Colors.N}").strip()
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[!] Cancelled by user{Colors.N}")
            return
        
        js_files = self.get_js_scripts()
        selected_script = None
        
        if bypass_choice == '6':
            if js_files:
                print(f"\n{Colors.C}╔══════════════════════════════════════════════════════════════════╗{Colors.N}")
                print(f"{Colors.C}║                    AVAILABLE SCRIPTS                             ║{Colors.N}")
                print(f"{Colors.C}╚══════════════════════════════════════════════════════════════════╝{Colors.N}")
                
                for i, script in enumerate(js_files, 1):
                    print(f"{Colors.G}{i}. {Colors.Y}{script}{Colors.N}")
                
                print(f"\n{Colors.G}[?] Select script number (or enter multiple numbers like 1,3,5):{Colors.N}")
                print(f"{Colors.DIM}Press Ctrl+C to cancel{Colors.N}")
                
                try:
                    script_choice = input(f"{Colors.C}krishna@tools~# {Colors.N}").strip()
                except KeyboardInterrupt:
                    print(f"\n{Colors.Y}[!] Cancelled by user{Colors.N}")
                    return
                
                if ',' in script_choice:
                    selected_indices = [int(x.strip()) for x in script_choice.split(',') if x.strip().isdigit()]
                    selected_scripts = [js_files[i-1] for i in selected_indices if 1 <= i <= len(js_files)]
                    
                    if selected_scripts:
                        print(f"{Colors.G}[✓] Selected scripts: {', '.join(selected_scripts)}{Colors.N}")
                        print(f"{Colors.Y}[*] Running with multiple scripts...{Colors.N}")
                        self.run_frida_in_same_window(selected_package, selected_scripts)
                        return
                elif script_choice.isdigit():
                    idx = int(script_choice)
                    if 1 <= idx <= len(js_files):
                        selected_script = js_files[idx-1]
                        print(f"{Colors.G}[✓] Selected script: {selected_script}{Colors.N}")
                else:
                    print(f"{Colors.R}[✗] Invalid selection{Colors.N}")
                    return
            else:
                print(f"{Colors.R}[✗] No .js scripts found in current directory{Colors.N}")
                print(f"{Colors.Y}[*] Place your Frida scripts (.js files) in the same folder{Colors.N}")
                return
        
        bypass_map = {
            '1': 'ssl',
            '2': 'root',
            '3': 'emulator',
            '4': 'anti',
            '5': 'multiple',
            '6': 'custom',
            '7': 'normal'
        }
        
        bypass_type = bypass_map.get(bypass_choice, 'normal')
        
        if bypass_type == 'custom' and selected_script:
            self.run_frida_bypass(selected_package, 'custom', selected_script)
        elif bypass_type != 'normal':
            self.run_frida_bypass(selected_package, bypass_type)
        else:
            self.run_frida_in_same_window(selected_package, [])
    
    def list_apps(self):
        print(f"{Colors.Y}[*] Listing applications...{Colors.N}")
        result = self.cmd("frida-ps -Uai")
        if result and result.stdout:
            print(result.stdout)
            
            # Save to file
            output_file = os.path.join(self.output_dir, f"app_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Installed Applications List\n")
                f.write(f"{'='*60}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                f.write(result.stdout)
            print(f"{Colors.G}[✓] App list saved to: {output_file}{Colors.N}")
        else:
            print(f"{Colors.R}[✗] Failed to list apps. Is frida-server running?{Colors.N}")
    
    def uninstall(self):
        print(f"{Colors.R}[*] Uninstalling Frida from device...{Colors.N}")
        self.stop_frida_server()
        
        if self.has_root:
            self.cmd(f"adb -s {self.device_id} shell \"su -c 'rm -f /data/local/tmp/frida-server'\"")
        else:
            self.cmd(f"adb -s {self.device_id} shell \"rm -f /data/local/tmp/frida-server\"")
        
        print(f"{Colors.G}[✓] Removed from device{Colors.N}")
        
        confirm = input(f"{Colors.Y}[?] Also remove PC Frida tools? (y/N): {Colors.N}")
        if confirm.lower() == 'y':
            self.remove_pc_frida()
            print(f"{Colors.G}[✓] PC Frida tools removed{Colors.N}")
    
    def full_install(self):
        print(f"{Colors.BD}{Colors.G}\n{'='*70}{Colors.N}")
        print(f"{Colors.BD}{Colors.G}🚀 AUTOMATED INSTALLATION STARTED (100% Success Guaranteed){Colors.N}")
        print(f"{Colors.BD}{Colors.G}{'='*70}{Colors.N}\n")
        
        if not self.check_adb():
            return False
        
        if not self.wait_for_device():
            return False
        
        self.check_root()
        self.detect_architecture()
        
        print(f"{Colors.BD}{Colors.Y}[!] This may take a few minutes. DO NOT INTERRUPT!{Colors.N}")
        print(f"{Colors.DIM}[*] You can press Ctrl+C to cancel at any time{Colors.N}")
        
        if not self.find_compatible_version_guaranteed():
            print(f"{Colors.R}[✗] Could not find compatible version{Colors.N}")
            return False
        
        downloaded = self.download_frida_server()
        if not downloaded:
            return False
        
        extracted = self.extract_frida(downloaded)
        if not extracted:
            return False
        
        if not self.push_to_device(extracted):
            return False
        
        self.install_pc_tools()
        self.start_frida_server()
        self.verify_installation()
        
        self.show_success()
        return True
    
    def show_success(self):
        print(f"\n{Colors.BD}{Colors.G}{'='*70}{Colors.N}")
        print(f"{Colors.BD}{Colors.G}🎉 INSTALLATION COMPLETE! 🎉{Colors.N}")
        print(f"{Colors.BD}{Colors.G}{'='*70}{Colors.N}")
        print(f"""
{Colors.C}✓ Version      : {self.version}
{Colors.C}✓ Architecture : {self.arch}
{Colors.C}✓ Device       : {self.device_id}
{Colors.C}✓ Root         : {'Yes' if self.has_root else 'No'}
{Colors.C}✓ Status       : {'Verified' if self.verified else 'Running'}
{Colors.N}
{Colors.G}📌 Quick Commands:{Colors.N}
  {Colors.Y}frida-ps -U{Colors.N}                    - List running processes
  {Colors.Y}frida-ps -Uai{Colors.N}                  - List all installed apps
  {Colors.Y}Option 6 from menu{Colors.N}              - Interactive shell
  {Colors.Y}Option 7 from menu{Colors.N}              - Advanced attach with bypasses
  {Colors.Y}Option 8 from menu{Colors.N}              - Simple attach
  {Colors.Y}frida -U PID{Colors.N}                   - Attach to process by PID
  {Colors.Y}frida -U "App Name"{Colors.N}            - Attach to process by name
  {Colors.Y}frida -U -f com.package.name{Colors.N}   - Spawn and attach to app

{Colors.C}{Colors.BD}जय श्री कृष्णा 🙏{Colors.N}
{Colors.G}📁 All outputs are saved in: {self.output_dir}{Colors.N}
        """)
    
    def run_menu(self):
        while True:
            try:
                logo()
                print(f"""
{Colors.BD}{Colors.C}╔══════════════════════════════════════════════════════════════════╗
║                         MAIN MENU                                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  {Colors.G}1{Colors.C} . 🚀 FULL AUTO INSTALL (100% Success Guaranteed)              ║
║  {Colors.G}2{Colors.C} . 📱 START FRIDA SERVER                                        ║
║  {Colors.G}3{Colors.C} . 🛑 STOP FRIDA SERVER                                        ║
║  {Colors.G}4{Colors.C} . 📊 CHECK STATUS & VERIFY                                    ║
║  {Colors.G}5{Colors.C} . 📋 LIST APPLICATIONS                                        ║
║  {Colors.G}6{Colors.C} . 💻 INTERACTIVE FRIDA SHELL                                  ║
║  {Colors.G}7{Colors.C} . 🔥 ADVANCED ATTACH (With Bypass Options)                    ║
║  {Colors.G}8{Colors.C} . 🎯 SIMPLE ATTACH (With Script Selection)                    ║
║  {Colors.G}9{Colors.C} . 🗑️  UNINSTALL FRIDA                                         ║
║  {Colors.G}0{Colors.C} . ❌ EXIT                                                     ║
╚══════════════════════════════════════════════════════════════════════════╝{Colors.N}
                """)
                
                choice = input(f"{Colors.C}{Colors.BD}krishna@tools~# {Colors.N}").strip()
                
                if choice == '1':
                    if self.full_install():
                        input(f"\n{Colors.G}[✓] Press Enter to continue{Colors.N}")
                    else:
                        input(f"\n{Colors.R}[✗] Installation failed. Press Enter{Colors.N}")
                
                elif choice == '2':
                    if not self.device_id:
                        if not self.wait_for_device(30):
                            input(f"\n{Colors.R}[✗] No device found. Press Enter{Colors.N}")
                            continue
                    self.start_frida_server()
                    print(f"\n{Colors.G}[✓] Press Enter to continue{Colors.N}")
                    input()
                
                elif choice == '3':
                    if self.device_id:
                        self.stop_frida_server()
                    else:
                        print(f"{Colors.Y}[*] No device connected{Colors.N}")
                    input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                
                elif choice == '4':
                    if not self.device_id:
                        self.wait_for_device(10)
                    if self.device_id:
                        self.check_frida_status()
                        self.verify_installation()
                    else:
                        print(f"{Colors.R}[✗] No device connected{Colors.N}")
                    input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                
                elif choice == '5':
                    if not self.device_id:
                        self.wait_for_device(10)
                    if self.device_id:
                        self.list_apps()
                    else:
                        print(f"{Colors.R}[✗] No device connected{Colors.N}")
                    input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                
                elif choice == '6':
                    if not self.device_id:
                        if not self.wait_for_device(10):
                            print(f"{Colors.R}[✗] No device connected. Please connect device first.{Colors.N}")
                            input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                            continue
                    
                    # Check if frida-server is running
                    if not self.check_frida_status():
                        print(f"{Colors.Y}[!] Frida server not running. Starting it now...{Colors.N}")
                        self.start_frida_server()
                    
                    self.interactive_shell()
                    input(f"\n{Colors.Y}[*] Press Enter to return to menu{Colors.N}")
                
                elif choice == '7':
                    if not self.device_id:
                        if not self.wait_for_device(10):
                            print(f"{Colors.R}[✗] No device connected. Please connect device first.{Colors.N}")
                            input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                            continue
                    
                    # Check if frida-server is running
                    if not self.check_frida_status():
                        print(f"{Colors.Y}[!] Frida server not running. Starting it now...{Colors.N}")
                        self.start_frida_server()
                    
                    self.interactive_attach()
                    input(f"\n{Colors.Y}[*] Press Enter to return to menu{Colors.N}")
                
                elif choice == '8':
                    if not self.device_id:
                        if not self.wait_for_device(10):
                            print(f"{Colors.R}[✗] No device connected. Please connect device first.{Colors.N}")
                            input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                            continue
                    
                    # Check if frida-server is running
                    if not self.check_frida_status():
                        print(f"{Colors.Y}[!] Frida server not running. Starting it now...{Colors.N}")
                        self.start_frida_server()
                    
                    self.simple_attach_mode()
                    input(f"\n{Colors.Y}[*] Press Enter to return to menu{Colors.N}")
                
                elif choice == '9':
                    confirm = input(f"{Colors.R}[!] Confirm uninstall? (y/N): {Colors.N}")
                    if confirm.lower() == 'y':
                        self.uninstall()
                    input(f"\n{Colors.Y}[*] Press Enter to continue{Colors.N}")
                
                elif choice == '0':
                    print(f"\n{Colors.G}[✓] जय श्री कृष्णा 🙏{Colors.N}")
                    self.stop_frida_server()
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                    sys.exit(0)
                
                # Clear screen for next iteration (except for interactive modes)
                if choice not in ['6', '7', '8']:
                    os.system('cls' if self.is_windows else 'clear')
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.Y}[!] Ctrl+C detected!{Colors.N}")
                print(f"{Colors.G}[✓] Exiting gracefully...{Colors.N}")
                self.stop_frida_server()
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"{Colors.C}{Colors.BD}जय श्री कृष्णा 🙏{Colors.N}")
                sys.exit(0)
            except Exception as e:
                print(f"{Colors.R}[✗] Unexpected error: {e}{Colors.N}")
                time.sleep(2)

if __name__ == "__main__":
    installer = WindowsFridaInstaller()
    installer.run_menu()
