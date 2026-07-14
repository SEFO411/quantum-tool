import os
import sys
import time
import pyautogui
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
BASE_DIR = Path(sys.argv[0]).resolve().parent

class QuantumFinalSuite:
    def __init__(self):
        self.version = "1.1.0-SILENT"
        self.is_running = True
        
        self.config_file = BASE_DIR / "quantum_config.json"
        
        # Canlı Hafıza
        self.active_template_name = "Varsayılan Sistem"
        self.active_author = "Sistem"
        self.target_mode = None  
        
        self.config = self.load_config()
        
        # Çift Tıklama Kontrolü
        self.check_file_trigger()

    def check_file_trigger(self):
        if len(sys.argv) > 1:
            file_path = Path(sys.argv[1]).resolve()
            if file_path.exists() and file_path.suffix == ".quantumtool":
                self.integrate_external_file(file_path)

    def integrate_external_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.active_template_name = data.get("template_name", "Bilinmeyen Şablon")
            self.active_author = data.get("author", "Bilinmeyen Yazar")
            self.target_mode = data.get("target_mode", "Normal")
            
            if "custom_delays" in data:
                self.config["autopilot_delays"] = data["custom_delays"]
            if "custom_sensitivity" in data:
                self.config["mouse_sensitivity"] = data["custom_sensitivity"]
                
            os.system('cls' if os.name == 'nt' else 'clear')
            welcome_msg = (
                f"[bold green]✓ Şablon Sisteme Entegre Edildi[/bold green]\n\n"
                f"[cyan]Şablon Adı  :[/cyan] {self.active_template_name}\n"
                f"[cyan]Geliştirici :[/cyan] {self.active_author}\n"
                f"[cyan]Hedef Mod   :[/cyan] {self.target_mode}\n\n"
                f"[magenta]Sistem doğrudan entegre modda çalıştırılıyor...[/magenta]"
            )
            console.print(Panel(welcome_msg, title="💠 QUANTUM ENGINE", border_style="green"))
            time.sleep(1.5)
            
        except Exception as e:
            console.print(f"[red]✗ Entegrasyon Hatası: {e}[/red]")
            time.sleep(3)

    def autopilot_logic(self, mode):
        try:
            delays = self.config.get("autopilot_delays", {"Noob": 1.2, "Normal": 0.4, "Espor": 0.05})
            delay = delays.get(mode, 0.4)
            sensitivity = self.config.get("mouse_sensitivity", 1.0)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            status_panel = (
                f"[bold gold1]ŞABLON:[/bold gold1] {self.active_template_name} (Yazar: {self.active_author})\n"
                f"[bold red]MOD:[/bold red] {mode.upper()} OPERASYONU\n"
                f"  • Gecikme: {delay}s\n"
                f"  • Hassasiyet: {sensitivity}x\n\n"
                f"[green]Sistem sessiz modda devrede. Durdurmak için CTRL+C yapın.[/green]"
            )
            console.print(Panel(status_panel, title="💠 CORE ACTIVE", border_style="magenta"))
            
            while True:
                x, y = pyautogui.position() 
                time.sleep(delay)
                
        except KeyboardInterrupt:
            console.print(f"\n[yellow][!] Operasyon durduruldu.[/yellow]")
            time.sleep(1)
            sys.exit()

    def main_menu(self):
        if self.target_mode:
            self.autopilot_logic(self.target_mode)
            return

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            menu_text = (
                "[1] Noob Modu (Yavaş)\n"
                "[2] Normal Mod (Dengeli)\n"
                "[3] E-Spor Modu (Hızlı)\n"
                "[Q] Çıkış"
            )
            console.print(Panel(menu_text, title="QUANTUM SUITE", border_style="cyan"))
            choice = Prompt.ask("Seçim", choices=["1", "2", "3", "q"], default="q")
            
            if choice in ["1", "2", "3"]:
                mode_map = {"1": "Noob", "2": "Normal", "3": "Espor"}
                self.autopilot_logic(mode_map[choice])
            elif choice == "q":
                break

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f: return json.load(f)
            except: pass
        return {"autopilot_delays": {"Noob": 1.2, "Normal": 0.4, "Espor": 0.05}, "mouse_sensitivity": 1.0}

if __name__ == "__main__":
    app = QuantumFinalSuite()
    app.main_menu()