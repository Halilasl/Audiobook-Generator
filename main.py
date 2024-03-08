import os
import PyPDF2
from gtts import gTTS
from googletrans import Translator
from langdetect import detect
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class AudiobookGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Audiobook Generator")

        self.file_path = tk.StringVar()
        self.original_language = tk.StringVar()
        self.target_language = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        self.label_file = tk.Label(self.master, text="Select PDF file:")
        self.label_file.grid(row=0, column=0)

        self.entry_file = tk.Entry(self.master, textvariable=self.file_path, state='disabled')
        self.entry_file.grid(row=0, column=1)

        self.btn_browse = tk.Button(self.master, text="Browse", command=self.browse_pdf)
        self.btn_browse.grid(row=0, column=2)


        self.label_language = tk.Label(self.master, text="Detected Language:")
        self.label_language.grid(row=1, column=0)

        self.entry_language = tk.Entry(self.master, textvariable=self.original_language, state='disabled')
        self.entry_language.grid(row=1, column=1)


        self.translate_var = tk.BooleanVar()
        self.check_translate = tk.Checkbutton(self.master, text="Translate", variable=self.translate_var, command=self.toggle_translation)
        self.check_translate.grid(row=2, column=0)

        self.label_target_language = tk.Label(self.master, text="Target Language:")
        self.label_target_language.grid(row=2, column=1)

        self.entry_target_language = tk.Entry(self.master, textvariable=self.target_language, state='disabled')
        self.entry_target_language.grid(row=2, column=2)


        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(self.master, text="")
        self.status_label.grid(row=5, column=0, columnspan=3)


        self.btn_execute = tk.Button(self.master, text="Generate Audiobook", command=self.generate_audiobook)
        self.btn_execute.grid(row=6, column=0, columnspan=3)

    def browse_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_path.set(file_path)
            pdf_text = self.pdf_to_text(file_path)
            self.original_language.set(detect(pdf_text))

    def pdf_to_text(self, file_path):
        text = ""
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
        except Exception as e:
            print(f"Error: {e}")
        return text

    def toggle_translation(self):
        state = 'normal' if self.translate_var.get() else 'disabled'
        self.entry_target_language.config(state=state)

    def generate_audiobook(self):
        pdf_path = self.file_path.get()
        target_language = self.target_language.get()

        if not pdf_path:
            self.update_status("Error: Please select a PDF file.")
            return

        pdf_text = self.pdf_to_text(pdf_path)

        if self.translate_var.get():
            if not target_language:
                self.update_status("Error: Please enter the target language.")
                return

            self.translate_and_speak(pdf_text, target_language)
        else:
            self.save_and_speak_original_text(pdf_text)

    def translate_and_speak(self, text, target_language):
        translator = Translator()
        total_pages = len(text.split('\x0c'))

        translated_text = ""
        for page_num, page_text in enumerate(text.split('\x0c'), start=1):
            translated_page = self.translate_text(page_text, target_language)
            translated_text += translated_page

            # Update progress bar
            progress_percentage = (page_num / total_pages) * 100
            self.update_progress(progress_percentage)

        self.save_and_speak_translated_text(translated_text, target_language)

    def translate_text(self, text, target_language='en'):
        translator = Translator()
        return translator.translate(text, dest=target_language).text

    def save_and_speak_translated_text(self, translated_text, target_language):
        translated_text_file = 'translated_text.txt'
        with open(translated_text_file, 'w', encoding='utf-8') as f:
            f.write(translated_text)

        text_to_speech(translated_text, language=target_language, output_file='translated_output.mp3')

    def save_and_speak_original_text(self, original_text):
        text_to_speech(original_text, language=self.original_language.get(), output_file='output.mp3')

    def update_progress(self, value):
        self.progress_var.set(value)
        self.master.update_idletasks()

    def update_status(self, message):
        self.status_label.config(text=message)

def text_to_speech(text, language='en', output_file='output.mp3'):
    if text.strip() != "":
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_file)
            os.system(f"open {output_file}")  # Open the file (macOS specific)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Error: No text to speak.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudiobookGeneratorApp(root)
    root.mainloop()