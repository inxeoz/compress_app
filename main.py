import os
import threading
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, ttk
from PIL import Image

def compress_images(source_folder, output_folder, quality, progress_callback):
    image_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            ext = file.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'tiff', 'tif', 'gif']:
                image_files.append(os.path.join(root, file))

    total_files = len(image_files)
    count = 0
    errors = []
    for idx, src_path in enumerate(image_files):
        try:
            rel_path = os.path.relpath(src_path, source_folder)
            dst_path = os.path.join(output_folder, os.path.splitext(rel_path)[0] + ".jpg")
            dst_dir = os.path.dirname(dst_path)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            with Image.open(src_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(dst_path, "JPEG", quality=quality, optimize=True)
            count += 1
        except Exception as e:
            # Log error, but do not stop processing
            errors.append(f"Failed to compress {src_path}: {e}")

        if progress_callback:
            progress_callback(idx + 1, total_files)
    return count, errors

def select_source():
    folder = filedialog.askdirectory()
    if folder:
        source_var.set(folder)

def select_output():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)

def run_compress_threaded():
    # Disable the compress button to prevent multiple runs
    compress_btn.config(state='disabled')
    progress_bar['value'] = 0
    status_var.set("Starting compression...")
    progress_bar.update()
    root.update_idletasks()

    def progress_callback(done, total):
        progress_bar['maximum'] = total
        progress_bar['value'] = done
        status_var.set(f"Compressed {done}/{total} images...")
        root.update_idletasks()

    def compress_task():
        src = source_var.get()
        out = output_var.get()
        try:
            quality = int(quality_var.get())
        except Exception:
            quality = 70
        if not src or not out:
            messagebox.showerror("Error", "Please select both folders.")
            compress_btn.config(state='normal')
            return
        count, errors = compress_images(src, out, quality, progress_callback)
        progress_bar['value'] = progress_bar['maximum']
        status_var.set("Compression finished.")
        compress_btn.config(state='normal')
        if errors:
            # Show summary of errors in a popup
            err_msg = f"Compressed {count} images.\n{len(errors)} errors occurred.\n\nFirst 5 errors:\n" + "\n".join(errors[:5])
            messagebox.showwarning("Completed with errors", err_msg)
        else:
            messagebox.showinfo("Done", f"Compression complete! {count} images processed.")

    threading.Thread(target=compress_task, daemon=True).start()

root = Tk()
root.title("Image Compressor")

source_var = StringVar()
output_var = StringVar()
quality_var = StringVar(value="70")
status_var = StringVar()

Label(root, text="Source Folder:").pack()
Button(root, text="Choose Source Folder", command=select_source).pack()
Label(root, textvariable=source_var, fg="blue", wraplength=400).pack()

Label(root, text="Output Folder:").pack()
Button(root, text="Choose Output Folder", command=select_output).pack()
Label(root, textvariable=output_var, fg="blue", wraplength=400).pack()

Label(root, text="JPEG Quality (1-100, default 70):").pack()
quality_entry = ttk.Entry(root, textvariable=quality_var, width=5)
quality_entry.pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

Label(root, textvariable=status_var, fg="green").pack()

compress_btn = Button(root, text="Compress Images!", command=run_compress_threaded, bg="green", fg="white")
compress_btn.pack(pady=10)

root.mainloop()