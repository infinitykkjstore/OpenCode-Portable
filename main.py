import os
import shutil
import subprocess
import sys


def ensure_opencode_in_path():
    """
    Adiciona dinamicamente possíveis diretórios do opencode ao PATH.
    Funciona em Railway, Render e outros hosts.
    """

    possible_dirs = [
        "/opt/render/.opencode/bin",          # Render
        os.path.expanduser("~/.opencode/bin"),
        os.path.expanduser("~/.local/bin"),   # comum em installers unix
        "/root/.local/bin",
        "/usr/local/bin",
    ]

    current_path = os.environ.get("PATH", "")

    for path in possible_dirs:
        if os.path.isdir(path) and path not in current_path:
            current_path = f"{path}:{current_path}"

    os.environ["PATH"] = current_path


def get_opencode_path():
    ensure_opencode_in_path()
    return shutil.which("opencode")


def is_opencode_installed():
    return get_opencode_path() is not None


def install_opencode():
    print("Preparando ambiente...")

    subprocess.run(
        ["apt", "update"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    subprocess.run(
        ["apt", "install", "-y", "curl"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Opencode não encontrado. Instalando...")

    try:
        result = subprocess.run(
            ["curl", "-fsSL", "https://opencode.ai/install"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Erro ao baixar o instalador:\n{result.stderr}")
            sys.exit(1)

        process = subprocess.run(
            ["bash"],
            input=result.stdout,
            text=True
        )

        if process.returncode != 0:
            print("Erro durante a instalação.")
            sys.exit(1)

        # recarrega PATH após instalação
        ensure_opencode_in_path()

        opencode = get_opencode_path()

        if not opencode:
            print("Instalação concluída, mas opencode não foi encontrado.")
            print("PATH atual:", os.environ.get("PATH"))
            sys.exit(1)

        print(f"Instalação concluída! ({opencode})")

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


def start_web_server():
    opencode = get_opencode_path()

    if not opencode:
        print("opencode não encontrado no PATH.")
        print("PATH atual:", os.environ.get("PATH"))
        sys.exit(1)

    print(f"Iniciando OpenCode usando: {opencode}")

    os.execv(opencode, [
        opencode,
        "web",
        "--hostname",
        "0.0.0.0",
        "--port",
        "4096"
    ])


if __name__ == "__main__":

    ensure_opencode_in_path()

    if is_opencode_installed():
        print("Opencode já está instalado.")
    else:
        install_opencode()

    start_web_server()
