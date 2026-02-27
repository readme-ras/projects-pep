import tkinter as tk
from tkinter import messagebox


class CalculatorGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")

        # Stack for history
        self.history_stack = []

        # Display
        self.display = tk.Entry(
            root,
            font=("Arial", 20),
            borderwidth=5,
            relief="ridge",
            justify="right"
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Buttons layout
        buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+",
            "C", "H"
        ]

        row = 1
        col = 0

        for btn in buttons:

            tk.Button(
                root,
                text=btn,
                width=6,
                height=2,
                font=("Arial", 14),
                command=lambda b=btn: self.on_click(b)
            ).grid(row=row, column=col, padx=5, pady=5)

            col += 1

            if col == 4:
                col = 0
                row += 1

    # Button Click Logic
    def on_click(self, char):

        if char == "C":
            self.display.delete(0, tk.END)

        elif char == "=":
            expr = self.display.get()

            try:
                result = eval(expr)

                record = f"{expr} = {result}"
                self.history_stack.append(record)

                self.display.delete(0, tk.END)
                self.display.insert(tk.END, str(result))

            except:
                messagebox.showerror("Error", "Invalid Expression")

        elif char == "H":
            self.show_history()

        else:
            self.display.insert(tk.END, char)

    # Show History Popup
    def show_history(self):

        if not self.history_stack:
            messagebox.showinfo("History", "No history yet")
            return

        history_text = "\n".join(reversed(self.history_stack))

        messagebox.showinfo("History", history_text)


# Run App
root = tk.Tk()
app = CalculatorGUI(root)
root.mainloop()