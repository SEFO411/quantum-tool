import os
import sys
import time
import pyautogui
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Ekran taraması için yeni kütüphaneler
import cv2
import numpy as np

console = Console()
BASE_DIR = Path(sys.argv[0]).resolve().parent

# PyAutoGUI güvenlik kilidini esnetelim ve hızlandıralım
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  

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
            delay = delays.get(mode, 0.05) # Gecikmeyi aimbot için biraz düşürdük
            sensitivity = self.config.get("mouse_sensitivity", 1.0)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            status_panel = (
                f"[bold gold1]ŞABLON:[/bold gold1] {self.active_template_name} (Yazar: {self.active_author})\n"
                f"[bold red]MOD:[/bold red] {mode.upper()} OPERASYONU\n"
                f"  • Gecikme: {delay}s\n"
                f"  • Hassasiyet: {sensitivity}x\n\n"
                f"[green]KIRMIZI hedef taraması aktif. Durdurmak için CTRL+C yapın.[/green]"
            )
            console.print(Panel(status_panel, title="💠 AIM ACTIVE", border_style="red"))
            
            # Ekran çözünürlüğünü al
            screen_width, screen_height = pyautogui.size()
            
            # Ekranın tam ortasında tarama yapacağımız alanın boyutu (Performans için tüm ekranı değil ortayı tarıyoruz)
            box_width, box_height = 400, 400
            left = (screen_width - box_width) // 2
            top = (screen_height - box_height) // 2

            # Algılanacak Kırmızı Renk Sınırları (HSV Renk Uzayında)
            # Rakiplerin can barı veya kırmızı vurgusu için uygun tonlar
            lower_red1 = np.array([0, 150, 110])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 150, 110])
            upper_red2 = np.array([180, 255, 255])
            
            while True:
                # Belirlenen bölgenin ekran görüntüsünü al
                screenshot = pyautogui.screenshot(region=(left, top, box_width, box_height))
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Kırmızı maskeleme yap (Kırmızı renk spektrumu iki bölgeye yayıldığı için birleştiriyoruz)
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = mask1 + mask2
                
                # Kırmızı piksellerin koordinatlarını bul
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # En büyük kırmızı alanı (en yakın rakibi) seç
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # Eğer tespit edilen alan çok küçük değilse (gürültüleri engellemek için)
                    if cv2.contourArea(largest_contour) > 15: 
                        # Hedefin merkez noktasını hesapla
                        M = cv2.moments(largest_contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            
                            # Tarama alanındaki koordinatı, gerçek ekran koordinatına dönüştür
                            target_x = left + cX
                            target_y = top + cY
                            
                            # Fareyi yumuşakça (veya anında) hedefe kaydır
                            current_x, current_y = pyautogui.position()
                            # Hassasiyete göre yeni konumu hesapla
                            move_x = int(current_x + (target_x - current_x) * sensitivity)
                            move_y = int(current_y + (target_y - current_y) * sensitivity)
                            
                            pyautogui.moveTo(move_x, move_y)
                            
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