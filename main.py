#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys


def is_opencode_installed():
    return shutil.which("opencode") is not None


def install_opencode():
    print("Opencode não encontrado. Instalando...")
    try:
        result = subprocess.run(
            ["curl", "-fsSL", "https://opencode.ai/install"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Erro ao baixar o instalador: {result.stderr}")
            sys.exit(1)

        process = subprocess.run(
            ["bash"],
            input=result.stdout,
            text=True
        )
        if process.returncode != 0:
            print("Erro durante a instalação.")
            sys.exit(1)
        
        print("Instalação concluída!")
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


def start_web_server():
    os.execvp("opencode", ["opencode", "web", "--hostname", "0.0.0.0", "--port", "4096"])


if __name__ == "__main__":
    if is_opencode_installed():
        print("Opencode já está instalado.")
        start_web_server()
    else:
        install_opencode()
        start_web_server()
