
root = TkinterDnD.Tk()
root.title("Plagiarism Detector")
root.geometry("800x600")
root.configure(bg="purple")

title_frame = tk.Frame(root, bg="yellow")
title_frame.pack(fill=tk.X)
header = tk.Label(title_frame, text="AuthetiCheck", font=("Arial", 18, "italic"), fg="black", bg="yellow", anchor="w")
header.pack(padx=10, pady=5, fill=tk.X)

frame = tk.Frame(root, bg="purple")
frame.pack(pady=5)
char_counter = tk.Label(frame, text="Characters: 0", font=("Arial", 10), fg="black", bg="purple")
char_counter.pack(side=tk.LEFT)
open_pdf_button = tk.Button(frame, text="Upload", command=open_pdf, bg="brown", fg="white")
open_pdf_button.pack(side=tk.RIGHT, padx=5)

drop_label = tk.Label(root, text="Drag & Drop", bg="purple", fg="white", width=94, height=1)
drop_label.pack(pady=10)

def handle_drop(event):
    file_path = event.data.strip('{}')  # Handle paths with spaces
    if file_path.lower().endswith('.pdf'):
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

        full_text = " ".join(extracted_text).strip()
        if full_text:
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, full_text)
            update_character_count()
        else:
            result_display.insert(tk.END, "Error: Could not extract text from PDF!\n", "error")
    else:
        messagebox.showerror("Invalid File", "Only PDF files are supported.")

drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', handle_drop)


text_input = scrolledtext.ScrolledText(root, height=10, width=80, wrap=tk.WORD, bg="white")
text_input.pack(pady=5)
text_input.bind("<KeyRelease>", update_character_count)

check_button = tk.Button(root, text="Check for Plagiarism", command=plagiarism_detector, bg="#FFFACD", font=("Arial", 12))
check_button.pack(pady=10)

result_display = scrolledtext.ScrolledText(root, height=10, width=80, wrap=tk.WORD)
result_display.pack(pady=5)

save_button = tk.Button(root, text="Download Report as PDF", bg="green", fg="white", font=("Arial", 12))
save_button.pack_forget()

visualize_button = tk.Button(root, text="Visualize", command=show_visualization, bg="cyan", fg="black", font=("Arial", 12), state=tk.DISABLED)
# Removed place and update_visualize_button_position
visualize_button.pack(side=tk.LEFT, padx=10, pady=10)
visualize_button.pack_forget()
