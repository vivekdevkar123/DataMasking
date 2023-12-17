import logging
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import threading
from utils import mask_private_info, configure_logger, load_ner_model

logger = configure_logger(logging)

class MaskingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Masking Tool")

        self.log_text = tk.StringVar()
        self.log_text.set("Logs:\n")

        self.log_label = tk.Label(root, textvariable=self.log_text, justify=tk.LEFT)
        self.log_label.pack(fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(root, text="Start Masking", command=self.start_masking)
        self.start_button.pack()

        self.ner = load_ner_model()

    def start_masking(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])

        if file_path:
            self.log("Masking process started...")
            threading.Thread(target=self.mask_file, args=(file_path,)).start()

    def mask_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                raise ValueError("Unsupported file format")

            data_col = "Verbatim"
            if data_col not in df.columns:
                raise ValueError("Data column not found")

            masked_lines_counter = 0
            processed_lines = 0
            new_texts = []

            df[data_col] = df[data_col].astype(str)

            for text in df[data_col]:
                masked_text = mask_private_info(text, self.ner)
                new_texts.append(masked_text)

                if "*****" in masked_text:
                    masked_lines_counter += 1
                processed_lines += 1

            df["Masked"] = new_texts
            df = df.drop([data_col], axis=1)

            masked_file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                              filetypes=[("CSV files", "*.csv")])
            df.to_csv(masked_file_path, index=False)

            self.log(f"Masking process completed. Masked file saved at: {masked_file_path}")

        except Exception as e:
            logger.error(f"Error during masking process: {str(e)}")

    def log(self, message):
        current_logs = self.log_text.get()
        self.log_text.set(current_logs + message + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = MaskingApp(root)
    root.mainloop()
