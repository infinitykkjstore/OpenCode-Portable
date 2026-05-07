#!/usr/bin/env python3

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


if __name__ == "__main__":
    if is_opencode_installed():
        print("Opencode já está instalado.")
    else:
        install_opencode()
