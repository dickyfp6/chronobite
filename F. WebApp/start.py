#!/usr/bin/env python3
"""
🌿 Quick Start Script untuk NutriPlan DSS WebApp
Jalankan script ini untuk setup dan menjalankan aplikasi
"""

import os
import sys
import subprocess
import platform

def print_banner():
    banner = """
    ╔════════════════════════════════════════════╗
    ║     🌿 NutriPlan DSS - Web Application    ║
    ║  Personalized Nutrition Recommendation     ║
    ╚════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version requirement"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ diperlukan!")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} ditemukan")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Menginstal dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies berhasil diinstal")
    except subprocess.CalledProcessError:
        print("❌ Gagal menginstal dependencies")
        sys.exit(1)

def run_app():
    """Run Flask application"""
    print("\n🚀 Menjalankan aplikasi...")
    print("═" * 50)
    print("URL Aplikasi: http://localhost:5000")
    print("═" * 50)
    print("\nTombol CTRL+C untuk menghentikan server\n")
    
    os.system(f"{sys.executable} app.py")

def main():
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Ask user choice
    print("\n📋 Opsi:")
    print("1. Install dependencies + Jalankan app")
    print("2. Hanya jalankan app")
    print("3. Hanya install dependencies")
    
    choice = input("\nPilih opsi (1-3): ").strip()
    
    if choice == "1":
        install_dependencies()
        run_app()
    elif choice == "2":
        run_app()
    elif choice == "3":
        install_dependencies()
    else:
        print("❌ Pilihan tidak valid")
        sys.exit(1)

if __name__ == "__main__":
    main()
