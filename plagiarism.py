import nltk
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import PyPDF2
from fpdf import FPDF
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from PIL import Image
import imagehash


report_data = []
plagiarism_risk = 0
# Download required NLTK resources
nltk.download('punkt')

IMAGE_DATABASE_FOLDER = "known_images"



def get_google_results(query, num_results=3):
    return [result for result in search(query, num_results=num_results)]

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except Exception:
        return ""

def similarity_score(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio() * 100

def update_character_count(event=None):
    char_count = len(text_input.get("1.0", tk.END).strip())
    char_counter.config(text=f"Characters: {char_count}")

def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
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


def sanitize_text(text):
    return text.encode("latin-1", "ignore").decode("latin-1")



def generate_pdf_report(report_data, char_count, plagiarism_risk):
    # COMBINED FIGURE (Pie + Bar)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Pie Chart
    labels = ['Plagiarism', 'Original']
    sizes = [plagiarism_risk, 100 - plagiarism_risk]
    colors = ['red', 'green']
    axs[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    axs[0].set_title("Plagiarism Risk Distribution")

    # Bar Chart
    urls = [entry['URL'] for entry in report_data]
    scores = [entry['Similarity Score'] for entry in report_data]
    bar_labels = [f"Source {i+1}" for i in range(len(urls))]

    bars = axs[1].bar(bar_labels, scores, color='blue')
    axs[1].set_ylabel('Similarity Score (%)')
    axs[1].set_xlabel('Sources')
    axs[1].set_title('Similarity Score by Source')
    axs[1].tick_params(axis='x', rotation=45)
    

    # Score labels
    for bar, score in zip(bars, scores):
        axs[1].text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 1,
                    f'{score:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    combined_path = "combined_chart.png"
    plt.savefig(combined_path)
    plt.close()

    # PDF Report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Plagiarism Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, sanitize_text(f"Plagiarism Risk: {plagiarism_risk:.2f}%"), ln=True)
    pdf.cell(200, 10, sanitize_text(f"Character Count: {char_count}"), ln=True)
    pdf.ln(10)

    # Add the combined chart image (full size)
    pdf.image(combined_path, x=10, w=190)
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    for idx, entry in enumerate(report_data, 1):
        pdf.multi_cell(0, 10, sanitize_text(f"{idx}. {entry['URL']}"), align="L")
        pdf.cell(200, 10, sanitize_text(f"Similarity Score: {entry['Similarity Score']:.2f}%"), ln=True)
        pdf.multi_cell(0, 10, sanitize_text(f"Extracted Text: {entry['Extracted Text']}..."), align="L")
        pdf.ln(5)

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        pdf.output(file_path)
        result_display.insert(tk.END, f"\nReport saved: {file_path}\n", "save")

def show_visualization():
    if not report_data:
        result_display.insert(tk.END, "\nNo data to visualize! Run the plagiarism check first.\n", "error")
        return

    visualize_window = tk.Toplevel(root)
    visualize_window.title("Plagiarism Visualization")

    fig = Figure(figsize=(12, 5), dpi=100)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    try:
        labels = ['Plagiarism', 'Original']
        sizes = [plagiarism_risk, 100 - plagiarism_risk]
        colors = ['red', 'green']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Plagiarism Risk Distribution")

        urls = [entry['URL'] for entry in report_data]
        scores = [entry['Similarity Score'] for entry in report_data]
        bar_labels = [f"Source {i+1}" for i in range(len(urls))]

        bars = ax2.bar(bar_labels, scores, color='blue')
        ax2.set_ylabel('Similarity Score (%)')
        ax2.set_xlabel('Sources')
        ax2.set_title('Similarity Score by Source')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_xticklabels(bar_labels, rotation=45, ha='right')

        fig.tight_layout()

        for bar, score in zip(bars, scores):
            ax2.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 1,
                        f'{score:.1f}%', ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, master=visualize_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    except Exception as e:
        messagebox.showerror("Visualization Error", f"An error occurred during visualization: {e}")


def plagiarism_detector():
    input_text = text_input.get("1.0", tk.END).strip()
    char_count = len(input_text)
    if not input_text:
        result_display.insert(tk.END, "Error: No text entered!\n", "error")
        return

    result_display.delete("1.0", tk.END)
    search_results = get_google_results(input_text[:100])
    global report_data, plagiarism_risk
    report_data = []

    for url in search_results:
        webpage_text = extract_text_from_url(url)
        if webpage_text:
            score = similarity_score(input_text, webpage_text)
            report_data.append({
                "URL": url,
                "Similarity Score": score,
                "Extracted Text": webpage_text[:300]
            })

    report_data = sorted(report_data, key=lambda x: x["Similarity Score"], reverse=True)
    plagiarism_risk = max([entry["Similarity Score"] for entry in report_data], default=0)

    result_display.insert(tk.END, f"Plagiarism Risk: {plagiarism_risk:.2f}%\n", "risk")
    for entry in report_data:
        result_display.insert(tk.END, f"Source: {entry['URL']}\n", "url")
        result_display.insert(tk.END, f"Similarity Score: {entry['Similarity Score']:.2f}%\n", "score")
        result_display.insert(tk.END, f"\nExtracted Text: {entry['Extracted Text']}...\n\n", "text")

    result_display.insert(tk.END, "\nSources Checked:\n", "sources")
    for i, url in enumerate(search_results, 1):
        result_display.insert(tk.END, f"{i}. {url}\n", "url")

    save_button.pack(pady=10)
    save_button.config(state=tk.NORMAL, command=lambda: generate_pdf_report(report_data, char_count, plagiarism_risk))
    visualize_button.pack(side=tk.LEFT, padx=10, pady=10) # Pack the button so it's visible
    visualize_button.config(state=tk.NORMAL)
