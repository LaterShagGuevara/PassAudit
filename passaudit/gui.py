import tkinter as tk
from tkinter import filedialog, messagebox

from passaudit.audit import analyze_password
from passaudit.utils import load_passwords_from_file, load_wordlist, load_passwords_from_csv

def start_gui(wordlist_path: str = "data/dictionary.txt") -> None:
    wordlist = load_wordlist(wordlist_path)

    root = tk.Tk()
    root.title("PassAudit")
    root.geometry("800x600")

    bg_color = "#2e2e2e"
    fg_color = "#ffffff"
    root.configure(bg=bg_color)

    result_var = tk.StringVar()
    rating_var = tk.StringVar()
    advice_var = tk.StringVar()

    def audit_single() -> None:
        pw = entry.get()
        if not pw:
            messagebox.showinfo("PassAudit", "Please enter a password")
            return
        analysis = analyze_password(pw, wordlist)

        fails = [k for k, passed in analysis["results"].items() if not passed]
        if fails:
            formatted = ", ".join(f.capitalize().replace("_", " ") for f in fails)
            result_var.set(f"Failed checks: {formatted}")
        else:
            result_var.set("Passed all checks!")

        rating_var.set(f"{analysis['rating']} ({analysis['score']}/7) | Entropy: {analysis['entropy']}")
        advice_var.set("  • " + "\n  • ".join(analysis["feedback"]))

    def clear_results() -> None:
        entry.delete(0, tk.END)
        result_var.set("")
        rating_var.set("")
        advice_var.set("")
        result_text.delete(1.0, tk.END)

    def audit_file() -> None:
        path = filedialog.askopenfilename()
        if not path:
            return
        if path.lower().endswith(".csv"):
            passwords = load_passwords_from_csv(path)
        else:
            passwords = load_passwords_from_file(path)

        lines = []
        for pw in passwords:
            a = analyze_password(pw, wordlist)
            fails = [k for k, passed in a["results"].items() if not passed]
            failed = ", ".join(f.capitalize().replace("_", " ") for f in fails) if fails else "OK"
            line = f"{pw}: {failed} | {a['rating']} | Entropy: {a['entropy']} | Tips: {', '.join(a['feedback'])}"
            lines.append(line)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(lines))

    def close_app() -> None:
        root.destroy()

    entry = tk.Entry(root, width=60)
    entry.pack(pady=10)

    button_frame = tk.Frame(root, bg=bg_color)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Check Password", command=audit_single, width=18).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Open File", command=audit_file, width=18).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Clear", command=clear_results, width=18).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Close", command=close_app, width=18).pack(side=tk.LEFT, padx=10)

    tk.Label(root, textvariable=result_var, fg=fg_color, bg=bg_color, font=("Arial", 12)).pack(pady=5)
    tk.Label(root, textvariable=rating_var, fg="#00ff00", bg=bg_color, font=("Arial", 12, "bold")).pack()
    tk.Label(root, text="Feedback:", fg=fg_color, bg=bg_color, font=("Arial", 10, "bold")).pack()
    tk.Label(root, textvariable=advice_var, fg="#ffcc00", bg=bg_color, font=("Arial", 10), justify="left", wraplength=700).pack(pady=5)

    result_text = tk.Text(root, width=100, height=15, bg=bg_color, fg=fg_color)
    result_text.pack(pady=10)

    root.mainloop()

