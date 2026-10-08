import customtkinter as ctk
import threading
from datetime import datetime

# Configure the appearance of the GUI
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MDPIAutomatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MDPI Campaign Automator")
        self.geometry("800x600")
        self.minsize(800, 600)

        # Configure grid layout (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ============ LEFT FRAME: INPUTS ============
        self.input_frame = ctk.CTkFrame(self, corner_radius=10)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self.input_frame, text="Campaign Setup", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Credentials
        self.entry_email = ctk.CTkEntry(self.input_frame, placeholder_text="MDPI Email")
        self.entry_email.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.entry_password = ctk.CTkEntry(self.input_frame, placeholder_text="MDPI Password", show="*")
        self.entry_password.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Years Filter
        self.year_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.year_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.year_frame.grid_columnconfigure((0, 1), weight=1)

        current_year = datetime.now().year
        self.entry_start_year = ctk.CTkEntry(self.year_frame, placeholder_text=f"Start Year (e.g. {current_year-2})")
        self.entry_start_year.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.entry_end_year = ctk.CTkEntry(self.year_frame, placeholder_text=f"End Year (e.g. {current_year})")
        self.entry_end_year.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

        # Keywords
        self.label_keywords = ctk.CTkLabel(self.input_frame, text="Keywords (One per line):")
        self.label_keywords.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.textbox_keywords = ctk.CTkTextbox(self.input_frame, height=150)
        self.textbox_keywords.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="ew")

        # Start Button
        self.btn_start = ctk.CTkButton(self.input_frame, text="Start Campaign", command=self.start_campaign_thread, height=40)
        self.btn_start.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")


        # ============ RIGHT FRAME: LOGS ============
        self.log_frame = ctk.CTkFrame(self, corner_radius=10)
        self.log_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        self.label_log = ctk.CTkLabel(self.log_frame, text="Process Logs", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_log.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.textbox_logs = ctk.CTkTextbox(self.log_frame, state="disabled", wrap="word")
        self.textbox_logs.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def log_message(self, message):
        """Helper to print logs to the GUI securely from any thread."""
        self.textbox_logs.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.textbox_logs.insert("end", f"[{timestamp}] {message}\n")
        self.textbox_logs.configure(state="disabled")
        self.textbox_logs.see("end")

    def start_campaign_thread(self):
        """Starts the backend process in a separate thread so GUI doesn't freeze."""
        # Validate inputs first
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        start_year = self.entry_start_year.get().strip()
        end_year = self.entry_end_year.get().strip()
        keywords = self.textbox_keywords.get("1.0", "end").strip().split('\n')
        keywords = [k.strip() for k in keywords if k.strip()]

        if not email or not password:
            self.log_message("ERROR: Please enter MDPI credentials.")
            return
        if not keywords:
            self.log_message("ERROR: Please enter at least one keyword.")
            return

        self.btn_start.configure(state="disabled", text="Running...")
        self.log_message("Starting campaign automation...")
        self.log_message(f"Keywords loaded: {len(keywords)}")
        
        # Run in thread
        threading.Thread(target=self.run_automation_logic, args=(email, password, start_year, end_year, keywords), daemon=True).start()

    def run_automation_logic(self, email, password, start_year, end_year, keywords):
        """This function will hold the actual web scraping and data processing code."""
        try:
            # TODO: Add playwright script here
            # TODO: Add pandas data processing here
            
            self.log_message("Phase 1 & 2 placeholder: Done!")
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
        finally:
            self.btn_start.configure(state="normal", text="Start Campaign")

if __name__ == "__main__":
    app = MDPIAutomatorApp()
    app.mainloop()
