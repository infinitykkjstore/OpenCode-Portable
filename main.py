import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.error


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
        print("AVISO: PERSONAL_TOKEN_GH nao encontrado. gh sera instalado mas nao logado.")
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
        subprocess.run(
            ["bash", "-c", f"gh auth setup-git"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )        
        print("GitHub CLI instalado e logado no git/gh.")

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

    print("Opencode nao encontrado. Instalando...")

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
            print("Erro durante a instalacao.")
            sys.exit(1)

        # recarrega PATH apos instalacao
        ensure_opencode_in_path()

        opencode = get_opencode_path()

        if not opencode:
            print("Instalacao concluida, mas opencode nao foi encontrado.")
            print("PATH atual:", os.environ.get("PATH"))
            sys.exit(1)

        print(f"Instalacao concluida! ({opencode})")

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


def download_file_from_url(url, temp_file_path, final_file_path):
    """
    Faz o download de um arquivo de uma URL e salva no caminho especificado.
    Retorna True se bem-sucedido, False caso contrario.
    """
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; OpenCode/1.0)'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 200:
                print(f"[Init] ERRO: Servidor retornou status {response.status}. Nao foi possivel baixar o arquivo.")
                return False
            file_data = response.read()

        # Salva temporariamente
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_data)

        # Cria o diretorio de destino se nao existir
        final_dir = os.path.dirname(final_file_path)
        os.makedirs(final_dir, exist_ok=True)

        # Move o arquivo para o destino final
        shutil.move(temp_file_path, final_file_path)

        print(f"[Init] SUCCESS: Arquivo salvo com sucesso em {final_file_path}")
        print(f"[Init] Tamanho do arquivo: {len(file_data)} bytes")
        return True

    except urllib.error.URLError as e:
        print(f"[Init] ERRO: Falha ao acessar a URL: {e.reason}")
        return False
    except Exception as e:
        print(f"[Init] ERRO inesperado durante o download/salvamento do arquivo: {e}")
        return False


def process_remote_file(env_var_name, final_file_path):
    """
    Verifica uma variavel de ambiente, faz o download de um arquivo se valido,
    e salva no caminho final especificado.
    """
    file_url = os.environ.get(env_var_name, "").strip()

    # Verifica se a variavel esta definida e nao e vazia
    if not file_url:
        print(f"[Init] {env_var_name} nao definida ou vazia. Ignorando download do arquivo.")
        return

    # Verifica se a URL comeca com http:// ou https://
    if not (file_url.startswith("http://") or file_url.startswith("https://")):
        print(f"[Init] {env_var_name} definida ('{file_url}'), mas nao e uma URL valida (deve comecar com http:// ou https://). Ignorando download.")
        return

    print(f"[Init] {env_var_name} detectada: {file_url}")
    print("[Init] Baixando arquivo...")

    # Define um caminho temporario baseado no nome do arquivo final
    temp_file_path = f"/tmp/{os.path.basename(final_file_path)}_temp"
    
    # Faz o download e salva o arquivo
    download_file_from_url(file_url, temp_file_path, final_file_path)


def download_and_store_opencode_config():
    """
    Verifica a variavel de ambiente CONFIG_OPENCODE_URL.
    Se definida e valida, baixa o arquivo e salva como ~/.config/opencode/opencode.json.
    """
    process_remote_file("CONFIG_OPENCODE_URL", os.path.expanduser("~/.config/opencode/opencode.json"))


def download_and_store_auth():
    """
    Verifica a variavel de ambiente AUTH_FILE_URL.
    Se definida e valida, baixa o arquivo e salva como ~/.local/share/opencode/auth.json.
    """
    process_remote_file("AUTH_FILE_URL", os.path.expanduser("~/.local/share/opencode/auth.json"))


def start_web_server():
    opencode = get_opencode_path()

    if not opencode:
        print("opencode nao encontrado no PATH.")
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
        print("Opencode ja esta instalado.")
        install_github_cli()
    else:
        install_opencode()

    # Verifica e baixa a configuracao remota antes de iniciar o servidor
    download_and_store_opencode_config()
    
    # Verifica e baixa o arquivo de autenticacao remota antes de iniciar o servidor
    download_and_store_auth()

    start_web_server()
