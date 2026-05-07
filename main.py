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


def install_github_cli():
    print("Instalando GitHub CLI...")
    token = os.environ.get("PERSONAL_TOKEN_GH")
    if not token:
        print("AVISO: PERSONAL_TOKEN_GH não encontrado. gh será instalado mas não logado.")
        token = ""

    deb_path = "/tmp/gh_latest.deb"

    subprocess.run(
        ["curl", "-fsSL", "-o", deb_path,
         "https://github.com/cli/cli/releases/download/v2.92.0/gh_2.92.0_linux_amd64.deb"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    subprocess.run(
        ["dpkg", "-i", deb_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    subprocess.run(
        ["apt", "install", "-f", "-y"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if token:
        subprocess.run(
            ["bash", "-c", f"echo {token} | gh auth login --with-token"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("GitHub CLI instalado e logado.")

    os.remove(deb_path)


def install_opencode():
    print("Preparando ambiente...")

    subprocess.run(
        ["apt", "update"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    subprocess.run(
        ["apt", "install", "-y", "curl", "wget", "nano"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    install_github_cli()

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
        install_github_cli()
    else:
        install_opencode()

    start_web_server()
