import os
import time
import threading
import pyttsx3
import pyautogui
import json
import logging
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Logging ayarları
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / f"quantum_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class QuantumFinalSuite:
    def __init__(self):
        self.version = "0.0.1-BETA"
        self.ai_mode = "Dev-Mode"
        self.is_running = True
        self.ide_code = "print('Quantum IDE Aktif!')\n# Buraya Python kodunu yaz..."
        self.config_file = Path("quantum_config.json")
        self.history_file = Path("ide_history.json")
        self.stats_file = Path("quantum_stats.json")
        
        # Ses motoru ayarları
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            logging.info("Ses motoru başlatıldı")
        except Exception as e:
            logging.error(f"Ses motoru hatası: {e}")
            console.print(f"[yellow]⚠️ Ses motoru başlatılamadı: {e}[/yellow]")
            self.engine = None
        
        # Yapılandırma yükleme
        self.config = self.load_config()
        self.ide_history = self.load_history()
        self.stats = self.load_stats()
        
        logging.info(f"Quantum Tool v{self.version} başlatıldı")

    def speak(self, text):
        """Asistanı seslendirir."""
        if self.engine is None or not self.config.get("voice_enabled", True):
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            logging.info(f"Sesli uyarı: {text[:50]}")
        except Exception as e:
            logging.error(f"Sesli uyarı hatası: {e}")
    
    # ============ KONFIGÜRASYON YÖNETİMİ ============
    
    def load_config(self):
        """Yapılandırma dosyasını yükler."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    logging.info("Yapılandırma yüklendi")
                    return json.load(f)
        except Exception as e:
            logging.error(f"Yapılandırma yükleme hatası: {e}")
        
        return self.get_default_config()
    
    def get_default_config(self):
        """Varsayılan yapılandırmayı döndürür."""
        return {
            "voice_enabled": True,
            "voice_speed": 160,
            "theme": "monokai",
            "autopilot_delays": {"Noob": 1.2, "Normal": 0.4, "Espor": 0.05},
            "mouse_sensitivity": 1.0,
            "keyboard_delay": 0.1
        }
    
    def save_config(self):
        """Yapılandırmayı kaydeder."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("Yapılandırma kaydedildi")
            console.print("[green]✓ Yapılandırma kaydedildi[/green]")
        except Exception as e:
            logging.error(f"Yapılandırma kaydetme hatası: {e}")
            console.print(f"[red]✗ Kaydetme hatası: {e}[/red]")
    
    # ============ İSTATİSTİKLER ============
    
    def load_stats(self):
        """İstatistikleri yükler."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"İstatistik yükleme hatası: {e}")
        
        return {"noob_uses": 0, "normal_uses": 0, "espor_uses": 0, "ide_executions": 0, "last_used": None}
    
    def update_stats(self, mode):
        """İstatistikleri günceller."""
        try:
            key = f"{mode.lower()}_uses"
            if key in self.stats:
                self.stats[key] += 1
            self.stats["last_used"] = datetime.now().isoformat()
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=4, ensure_ascii=False)
            logging.info(f"İstatistik güncellendi: {mode}")
        except Exception as e:
            logging.error(f"İstatistik güncelleme hatası: {e}")
    
    def show_stats(self):
        """İstatistikleri gösterir."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        table = Table(title="📊 QUANTUM TOOL İSTATİSTİKLERİ", border_style="cyan")
        table.add_column("Mod", style="cyan")
        table.add_column("Kullanım Sayısı", style="yellow")
        
        table.add_row("Noob Modu", str(self.stats.get("noob_uses", 0)))
        table.add_row("Normal Mod", str(self.stats.get("normal_uses", 0)))
        table.add_row("E-Spor Modu", str(self.stats.get("espor_uses", 0)))
        
        console.print(table)
        console.print(f"\n[green]IDE Çalıştırılma:[/green] {self.stats.get('ide_executions', 0)} kez")
        console.print(f"[green]Son kullanım:[/green] {self.stats.get('last_used', 'Hiç')}")
        console.print(f"[green]Toplam Sesson:[/green] {sum(self.stats.values()) - 1}")
        
        Prompt.ask("\n[cyan]Devam etmek için ENTER'a basın[/cyan]")
    
    # ============ IDE GEÇMİŞİ VE DOSYA YÖNETİMİ ============
    
    def load_history(self):
        """IDE geçmişini yükler."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    logging.info("IDE geçmişi yüklendi")
                    return json.load(f)
        except Exception as e:
            logging.error(f"Geçmiş yükleme hatası: {e}")
        return []
    
    def save_to_history(self, code):
        """Kodu geçmişe kaydeder."""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "code": code,
                "length": len(code)
            }
            self.ide_history.append(history_entry)
            
            if len(self.ide_history) > 50:
                self.ide_history = self.ide_history[-50:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.ide_history, f, indent=4, ensure_ascii=False)
            logging.info("Kod geçmişe kaydedildi")
        except Exception as e:
            logging.error(f"Geçmişe kaydetme hatası: {e}")
    
    def save_code_to_file(self, filename=None):
        """Kodu dosyaya kaydeder."""
        if filename is None:
            filename = Prompt.ask("Dosya adı (uzantı hariç)", default="quantum_script")
        
        try:
            filepath = Path(f"saved_codes/{filename}.py")
            filepath.parent.mkdir(exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.ide_code)
            logging.info(f"Kod kaydedildi: {filepath}")
            console.print(f"[green]✓ Kod kaydedildi: {filepath}[/green]")
        except Exception as e:
            logging.error(f"Dosyaya kaydetme hatası: {e}")
            console.print(f"[red]✗ Kaydetme hatası: {e}[/red]")
    
    def load_code_from_file(self):
        """Dosyadan kodu yükler."""
        try:
            codes_dir = Path("saved_codes")
            if not codes_dir.exists():
                console.print("[yellow]Kaydedilmiş kod yok[/yellow]")
                return
            
            files = list(codes_dir.glob("*.py"))
            if not files:
                console.print("[yellow]Kaydedilmiş kod yok[/yellow]")
                return
            
            for i, f in enumerate(files, 1):
                console.print(f"[{i}] {f.stem}")
            
            choice = Prompt.ask("Seç", choices=[str(i) for i in range(1, len(files) + 1)])
            self.ide_code = files[int(choice) - 1].read_text(encoding='utf-8')
            logging.info(f"Kod yüklendi: {files[int(choice) - 1]}")
            console.print("[green]✓ Kod yüklendi[/green]")
        except Exception as e:
            logging.error(f"Dosyadan yükleme hatası: {e}")
            console.print(f"[red]✗ Yükleme hatası: {e}[/red]")
    
    def show_history(self):
        """Geçmiş kodları gösterir."""
        if not self.ide_history:
            console.print("[yellow]Geçmiş boş[/yellow]")
            return
        
        for i, entry in enumerate(self.ide_history[-10:], 1):
            time_str = entry["timestamp"]
            code_preview = entry["code"][:40].replace('\n', ' ')
            console.print(f"[{i}] {time_str} - {code_preview}...")

    # ============ GELİŞMİŞ OTOPİLOT ============
    
    def autopilot_logic(self, mode):
        """Seçilen moda göre otopilot tepki mekanizması."""
        try:
            delays = self.config.get("autopilot_delays", {"Noob": 1.2, "Normal": 0.4, "Espor": 0.05})
            delay = delays.get(mode, 0.5)
            mouse_sensitivity = self.config.get("mouse_sensitivity", 1.0)
            
            # İstatistik güncelle
            self.update_stats(mode)
            
            # Sorumluluk reddi ve sesli uyarı
            os.system('cls' if os.name == 'nt' else 'clear')
            warning = f"{mode.upper()} MODU AKTİF. Ban riski kullanıcıya aittir!"
            console.print(Panel(f"[bold red]{warning}[/bold red]", border_style="red"))
            self.speak(warning)
            
            console.print(f"\n[cyan]⚙️ AYARLAR:[/cyan]")
            console.print(f"  • Hız Gecikmesi: {delay}s")
            console.print(f"  • Fare Duyarlılığı: {mouse_sensitivity}x")
            console.print(f"\n[cyan][*] {mode} Otopilotu arka planda çalışıyor... (Çıkış için CTRL+C)[/cyan]")
            
            time.sleep(2)
            
            try:
                iteration = 0
                while True:
                    iteration += 1
                    # Mouse hareketini simüle et
                    x, y = pyautogui.position()
                    # pyautogui.moveTo(x + 1, y + 1)  # Gerçek kullanımda aç
                    time.sleep(delay)
                    
                    if iteration % 100 == 0:
                        console.print(f"[yellow]⏱️ Çalışma süresi: {iteration * delay:.1f}s[/yellow]", end='\r')
                        
            except KeyboardInterrupt:
                console.print(f"\n[yellow][!] {mode} Otopilotu durduruldu.[/yellow]")
                console.print(f"[green]✓ Toplam çalışma: {iteration * delay:.1f} saniye[/green]")
                logging.info(f"{mode} modu durduruldu: {iteration * delay:.1f}s çalışma")
                time.sleep(1)
        
        except Exception as e:
            logging.error(f"Otopilot hatası ({mode}): {e}")
            console.print(f"[red]✗ Otopilot hatası: {e}[/red]")
    
    # ============ AYARLAR MENÜSÜ ============
    
    def settings_menu(self):
        """Ayarlar menüsü."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(Panel(
                "[1] Ses: " + ("[green]✓ Açık[/green]" if self.config.get("voice_enabled") else "[red]✗ Kapalı[/red]") + "\n"
                "[2] Ses Hızı (şu an: " + str(self.config.get("voice_speed", 160)) + ")\n"
                "[3] Fare Duyarlılığı (şu an: " + str(self.config.get("mouse_sensitivity", 1.0)) + "x)\n"
                "[4] Otopilot Hız Ayarları\n"
                "[5] Varsayılanlara Sıfırla\n"
                "[Q] Geri",
                title="⚙️ AYARLAR", border_style="yellow"
            ))
            
            choice = Prompt.ask("Seçim", choices=["1", "2", "3", "4", "5", "q"], default="q")
            
            try:
                if choice == "1":
                    self.config["voice_enabled"] = not self.config.get("voice_enabled", True)
                    self.save_config()
                elif choice == "2":
                    speed = int(Prompt.ask("Ses Hızı (75-300)", default="160"))
                    if 75 <= speed <= 300:
                        self.config["voice_speed"] = speed
                        if self.engine:
                            self.engine.setProperty('rate', speed)
                        self.save_config()
                    else:
                        console.print("[red]Geçersiz değer (75-300)[/red]")
                elif choice == "3":
                    sensitivity = float(Prompt.ask("Fare Duyarlılığı (0.1-5.0)", default="1.0"))
                    if 0.1 <= sensitivity <= 5.0:
                        self.config["mouse_sensitivity"] = sensitivity
                        self.save_config()
                    else:
                        console.print("[red]Geçersiz değer (0.1-5.0)[/red]")
                elif choice == "4":
                    self.customize_autopilot_speeds()
                elif choice == "5":
                    self.config = self.get_default_config()
                    self.save_config()
                    console.print("[green]✓ Varsayılanlara sıfırlandı[/green]")
                    time.sleep(1)
                elif choice == "q":
                    break
            except Exception as e:
                logging.error(f"Ayarlar menüsü hatası: {e}")
                console.print(f"[red]✗ Hata: {e}[/red]")
                time.sleep(1)
    
    def customize_autopilot_speeds(self):
        """Otopilot hızlarını özelleştirir."""
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print("[yellow]Otopilot Hız Özelleştirmesi[/yellow]\n")
        
        delays = self.config.get("autopilot_delays", {"Noob": 1.2, "Normal": 0.4, "Espor": 0.05})
        
        try:
            for mode in ["Noob", "Normal", "Espor"]:
                current = delays.get(mode, 0.5)
                new_speed = float(Prompt.ask(f"{mode} Modu Gecikmesi (saniye)", default=str(current)))
                if new_speed > 0:
                    delays[mode] = new_speed
            
            self.config["autopilot_delays"] = delays
            self.save_config()
            console.print("[green]✓ Hızlar güncellendi[/green]")
        except Exception as e:
            logging.error(f"Hız özelleştirme hatası: {e}")
            console.print(f"[red]✗ Hata: {e}[/red]")
        
        time.sleep(1)

    def run_ide(self):
        """Dahili Python IDE sistemi."""
        while True:
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                syntax = Syntax(self.ide_code, "python", theme=self.config.get("theme", "monokai"), line_numbers=True)
                console.print(Panel(syntax, title="Quantum IDE v1.0", border_style="green"))
                
                console.print("\n[bold yellow]Komutlar:[/bold yellow]")
                console.print("[E] Düzenle | [R] Çalıştır | [K] Geçmiş | [Y] Yükle | [S] Kaydet | [T] Temizle | [Q] Menüye Dön")
                cmd = Prompt.ask("Seçiminiz", choices=["e", "r", "k", "y", "s", "t", "q"], default="e")

                if cmd == "e":
                    new_code = Prompt.ask("Yeni Kod Satırı Ekle (veya kodun tamamını yapıştır)")
                    self.ide_code += "\n" + new_code if self.ide_code else new_code
                
                elif cmd == "r":
                    console.print("\n[bold cyan]--- ÇIKTI ---[/bold cyan]")
                    try:
                        self.stats["ide_executions"] += 1
                        exec(self.ide_code)
                        self.save_to_history(self.ide_code)
                        logging.info("Kod başarıyla çalıştırıldı")
                    except Exception as e:
                        logging.error(f"Kod çalıştırma hatası: {e}")
                        console.print(f"[red]Hata: {e}[/red]")
                    Prompt.ask("\nDevam etmek için ENTER'a basın")
                
                elif cmd == "k":
                    self.show_history()
                    Prompt.ask("\nDevam etmek için ENTER'a basın")
                
                elif cmd == "y":
                    self.load_code_from_file()
                    time.sleep(1)
                
                elif cmd == "s":
                    self.save_code_to_file()
                    time.sleep(1)
                
                elif cmd == "t":
                    confirm = Prompt.ask("Kodu temizle?", choices=["e", "h"], default="h")
                    if confirm == "e":
                        self.ide_code = ""
                        console.print("[green]✓ Kod temizlendi[/green]")
                        time.sleep(1)
                
                elif cmd == "q":
                    break
            
            except Exception as e:
                logging.error(f"IDE hatası: {e}")
                console.print(f"[red]✗ IDE Hatası: {e}[/red]")
                time.sleep(1)

    def main_menu(self):
        """Ana menü sistemi."""
        while True:
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                menu_text = (
                    "[1] [green]Noob Modu[/green] (Güvenli/Yavaş)\n"
                    "[2] [yellow]Normal Mod[/yellow] (Dengeli)\n"
                    "[3] [red]E-Spor Modu[/red] (Ultra Hızlı/Riskli)\n"
                    "[4] [blue]Quantum IDE[/blue] (Kod Geliştirme)\n"
                    "[5] [magenta]İstatistikler[/magenta]\n"
                    "[6] [cyan]Ayarlar[/cyan]\n"
                    "[Q] Çıkış"
                )
                console.print(Panel(menu_text, title=f"QUANTUM TOOL v{self.version}", subtitle="Tüm Özellikler Aktif", border_style="cyan"))
                
                choice = Prompt.ask("Seçim", choices=["1", "2", "3", "4", "5", "6", "q"], default="q")
                
                if choice in ["1", "2", "3"]:
                    mode_map = {"1": "Noob", "2": "Normal", "3": "Espor"}
                    self.autopilot_logic(mode_map[choice])
                elif choice == "4":
                    self.run_ide()
                elif choice == "5":
                    self.show_stats()
                elif choice == "6":
                    self.settings_menu()
                elif choice == "q":
                    console.print("[bold cyan]Quantum Tool Kapatılıyor...[/bold cyan]")
                    logging.info("Quantum Tool kapandı")
                    break
            
            except Exception as e:
                logging.error(f"Ana menü hatası: {e}")
                console.print(f"[red]✗ Menü Hatası: {e}[/red]")
                time.sleep(1)

if __name__ == "__main__":
    app = QuantumFinalSuite()
    app.main_menu()