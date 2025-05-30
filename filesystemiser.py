import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

DEFAULT_FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xlsx"],
    "Music": [".mp3", ".wav", ".aac"],
    "Archives": [".zip", ".rar", ".tar", ".7z"]
}

# Global undo log
UNDO_LOG = {}


def organize_files(folder_path, file_types, status_label):
    """Organize files into folders based on their extensions."""
    global UNDO_LOG
    UNDO_LOG = {}  # Reset undo log
    organized_count = 0  # Count of organized files

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_name)[1].lower()
            folder_name = "Others"  # Default category for unknown files

            # Find the folder name based on the extension
            for category, extensions in file_types.items():
                if file_extension in extensions:
                    folder_name = category
                    break

            # Create the category folder if it doesn't exist
            category_folder = os.path.join(folder_path, folder_name)
            os.makedirs(category_folder, exist_ok=True)

            # Move the file and save its original location for undo
            shutil.move(file_path, os.path.join(category_folder, file_name))
            UNDO_LOG[file_name] = file_path
            organized_count += 1

    # Save the undo log
    with open("undo_log.json", "w") as log_file:
        json.dump(UNDO_LOG, log_file)

    # Update status
    status_label.config(text=f"Organized {organized_count} files!")


def undo_organization(status_label):
    """Undo the last organization operation."""
    if not os.path.exists("undo_log.json"):
        messagebox.showerror("Error", "No undo data available.")
        return

    with open("undo_log.json", "r") as log_file:
        undo_data = json.load(log_file)

    for file_name, original_path in undo_data.items():
        current_path = os.path.join(os.path.dirname(original_path), file_name)
        if os.path.exists(current_path):
            shutil.move(current_path, original_path)

    messagebox.showinfo("Success", "Files have been restored to their original locations.")
    os.remove("undo_log.json")  # Clear the undo log
    status_label.config(text="Undo completed! Files restored.")


def start_organizer(status_label):
    """Launch the folder selection and file organization process."""
    folder_path = filedialog.askdirectory(title="Select Folder to Organize")
    if not folder_path:
        return

    # Add custom categories
    custom_categories = {}
    for entry in custom_entries:
        category = entry[0].get()
        extensions = entry[1].get().split(",")
        if category and extensions:
            custom_categories[category] = [ext.strip().lower() for ext in extensions]

    # Combine default and custom file types
    file_types = DEFAULT_FILE_TYPES.copy()
    file_types.update(custom_categories)

    # Organize files and update status
    organize_files(folder_path, file_types, status_label)
    summary = "\n".join([f"{category}: {len(os.listdir(os.path.join(folder_path, category)))} files"
                         for category in file_types.keys() if os.path.exists(os.path.join(folder_path, category))])
    messagebox.showinfo("Summary", f"Files organized successfully!\n\n{summary}")


# GUI Setup
root = tk.Tk()
root.title("File Organizer")
root.geometry("600x500")
root.resizable(False, False)

# Title Label
title_label = tk.Label(root, text="📂 File Organizer", font=("Arial", 18, "bold"), fg="blue")
title_label.pack(pady=10)

# Instructions
instructions = tk.Label(root, text="Add custom categories and extensions (comma-separated):", font=("Arial", 12))
instructions.pack(pady=5)

# Frame for custom entries
frame = tk.Frame(root)
frame.pack(pady=10)

# Scrollable area for custom entries
canvas = tk.Canvas(frame, width=550, height=150)
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Adding custom entry fields
custom_entries = []
for _ in range(5):  # Allow up to 5 custom categories
    category_label = tk.Label(scrollable_frame, text="Category:", font=("Arial", 10))
    category_label.grid(row=_, column=0, padx=5, pady=5)
    category_entry = tk.Entry(scrollable_frame, width=15)
    category_entry.grid(row=_, column=1, padx=5, pady=5)

    extensions_label = tk.Label(scrollable_frame, text="Extensions:", font=("Arial", 10))
    extensions_label.grid(row=_, column=2, padx=5, pady=5)
    extensions_entry = tk.Entry(scrollable_frame, width=25)
    extensions_entry.grid(row=_, column=3, padx=5, pady=5)

    custom_entries.append((category_entry, extensions_entry))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Buttons
organize_button = tk.Button(root, text="Organize Files", command=lambda: start_organizer(status_label), bg="green", fg="white", font=("Arial", 12), width=20)
organize_button.pack(pady=10)

undo_button = tk.Button(root, text="Undo", command=lambda: undo_organization(status_label), bg="red", fg="white", font=("Arial", 12), width=20)
undo_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
status_label.pack(pady=10)

# Start the GUI loop
root.mainloop()
