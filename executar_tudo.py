
#!/usr/bin/env python3
# #somente para executar os outros codigos
import sys
import subprocess
import platform
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCRIPTS = [
    "roteador.py",
    "servidor_central.py",
    "cliente_a_gui.py",
    "cliente_b_gui.py",
]


def run_in_new_terminal(path: Path) -> None:
    system = platform.system()
    if system == "Windows":
        cmd = (
            f"start powershell -NoExit -Command \"& '{sys.executable}' '{path}'\""
        )
        subprocess.Popen(cmd, shell=True)
    else:
        subprocess.Popen([sys.executable, str(path)])


def main():
    for script in SCRIPTS:
        path = HERE / script
        if not path.exists():
            print(f"Erro: script nao encontrado: {path}")
            sys.exit(1)
        print(f"Abrindo terminal para {script}...")
        run_in_new_terminal(path)
    print("Comando de abertura enviado para todos os scripts.")


if __name__ == "__main__":
    main()
