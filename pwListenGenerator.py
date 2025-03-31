import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import string
import random
import itertools

class PasswortGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Passwortlisten-Generator")
        self.root.geometry("700x800")
        
        # Initialisieren der Variablen
        self.num_lists = tk.IntVar(value=2)
        self.min_length = tk.IntVar()
        self.max_length = tk.IntVar()
        self.order = tk.StringVar()
        self.insert_option = tk.BooleanVar()
        self.insert_chars = tk.StringVar()
        self.num_insertions = tk.IntVar(value=1)
        self.generate_all = tk.BooleanVar(value=True)  # Option, alle Kombinationen zu generieren
        self.specific_num = tk.IntVar()
        
        self.words = []
        self.numbers = []
        self.symbols = []
        self.output_file = tk.StringVar()
        
        # Fortschrittsbalken-Referenz (wird in create_widgets gesetzt)
        self.progress = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Erstellen eines Canvas und Scrollbar für die gesamte GUI
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Bindings für Mausrad-Scrollen
        canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas))
        canvas.bind_all("<Button-4>", lambda event: self._on_mousewheel(event, canvas))  # Linux
        canvas.bind_all("<Button-5>", lambda event: self._on_mousewheel(event, canvas))  # Linux
        
        # Inneres Frame
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="center")
        
        # Abschnitt 0: Ausgabedatei auswählen
        frame0 = ttk.LabelFrame(inner_frame, text="0. Ausgabedatei auswählen")
        frame0.pack(padx=10, pady=10, fill="x")
        
        output_frame = ttk.Frame(frame0)
        output_frame.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(output_frame, text="Zieldatei:").pack(side="left", padx=5)
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file)
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True)
        browse_btn = ttk.Button(output_frame, text="Durchsuchen", command=self.browse_output_file)
        browse_btn.pack(side="left", padx=5)
        
        # Abschnitt 1: Anzahl der Listen auswählen
        frame1 = ttk.LabelFrame(inner_frame, text="1. Anzahl der Listen auswählen")
        frame1.pack(padx=10, pady=10, fill="x")
        
        btn_frame = ttk.Frame(frame1)
        btn_frame.pack(pady=5)
        
        up_btn = ttk.Button(btn_frame, text="▲", width=3, command=self.increase_num_lists)
        up_btn.grid(row=0, column=0, padx=5)
        
        self.num_label = ttk.Label(btn_frame, textvariable=self.num_lists, width=5, anchor="center")
        self.num_label.grid(row=0, column=1)
        
        down_btn = ttk.Button(btn_frame, text="▼", width=3, command=self.decrease_num_lists)
        down_btn.grid(row=0, column=2, padx=5)
        
        # Abschnitt 2: Listen laden
        frame2 = ttk.LabelFrame(inner_frame, text="2. Listen laden")
        frame2.pack(padx=10, pady=10, fill="x")
        
        load_words_btn = ttk.Button(frame2, text="Wortliste laden", command=self.load_words)
        load_words_btn.pack(pady=5, fill="x")
        
        load_numbers_btn = ttk.Button(frame2, text="Zahlenliste laden", command=self.load_numbers)
        load_numbers_btn.pack(pady=5, fill="x")
        
        load_symbols_btn = ttk.Button(frame2, text="Sonderzeichenliste laden", command=self.load_symbols)
        load_symbols_btn.pack(pady=5, fill="x")
        
        self.loaded_labels = ttk.Label(frame2, text="Geladene Listen: 0")
        self.loaded_labels.pack(pady=5)
        
        # Abschnitt 3: Passwortlängen festlegen
        frame3 = ttk.LabelFrame(inner_frame, text="3. Passwortlängen festlegen")
        frame3.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame3, text="Minimale Länge:").pack(pady=5, anchor="w", padx=5)
        self.min_entry = ttk.Entry(frame3, textvariable=self.min_length)
        self.min_entry.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(frame3, text="Maximale Länge:").pack(pady=5, anchor="w", padx=5)
        self.max_entry = ttk.Entry(frame3, textvariable=self.max_length)
        self.max_entry.pack(pady=5, padx=5, fill="x")
        
        # Abschnitt 4: Reihenfolge der Elemente bestimmen
        frame4 = ttk.LabelFrame(inner_frame, text="4. Reihenfolge der Elemente bestimmen")
        frame4.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame4, text="Geben Sie die Reihenfolge ein (z.B. wort, zahl, zeichen):").pack(pady=5, anchor="w", padx=5)
        self.order_entry = ttk.Entry(frame4, textvariable=self.order)
        self.order_entry.pack(pady=5, padx=5, fill="x")
        ttk.Label(frame4, text="Verwenden Sie 'wort', 'zahl' und 'zeichen', getrennt durch Kommas oder Leerzeichen.").pack(pady=2, anchor="w", padx=5)
        
        # Abschnitt 5: Option zum Einfügen von Zeichen in Wörter
        frame5 = ttk.LabelFrame(inner_frame, text="5. Option: Zeichen in Wörter einfügen")
        frame5.pack(padx=10, pady=10, fill="x")
        
        insert_check = ttk.Checkbutton(frame5, text="Zeichen in Wörter einfügen", variable=self.insert_option, command=self.toggle_insert_options)
        insert_check.pack(pady=5, anchor="w", padx=5)
        
        insert_frame = ttk.Frame(frame5)
        insert_frame.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(insert_frame, text="Zu einfügende Zeichen:").grid(row=0, column=0, sticky="w")
        self.insert_combo = ttk.Combobox(insert_frame, textvariable=self.insert_chars, values=["Zahlen", "Sonderzeichen", "Beides"], state="disabled")
        self.insert_combo.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(insert_frame, text="Anzahl der Einfügungen pro Wort:").grid(row=1, column=0, sticky="w")
        self.insert_spin = ttk.Spinbox(insert_frame, from_=1, to=10, textvariable=self.num_insertions, state="disabled")
        self.insert_spin.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        insert_frame.columnconfigure(1, weight=1)
        
        # Abschnitt 6: Generierungseinstellungen
        frame6 = ttk.LabelFrame(inner_frame, text="6. Generierungseinstellungen")
        frame6.pack(padx=10, pady=10, fill="x")
        
        generate_options_frame = ttk.Frame(frame6)
        generate_options_frame.pack(pady=5, padx=5, fill="x")
        
        self.all_radio = ttk.Radiobutton(generate_options_frame, text="Alle möglichen Kombinationen generieren", variable=self.generate_all, value=True, command=self.toggle_generate_options)
        self.all_radio.pack(anchor="w", pady=2, padx=5)
        
        self.specific_radio = ttk.Radiobutton(generate_options_frame, text="Eine bestimmte Anzahl von Passwörtern generieren", variable=self.generate_all, value=False, command=self.toggle_generate_options)
        self.specific_radio.pack(anchor="w", pady=2, padx=5)
        
        specific_frame = ttk.Frame(frame6)
        specific_frame.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(specific_frame, text="Anzahl der Passwörter:").pack(side="left", padx=5)
        self.specific_entry = ttk.Entry(specific_frame, textvariable=self.specific_num, state="disabled")
        self.specific_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Abschnitt 7: Passwortliste generieren und speichern
        frame7 = ttk.LabelFrame(inner_frame, text="7. Passwortliste generieren und speichern")
        frame7.pack(padx=10, pady=10, fill="x")
        
        generate_btn = ttk.Button(frame7, text="Passwortliste generieren", command=self.generate_passwords)
        generate_btn.pack(pady=10)
        
        # HIER: Fortschrittsbalken hinzufügen (mode="determinate")
        self.progress = ttk.Progressbar(frame7, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
    
    # Methoden zur Handhabung der Scroll-Events
    def _on_mousewheel(self, event, canvas):
        if event.num == 5 or event.delta == -120:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            canvas.yview_scroll(-1, "units")
    
    # Methoden zur Handhabung der Widgets und Logik
    def increase_num_lists(self):
        current = self.num_lists.get()
        self.num_lists.set(current + 1)
    
    def decrease_num_lists(self):
        current = self.num_lists.get()
        if self.insert_option.get():
            if current > 1:
                self.num_lists.set(current - 1)
        else:
            if current > 2:
                self.num_lists.set(current - 1)
    
    def load_words(self):
        file_path = filedialog.askopenfilename(title="Wortliste auswählen", filetypes=[("Textdateien", "*.txt")])
        if file_path:
            self.words = self.load_list(file_path)
            self.update_loaded_labels()
    
    def load_numbers(self):
        file_path = filedialog.askopenfilename(title="Zahlenliste auswählen", filetypes=[("Textdateien", "*.txt")])
        if file_path:
            self.numbers = self.load_list(file_path)
            self.update_loaded_labels()
    
    def load_symbols(self):
        file_path = filedialog.askopenfilename(title="Sonderzeichenliste auswählen", filetypes=[("Textdateien", "*.txt")])
        if file_path:
            self.symbols = self.load_list(file_path)
            self.update_loaded_labels()
    
    def load_list(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei:\n{e}")
            return []
    
    def update_loaded_labels(self):
        if self.insert_option.get():
            required = 1
        else:
            required = 2
        count = sum([bool(self.words), bool(self.numbers), bool(self.symbols)])
        self.loaded_labels.config(text=f"Geladene Listen: {count} (mindestens {required} erforderlich)")
    
    def toggle_insert_options(self):
        if self.insert_option.get():
            self.insert_combo.config(state="readonly")
            self.insert_spin.config(state="normal")
        else:
            self.insert_combo.set('')
            self.insert_combo.config(state="disabled")
            self.insert_spin.config(state="disabled")
        self.update_loaded_labels()
    
    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Textdateien", "*.txt")],
                                                 title="Ausgabedatei auswählen")
        if file_path:
            self.output_file.set(file_path)
    
    def toggle_generate_options(self):
        if self.generate_all.get():
            self.specific_entry.config(state="disabled")
            self.specific_num.set('')
        else:
            self.specific_entry.config(state="normal")
    
    def generate_passwords(self):
        # --- Fortschrittsbalken zurücksetzen ---
        self.progress['value'] = 0
        
        # Validierung der Ausgabedatei
        output = self.output_file.get()
        if not output:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Ausgabedatei aus.")
            return
        
        # Validierung der geladenen Listen
        if self.insert_option.get():
            min_required = 1
        else:
            min_required = 2
        loaded = sum([bool(self.words), bool(self.numbers), bool(self.symbols)])
        if loaded < min_required:
            messagebox.showerror("Fehler", f"Bitte laden Sie mindestens {min_required} Listen (Wörter, Zahlen, Sonderzeichen).")
            return
        
        # Validierung der Reihenfolge
        order_input = self.order.get().lower()
        # Splitten nach Komma oder Leerzeichen
        if ',' in order_input:
            order = [item.strip() for item in order_input.split(',') if item.strip()]
        else:
            order = [item.strip() for item in order_input.split() if item.strip()]
        
        valid_elements = {'wort', 'zahl', 'zeichen'}
        if not set(order).issubset(valid_elements) or len(order) < 1:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Reihenfolge ein (z.B. wort, zahl, zeichen).")
            return
        
        # Validierung der Passwortlängen
        min_len = self.min_length.get() if self.min_length.get() else None
        max_len = self.max_length.get() if self.max_length.get() else None
        if min_len and max_len and min_len > max_len:
            messagebox.showerror("Fehler", "Minimale Länge darf nicht größer als maximale Länge sein.")
            return
        
        # Option zum Einfügen von Zeichen in Wörter
        insert_option = self.insert_option.get()
        insert_chars_list = []
        num_insertions = self.num_insertions.get()
        if insert_option:
            choice = self.insert_chars.get()
            if choice == "Zahlen":
                insert_chars_list = list(string.digits)
            elif choice == "Sonderzeichen":
                insert_chars_list = list(string.punctuation)
            elif choice == "Beides":
                insert_chars_list = list(string.digits + string.punctuation)
            else:
                messagebox.showerror("Fehler", "Bitte wählen Sie gültige Zeichen zum Einfügen.")
                return
        
        # Generierung der Passwörter
        if self.generate_all.get():
            # Alle möglichen Kombinationen basierend auf der Reihenfolge
            try:
                lists = []
                for elem in order:
                    if elem == 'wort' and self.words:
                        lists.append(self.words)
                    elif elem == 'zahl' and self.numbers:
                        lists.append(self.numbers)
                    elif elem == 'zeichen' and self.symbols:
                        lists.append(self.symbols)
                
                all_combinations = itertools.product(*lists)
                generated_passwords = set()
                
                # --- Anzahl aller Kombinationen berechnen, um den Progressbar zu konfigurieren ---
                total_combos = 1
                for l in lists:
                    total_combos *= len(l)
                self.progress['maximum'] = total_combos
                
                for i, combo in enumerate(all_combinations, start=1):
                    password = ''.join(combo)
                    # Option zum Einfügen von Zeichen in Wörter
                    if insert_option and 'wort' in order:
                        password = self.insert_chars_in_password(password, order, insert_chars_list, num_insertions)
                    
                    # Länge überprüfen
                    pwd_length = len(password)
                    if ((min_len is None or pwd_length >= min_len) and 
                        (max_len is None or pwd_length <= max_len)):
                        generated_passwords.add(password)
                    
                    # Fortschrittsbalken aktualisieren
                    # (z.B. nur alle 1000 Schritte, damit es nicht zu ruckelig wird)
                    if i % 1000 == 0 or i == total_combos:
                        self.progress['value'] = i
                        self.root.update_idletasks()
                
                # Speichern der Passwörter
                try:
                    with open(output, 'w', encoding='utf-8') as f:
                        for pwd in generated_passwords:
                            f.write(pwd + '\n')
                    messagebox.showinfo("Erfolg", f"{len(generated_passwords)} Passwörter wurden in '{output}' gespeichert.")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern der Datei:\n{e}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler bei der Generierung der Passwörter:\n{e}")
        else:
            # Eine bestimmte Anzahl von Passwörtern generieren
            specific_num = self.specific_num.get()
            if specific_num < 1:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Anzahl von Passwörtern ein.")
                return
            
            generated_passwords = set()
            attempts = 0
            max_attempts = specific_num * 10
            
            # Fortschrittsbalken auf Anzahl Versuche oder gewünschte Anzahl Passwörter setzen
            # Du kannst selbst entscheiden, ob du `max_attempts` oder `specific_num` nimmst.
            # Hier nehmen wir max_attempts als Maximum, damit man sieht, wann wirklich Schluss ist.
            self.progress['maximum'] = max_attempts
            
            while len(generated_passwords) < specific_num and attempts < max_attempts:
                pwd = self.create_password(order, insert_option, insert_chars_list, num_insertions)
                if pwd:
                    generated_passwords.add(pwd)
                
                attempts += 1
                self.progress['value'] = attempts
                # Update der GUI
                if attempts % 100 == 0 or attempts == max_attempts:
                    self.root.update_idletasks()
            
            if len(generated_passwords) < specific_num:
                messagebox.showwarning("Warnung", "Maximale Versuche erreicht. Einige Passwörter wurden möglicherweise nicht generiert.")
            
            # Speichern der Passwörter in die Ausgabedatei
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    for pwd in generated_passwords:
                        f.write(pwd + '\n')
                messagebox.showinfo("Erfolg", f"{len(generated_passwords)} Passwörter wurden in '{output}' gespeichert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern der Datei:\n{e}")
    
    def insert_chars_in_password(self, password, order, chars, num_insertions):
        # Finden der Positionen der Wörter in der Reihenfolge
        words_indices = [i for i, elem in enumerate(order) if elem == 'wort']
        if not words_indices:
            return password
        
        # Zerlegen des Passworts in Komponenten
        components = []
        start = 0
        for idx, elem in enumerate(order):
            if elem == 'wort':
                word = self.words[random.randint(0, len(self.words)-1)]
                # Einfügen von Zeichen in das Wort
                word = self.insert_chars_in_word(word, chars, num_insertions)
                components.append(word)
                start += len(word)
            elif elem == 'zahl':
                number = self.numbers[random.randint(0, len(self.numbers)-1)]
                components.append(number)
                start += len(number)
            elif elem == 'zeichen':
                symbol = self.symbols[random.randint(0, len(self.symbols)-1)]
                components.append(symbol)
                start += len(symbol)
        
        return ''.join(components)
    
    def create_password(self, order, insert_option, insert_chars_list, num_insertions):
        components = []
        for elem in order:
            if elem == 'wort' and self.words:
                word = random.choice(self.words)
                if insert_option and insert_chars_list:
                    word = self.insert_chars_in_word(word, insert_chars_list, num_insertions)
                components.append(word)
            elif elem == 'zahl' and self.numbers:
                components.append(random.choice(self.numbers))
            elif elem == 'zeichen' and self.symbols:
                components.append(random.choice(self.symbols))
        
        password = ''.join(components)
        
        # Länge überprüfen
        pwd_length = len(password)
        min_len = self.min_length.get() if self.min_length.get() else 0
        max_len = self.max_length.get() if self.max_length.get() else float('inf')
        if min_len <= pwd_length <= max_len:
            return password
        return None
    
    def insert_chars_in_word(self, word, chars, num_insertions):
        for _ in range(num_insertions):
            if len(word) == 0:
                break
            pos = random.randint(0, len(word))
            char = random.choice(chars)
            word = word[:pos] + char + word[pos:]
        return word

def main():
    root = tk.Tk()
    app = PasswortGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
