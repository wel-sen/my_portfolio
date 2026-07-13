#!/usr/bin/env python3
"""
IDM Activator GUI - Python Version
A GUI application to activate Internet Download Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import winreg
import os
import sys
import shutil
import subprocess
import ctypes
import webbrowser
import urllib.request
import json
from pathlib import Path


class IDMActivatorGUI:
    def __init__(self):
        self.version = "v4.9.6"
        self.supported_versions = ("v6.42b58 Full", "v6.42b58 Trial", "v6.42b58")
        self.script_dir = Path(__file__).parent.absolute()
        self.src_dir = self.script_dir / "src"
        self.backup_dir = self.script_dir / "backup"
        self.default_dest_dir = Path("C:/Program Files (x86)/Internet Download Manager")
        
        # Initialize GUI
        self.setup_gui()
        self.detect_idm_path()
        
    def setup_gui(self):
        """Setup the main GUI window"""
        self.root = tk.Tk()
        self.root.title(f"IDM Activator GUI {self.version}")
        self.root.geometry("400x280")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Create main frame with less padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # IDM Install Path section
        path_label = ttk.Label(main_frame, text="IDM Install Path:")
        path_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Path entry and browse button frame
        self.path_var = tk.StringVar()
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=35)
        self.path_entry.grid(row=0, column=0, sticky="ew")
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_path)
        browse_btn.grid(row=0, column=1, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # Large blue Activate button
        self.activate_btn = tk.Button(main_frame, text="Activate", 
                                     command=self.activate_idm,
                                     bg="#1f7ce8", fg="white", 
                                     font=("Segoe UI", 10, "bold"),
                                     height=2, relief="flat",
                                     cursor="hand2")
        self.activate_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Hover effects for activate button
        def on_activate_enter(e):
            self.activate_btn.config(bg="#1a6bb8")
        def on_activate_leave(e):
            self.activate_btn.config(bg="#1f7ce8")
        self.activate_btn.bind("<Enter>", on_activate_enter)
        self.activate_btn.bind("<Leave>", on_activate_leave)
        
        # Add Extra FileType Extensions button
        self.extensions_btn = tk.Button(main_frame, text="Add Extra FileType Extensions", 
                                       command=self.update_extensions,
                                       bg="#e1e1e1", fg="black", 
                                       font=("Segoe UI", 9),
                                       height=1, relief="flat",
                                       cursor="hand2")
        self.extensions_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Check for Updates and Repository buttons frame
        updates_frame = ttk.Frame(main_frame)
        updates_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.update_btn = tk.Button(updates_frame, text="Check for Updates", 
                                   command=self.check_updates,
                                   bg="#e1e1e1", fg="black", 
                                   font=("Segoe UI", 9),
                                   height=1, relief="flat",
                                   cursor="hand2")
        self.update_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.repository_btn = tk.Button(updates_frame, text="Repository", 
                                       command=self.open_repository,
                                       bg="#e1e1e1", fg="black", 
                                       font=("Segoe UI", 9),
                                       height=1, relief="flat",
                                       cursor="hand2")
        self.repository_btn.grid(row=0, column=1, sticky="ew")
        
        updates_frame.columnconfigure(0, weight=1)
        updates_frame.columnconfigure(1, weight=1)
        
        # Exit button
        self.exit_btn = tk.Button(main_frame, text="Exit", 
                                 command=self.exit_app,
                                 bg="#e1e1e1", fg="black", 
                                 font=("Segoe UI", 9),
                                 height=1, relief="flat",
                                 cursor="hand2")
        self.exit_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Status label at bottom
        admin_status = "Running with administrative privileges." if self.is_admin() else "Not running as administrator."
        self.status_var = tk.StringVar(value=admin_status)
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Segoe UI", 8))
        status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def is_admin(self):
        """Check if the script is running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        """Restart the script with administrator privileges"""
        if self.is_admin():
            return True
        else:
            try:
                # Use ShellExecuteW with SW_HIDE (0) to hide the CMD window
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{__file__}"', None, 0)
                return False
            except:
                messagebox.showerror("Error", "Failed to request administrator privileges.")
                return False

    def detect_idm_path(self):
        """Detect IDM installation path from registry"""
        idm_path = None
        
        # Try different registry locations
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Internet Download Manager", "InstallPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Internet Download Manager", "InstallPath"),
            (winreg.HKEY_CURRENT_USER, r"Software\DownloadManager", "InstallPath")
        ]
        
        for hkey, subkey, value_name in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    idm_path, _ = winreg.QueryValueEx(key, value_name)
                    break
            except (FileNotFoundError, OSError):
                continue
        
        if idm_path and Path(idm_path).exists():
            self.path_var.set(idm_path)
        else:
            self.path_var.set(str(self.default_dest_dir))

    def browse_path(self):
        """Browse for IDM installation directory"""
        path = filedialog.askdirectory(
            title="Select IDM Installation Directory",
            initialdir=self.path_var.get()
        )
        if path:
            self.path_var.set(path)

    def verify_files(self, file_list):
        """Verify that required files exist"""
        for file_name in file_list:
            file_path = self.src_dir / file_name
            if not file_path.exists():
                messagebox.showerror("Error", f"Source file '{file_name}' not found.")
                return False
        return True

    def verify_destination(self):
        """Verify IDM installation directory and executable"""
        dest_path = Path(self.path_var.get())
        
        if not dest_path.exists():
            messagebox.showerror("Error", f"Directory '{dest_path}' not found.")
            return False
        
        idman_exe = dest_path / "IDMan.exe"
        if not idman_exe.exists():
            messagebox.showerror("Error", f"IDMan.exe not found in '{dest_path}'.")
            return False
        
        return True

    def create_backup(self):
        """Create backup of existing files and registry"""
        try:
            # Remove existing backup directory
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            # Create new backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup IDMan.exe
            dest_path = Path(self.path_var.get())
            idman_exe = dest_path / "IDMan.exe"
            if idman_exe.exists():
                shutil.copy2(idman_exe, self.backup_dir / "IDMan_backup.exe")
            
            # Backup registry
            backup_reg = self.backup_dir / "Registry_backup.reg"
            subprocess.run([
                "reg", "export", 
                r"HKCU\Software\DownloadManager", 
                str(backup_reg), "/y"
            ], check=True, capture_output=True)
            
            return True
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            return False

    def get_idm_version(self):
        """Get IDM version from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\DownloadManager") as key:
                version, _ = winreg.QueryValueEx(key, "idmvers")
                return version
        except (FileNotFoundError, OSError):
            return None

    def check_idm_version(self):
        """Check if IDM version is supported"""
        version = self.get_idm_version()
        if not version:
            messagebox.showerror("Error", "Unable to determine IDM version from registry.")
            return False
        
        if version not in self.supported_versions:
            messagebox.showerror("Error", 
                f"Unsupported IDM version '{version}'. "
                f"Supported versions are {', '.join(self.supported_versions)}.")
            return False
        
        return True

    def terminate_idm(self):
        """Terminate IDM process if running"""
        try:
            subprocess.run(["taskkill", "/F", "/IM", "IDMan.exe"], 
                          capture_output=True, check=False)
            return True
        except Exception:
            return False

    def apply_registry_file(self, reg_file):
        """Apply registry file"""
        try:
            subprocess.run(["regedit", "/s", str(reg_file)], check=True)
            return True
        except Exception as e:
            messagebox.showerror("Registry Error", f"Failed to apply registry: {str(e)}")
            return False

    def activate_idm(self):
        """Activate IDM"""
        # We already have admin privileges at this point
        self.status_var.set("Activating IDM...")
        self.root.update()
        
        # Verify files
        if not self.verify_files(["data.bin", "Registry.bin"]):
            self.status_var.set("Activation failed - files missing")
            return
        
        # Verify destination
        if not self.verify_destination():
            self.status_var.set("Activation failed - invalid path")
            return
        
        # Check version
        if not self.check_idm_version():
            self.status_var.set("Activation failed - version mismatch")
            return
        
        # Create backup
        if not self.create_backup():
            self.status_var.set("Activation failed - backup error")
            return
        
        # Terminate IDM
        self.terminate_idm()
        
        try:
            # Apply registry
            registry_file = self.src_dir / "Registry.bin"
            if not self.apply_registry_file(registry_file):
                self.status_var.set("Activation failed - registry error")
                return
            
            # Copy data file
            data_file = self.src_dir / "data.bin"
            dest_file = Path(self.path_var.get()) / "IDMan.exe"
            shutil.copy2(data_file, dest_file)
            
            self.status_var.set("IDM activated successfully!")
            messagebox.showinfo("Success", "IDM activated successfully!")
            
        except Exception as e:
            self.status_var.set("Activation failed")
            messagebox.showerror("Error", f"Activation failed: {str(e)}")

    def update_extensions(self):
        """Update file extensions"""
        self.status_var.set("Updating extensions...")
        self.root.update()
        
        # Verify extensions file
        if not self.verify_files(["extensions.bin"]):
            self.status_var.set("Extension update failed - file missing")
            return
        
        try:
            # Apply extensions registry
            extensions_file = self.src_dir / "extensions.bin"
            if self.apply_registry_file(extensions_file):
                self.status_var.set("Extensions updated successfully!")
                messagebox.showinfo("Success", "Extensions updated successfully!")
            else:
                self.status_var.set("Extension update failed")
        except Exception as e:
            self.status_var.set("Extension update failed")
            messagebox.showerror("Error", f"Extension update failed: {str(e)}")

    def check_app_version(self):
        """Check if current app version is the latest"""
        try:
            # Get latest release info from Codeberg API
            url = "https://codeberg.org/api/v1/repos/oop7/IDM-Activator/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'IDM-Activator-GUI'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', '').replace('v', 'V')
                
                if latest_version and latest_version != self.version:
                    return False, latest_version
                else:
                    return True, self.version
        except Exception:
            # If we can't check, assume current version is OK
            return None, self.version

    def check_updates(self):
        """Check for updates"""
        self.status_var.set("Checking for updates...")
        self.root.update()
        
        try:
            is_latest, latest_version = self.check_app_version()
            
            if is_latest is True:
                # Current version is up to date
                self.status_var.set("App is up to date")
                messagebox.showinfo("Up to Date", 
                    f"You have the latest version ({self.version})!")
            elif is_latest is False:
                # New version available
                self.status_var.set(f"New version available: {latest_version}")
                response = messagebox.askyesno("Update Available", 
                    f"A new version ({latest_version}) is available!\n"
                    f"Current version: {self.version}\n\n"
                    "Would you like to open the releases page to download it?")
                
                if response:
                    webbrowser.open("https://codeberg.org/oop7/IDM-Activator/releases/")
                    self.status_var.set("Releases page opened")
                else:
                    self.status_var.set("Update check cancelled")
            else:
                # Couldn't check, open releases page
                self.status_var.set("Could not check version, opening releases page...")
                webbrowser.open("https://codeberg.org/oop7/IDM-Activator/releases/")
                self.status_var.set("Releases page opened")
                
        except Exception as e:
            self.status_var.set("Failed to check for updates")
            messagebox.showerror("Error", f"Failed to check for updates: {str(e)}")

    def open_repository(self):
        """Open repository page"""
        self.status_var.set("Opening repository...")
        try:
            webbrowser.open("https://codeberg.org/oop7/IDM-Activator/")
            self.status_var.set("Repository opened in browser")
        except Exception:
            messagebox.showerror("Error", "Failed to open repository.")
            self.status_var.set("Failed to open repository")

    def exit_app(self):
        """Exit the application"""
        self.root.quit()

    def run(self):
        """Run the application"""
        # Admin privileges already checked in main(), just run the GUI
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        # Check admin privileges before creating GUI
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        
        def run_as_admin():
            try:
                # Use ShellExecuteW with SW_HIDE (0) to hide the CMD window
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{__file__}"', None, 0)
                return True
            except:
                return False
        
        # If not admin, request elevation and exit immediately
        if not is_admin():
            # Create a temporary root window just for the message
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
            
            response = messagebox.askyesno(
                "Administrator Privileges Required", 
                "This application requires administrator privileges to function properly.\n\n"
                "Would you like to restart with administrator privileges?",
                parent=temp_root)
            
            temp_root.destroy()
            
            if response:
                if run_as_admin():
                    sys.exit(0)  # Exit immediately after elevation request
                else:
                    messagebox.showerror("Error", "Failed to request administrator privileges.")
                    sys.exit(1)
            else:
                sys.exit(0)  # User declined, exit
        
        # Only create the main app if we have admin privileges
        app = IDMActivatorGUI()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
