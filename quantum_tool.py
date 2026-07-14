import os
import sys
import time
import pyautogui
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Yeni ve hızlı ekran yakalama kütüphaneleri
import cv2
import numpy as np
import mss

console = Console()
BASE_DIR = Path(sys.argv[0]).resolve().parent

# Gecikmeleri tamamen sıfırlıyoruz (Maksimum Hız)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  

class QuantumFinalSuite:
    def __init__(self):
        self.version = "1.2.0-TURBO"
        self.is_running = True
        
        self.config_file = BASE_DIR / "quantum_config.json"
        
        # Canlı Hafıza
        self.active_template_name = "Varsayılan Sistem"
        self.active_author = "Sistem"
        self.target_mode = None  
        
        self.config = self.load_config()
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
            # Aimbot modu seçildiğinde arkadaki uyku süresini çok küçük tutuyoruz
            delays = self.config.get("autopilot_delays", {"Noob": 0.1, "Normal": 0.01, "Espor": 0.001})
            delay = delays.get(mode, 0.001)
            sensitivity = self.config.get("mouse_sensitivity", 1.0)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            status_panel = (
                f"[bold gold1]ŞABLON:[/bold gold1] {self.active_template_name} (Yazar: {self.active_author})\n"
                f"[bold red]MOD:[/bold red] {mode.upper()} OPERASYONU (TÜM EKRAN)\n"
                f"  • Hassasiyet: {sensitivity}x\n\n"
                f"[green]Ultra Hızlı TÜM EKRAN Kırmızı hedef taraması aktif.[/green]\n"
                f"[yellow]Kapatmak için CMD ekranına gelip CTRL+C yapın.[/yellow]"
            )
            console.print(Panel(status_panel, title="💠 TURBO AIM ACTIVE", border_style="red"))
            
            # Genişletilmiş Oyun İçi Kırmızı Renk Sınırları (HSV)
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([165, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            
            # Ultra hızlı ekran yakalayıcıyı başlat (Tüm Ekran)
            with mss.mss() as sct:
                # 1 numaralı ana monitörün tamamını hedefler
                monitor = sct.monitors[1] 
                
                while True:
                    # Tüm ekranın görüntüsünü nanosaniyeler içinde al
                    screenshot = sct.grab(monitor)
                    
                    # Görüntüyü OpenCV formatına çevir
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    
                    # Kırmızı maskeleme yap
                    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                    mask = mask1 + mask2
                    
                    # Kırmızı piksellerin konturlarını (bölgelerini) bul
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        # Ekrandaki en büyük kırmızı alanı seç (Genelde en yakın rakip olur)
                        largest_contour = max(contours, key=cv2.contourArea)
                        
                        # Çok küçük pikselleri (efektleri, mermileri) ele, sadece belirgin hedeflere git (Alan > 25)
                        if cv2.contourArea(largest_contour) > 25: 
                            M = cv2.moments(largest_contour)
                            if M["m00"] != 0:
                                # Hedefin merkez koordinatları
                                target_x = int(M["m10"] / M["m00"])
                                target_y = int(M["m01"] / M["m00"])
                                
                                # Mevcut fare konumunu al
                                current_x, current_y = pyautogui.position()
                                
                                # Hassasiyet (Sensitivity) çarpanına göre yeni konumu hesapla
                                move_x = int(current_x + (target_x - current_x) * sensitivity)
                                move_y = int(current_y + (target_y - current_y) * sensitivity)
                                
                                # Fareyi hedefe kilitle
                                pyautogui.moveTo(move_x, move_y)
                                
                    if delay > 0:
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
                "[3] E-Spor Modu (Turbo Hızlı)\n"
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
        return {"autopilot_delays": {"Noob": 0.1, "Normal": 0.01, "Espor": 0.001}, "mouse_sensitivity": 1.0}

if __name__ == "__main__":
    app = QuantumFinalSuite()
    app.main_menu()