import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os

class QuantumToolBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantumTool Uzantı Yapıcı v2.1 - Stabil Sürüm")
        self.root.geometry("700x800")
        
        self.current_file = None
        self.target_dir = os.path.dirname(os.path.abspath(__file__))
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Yeni Şablon", command=self.new_template)
        filemenu.add_command(label="Farklı Kaydet...", command=self.save_as_template)
        filemenu.add_separator()
        filemenu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=filemenu)
        self.root.config(menu=menubar)

        # Hatalı olan 'shadow=False' parametresi buradan tamamen kaldırıldı
        dir_frame = ttk.LabelFrame(self.root, text=" 📂 Kayıt Klasörü Ayarı (Ana Uygulamanın Klasörü) ", padding=10)
        dir_frame.pack(fill="x", padx=15, pady=5)
        
        self.lbl_dir = ttk.Label(dir_frame, text=self.target_dir, font=("Arial", 8, "italic"), wraplength=450)
        self.lbl_dir.pack(side="left", fill="x", expand=True)
        
        btn_browse = ttk.Button(dir_frame, text="Klasör Seç", command=self.browse_folder)
        btn_browse.pack(side="right")

        frame = ttk.LabelFrame(self.root, text=" Meta Veriler ", padding=10)
        frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame, text="Şablon Adı:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_name = ttk.Entry(frame, width=40)
        self.ent_name.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Yazar:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_author = ttk.Entry(frame, width=40)
        self.ent_author.grid(row=1, column=1, pady=5, padx=5)

        content_frame = ttk.LabelFrame(self.root, text=" Tema & Özellik Kodu (Python) ", padding=10)
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.txt_content = tk.Text(content_frame, wrap="word", undo=True)
        self.txt_content.pack(fill="both", expand=True)

        btn_save = tk.Button(self.root, text="💾 ŞABLONU DOĞRUDAN KAYDET", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.quick_save)
        btn_save.pack(fill="x", padx=15, pady=10, ipady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.target_dir, title="Ana Uygulamanın 'saved_templates' Klasörünü Seçin")
        if folder:
            self.target_dir = folder
            self.lbl_dir.config(text=folder)

    def new_template(self):
        self.ent_name.delete(0, tk.END)
        self.ent_author.delete(0, tk.END)
        self.txt_content.delete("1.0", tk.END)
        self.current_file = None

    def quick_save(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Uyarı", "Lütfen şablona bir ad verin.")
            return

        safe_filename = "".join([c for c in name.lower() if c.isalnum() or c in (" ", "_", "-")]).replace(" ", "_")
        self.current_file = os.path.join(self.target_dir, f"{safe_filename}.quantumtool")
        self.execute_save()

    def save_as_template(self):
        file_path = filedialog.asksaveasfilename(
            initialdir=self.target_dir,
            defaultextension=".quantumtool",
            filetypes=[("QuantumTool Files", "*.quantumtool")],
            title="Şablonu Kaydet"
        )
        if file_path:
            self.current_file = file_path
            self.execute_save()

    def execute_save(self):
        template_data = {
            "template_name": self.ent_name.get(),
            "author": self.ent_author.get() if self.ent_author.get() else "QuantumBuilder",
            "version": "0.0.1",
            "content": self.txt_content.get("1.0", "end-1c")
        }

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Başarılı", f"Şablon başarıyla kaydedildi!\n\nKonum:\n{self.current_file}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yazılamadı:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumToolBuilder(root)
    root.mainloop()