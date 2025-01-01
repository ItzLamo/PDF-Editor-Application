import customtkinter as ctk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from typing import Dict, Any, Callable, List, Tuple
import os

# Theme Management
class Theme:
    COLORS = {
        "primary": "#1f538d",
        "secondary": "#2d7dd2",
        "accent": "#45b7d1",
        "background": "#2b2b2b",
        "surface": "#333333",
        "text": "#ffffff",
        "text_secondary": "#cccccc",
        "success": "#28a745",
        "error": "#dc3545"
    }

    BUTTON_STYLES = {
        "primary": {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["secondary"],
            "text_color": COLORS["text"],
            "corner_radius": 8
        },
        "secondary": {
            "fg_color": "transparent",
            "hover_color": COLORS["surface"],
            "text_color": COLORS["text"],
            "corner_radius": 8,
            "border_width": 2,
            "border_color": COLORS["secondary"]
        }
    }

    @classmethod
    def setup_theme(cls) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    @classmethod
    def get_button_style(cls, style_type: str = "primary") -> Dict[str, Any]:
        return cls.BUTTON_STYLES.get(style_type, cls.BUTTON_STYLES["primary"])

# PDF Operations
def merge_pdfs(input_paths: List[str], output_path: str) -> bool:
    try:
        merger = PdfWriter()
        for path in input_paths:
            merger.append(path)
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)
        return True
    except Exception as e:
        print(f"Error merging PDFs: {str(e)}")
        return False

def split_pdf(input_path: str, ranges: List[Tuple[int, int]], output_prefix: str) -> bool:
    try:
        reader = PdfReader(input_path)
        for i, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for page_num in range(start - 1, min(end, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
            output_path = f"{output_prefix}_{i + 1}.pdf"
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        return True
    except Exception as e:
        print(f"Error splitting PDF: {str(e)}")
        return False

# UI Components
class FileList(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.files: List[str] = []
        self.labels = []

    def add_file(self, file_path: str) -> None:
        if file_path not in self.files:
            self.files.append(file_path)
            label = ctk.CTkLabel(
                self,
                text=os.path.basename(file_path),
                fg_color=Theme.COLORS["surface"],
                corner_radius=4,
                padx=10,
                pady=5
            )
            label.pack(fill="x", padx=5, pady=2)
            self.labels.append(label)

    def clear_files(self) -> None:
        self.files.clear()
        for label in self.labels:
            label.destroy()
        self.labels.clear()

class ActionButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str,
        command: Callable,
        style: str = "primary",
        **kwargs
    ):
        button_style = Theme.get_button_style(style)
        super().__init__(
            master,
            text=text,
            command=command,
            **button_style,
            **kwargs
        )

# Main Application
class PDFToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Editor")
        self.geometry("800x600")
        Theme.setup_theme()
        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            self.main_container,
            text="PDF Editor",
            font=("Helvetica", 24, "bold"),
            text_color=Theme.COLORS["text"]
        )
        title.pack(pady=10)

        # Tabs
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Merge tab
        merge_tab = self.tabview.add("Merge PDFs")
        self.setup_merge_tab(merge_tab)

        # Split tab
        split_tab = self.tabview.add("Split PDF")
        self.setup_split_tab(split_tab)

    def setup_merge_tab(self, tab):
        # File list
        self.merge_file_list = FileList(tab, width=700, height=300)
        self.merge_file_list.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", pady=10)

        ActionButton(
            button_frame,
            text="Add Files",
            command=self.add_files_to_merge,
            style="primary"
        ).pack(side="left", padx=5)

        ActionButton(
            button_frame,
            text="Clear Files",
            command=self.clear_merge_files,
            style="secondary"
        ).pack(side="left", padx=5)

        ActionButton(
            button_frame,
            text="Merge PDFs",
            command=self.merge_files,
            style="primary"
        ).pack(side="right", padx=5)

    def setup_split_tab(self, tab):
        # File selection
        self.split_file_label = ctk.CTkLabel(
            tab,
            text="No file selected",
            text_color=Theme.COLORS["text_secondary"]
        )
        self.split_file_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", pady=10)

        ActionButton(
            button_frame,
            text="Select PDF",
            command=self.select_pdf_to_split,
            style="primary"
        ).pack(side="left", padx=5)

        ActionButton(
            button_frame,
            text="Split PDF",
            command=self.split_file,
            style="primary"
        ).pack(side="right", padx=5)

        # Split options
        self.page_range_var = ctk.StringVar(value="1-end")
        range_frame = ctk.CTkFrame(tab)
        range_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            range_frame,
            text="Page Range (e.g., 1-5,7-10):",
            text_color=Theme.COLORS["text"]
        ).pack(side="left", padx=5)

        ctk.CTkEntry(
            range_frame,
            textvariable=self.page_range_var,
            width=200
        ).pack(side="left", padx=5)

    def add_files_to_merge(self):
        files = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")]
        )
        for file in files:
            self.merge_file_list.add_file(file)

    def clear_merge_files(self):
        self.merge_file_list.clear_files()

    def merge_files(self):
        if len(self.merge_file_list.files) < 2:
            messagebox.showerror(
                "Error",
                "Please select at least two PDF files to merge."
            )
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if output_path:
            if merge_pdfs(self.merge_file_list.files, output_path):
                messagebox.showinfo(
                    "Success",
                    "PDFs merged successfully!"
                )
                self.clear_merge_files()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to merge PDFs. Please try again."
                )

    def select_pdf_to_split(self):
        file = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.split_file_path = file
            self.split_file_label.configure(
                text=f"Selected: {os.path.basename(file)}"
            )

    def split_file(self):
        if not hasattr(self, 'split_file_path'):
            messagebox.showerror(
                "Error",
                "Please select a PDF file to split."
            )
            return

        try:
            ranges = []
            for range_str in self.page_range_var.get().split(','):
                start, end = range_str.split('-')
                start = int(start)
                end = float('inf') if end.lower() == 'end' else int(end)
                ranges.append((start, end))

            output_dir = filedialog.askdirectory()
            if output_dir:
                output_prefix = os.path.join(
                    output_dir,
                    os.path.splitext(
                        os.path.basename(self.split_file_path)
                    )[0]
                )
                if split_pdf(self.split_file_path, ranges, output_prefix):
                    messagebox.showinfo(
                        "Success",
                        "PDF split successfully!"
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to split PDF. Please try again."
                    )
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid page range format. Please use format like '1-5,7-10'."
            )

if __name__ == "__main__":
    app = PDFToolsApp()
    app.mainloop()