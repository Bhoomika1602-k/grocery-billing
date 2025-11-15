# main.py
import sys
from pathlib import Path
from math import sin
import tkinter as tk
from tkinter import ttk, messagebox

# ensure local folder on sys.path so imports resolve
THIS_DIR = Path(__file__).parent.resolve()
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

try:
    from db import init_db, save_purchase
except Exception as e:
    raise ImportError("Could not import 'db'. Ensure db.py is in the same folder as main.py") from e

# Initialize DB
init_db()

# ---------- Constants / Theme ----------
SAFFRON = "#FF9933"
BG = "#FFF6ED"        # pale background
CARD = "#F2E6D0"      # card background
TEXT = "#3b2f2f"

# ---------- Root window ----------
root = tk.Tk()
root.title("🛒 Grocery Billing System")
root.geometry("900x650")
root.config(bg=BG)
root.resizable(False, False)

# ---------- Animated header canvas ----------
header_h = 120
header_canvas = tk.Canvas(root, height=header_h, bd=0, highlightthickness=0, relief='ridge')
header_canvas.pack(fill="x", side="top")
# saffron strip background
header_canvas.create_rectangle(0, 0, 900, header_h, fill=SAFFRON, outline=SAFFRON)

# Title text (on top of saffron)
title_id = header_canvas.create_text(450, 28, text="Modern Grocery Billing System",
                                     font=("Segoe UI", 20, "bold"), fill="white")
subtitle_id = header_canvas.create_text(450, 58, text="Select items, edit quantities, add custom items, then generate bill.",
                                        font=("Segoe UI", 10), fill="#FFF3E6")

# Animated food emojis (floating up/down)
emoji_texts = ["🍎", "🍞", "🧂", "🧀", "🍪", "🥛", "🌽"]
emoji_items = []
# create multiple emojis spaced horizontally
for i, e in enumerate(emoji_texts):
    x = 40 + i * 120
    y = 95
    item = header_canvas.create_text(x, y, text=e, font=("Segoe UI Emoji", 26))
    emoji_items.append((item, x, y, i * 0.6))  # (id, base_x, base_y, phase)

# animation state
anim_step = 0

def animate_emojis():
    global anim_step
    anim_step += 0.08
    for item, base_x, base_y, phase in emoji_items:
        # gentle vertical float using sine
        dy = 8 * sin(anim_step + phase)
        header_canvas.coords(item, base_x, base_y + dy)
    # repeat
    header_canvas.after(50, animate_emojis)

animate_emojis()

# ---------- Main container ----------
container = ttk.Frame(root)
container.pack(fill="both", expand=True, padx=16, pady=(12,16))
container.configure(style="Card.TFrame")

style = ttk.Style()
style.theme_use("clam")
style.configure("Card.TFrame", background=BG)
style.configure("Card.TLabelframe", background=BG, foreground=TEXT)
style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
style.configure("TLabel", background=BG, foreground=TEXT)
style.configure("TButton", font=("Segoe UI", 11, "bold"))
style.configure("Small.TLabel", font=("Segoe UI", 10), background=BG)
style.configure("Footer.TLabel", font=("Segoe UI", 9), background=BG, foreground="#6b5a4a")

# Left panel (items) and right panel (controls)
left = ttk.Labelframe(container, text="Items", padding=(12,10))
left.grid(row=0, column=0, sticky="nsew", padx=(0,12))
right = ttk.Labelframe(container, text="Controls", padding=(12,10))
right.grid(row=0, column=1, sticky="nsew")

container.columnconfigure(0, weight=1)
container.columnconfigure(1, weight=0)
left.config(width=520, height=420)
right.config(width=320, height=420)

# ---------- Items data ----------
items = {
    "Milk": 45.0,
    "Bread": 25.0,
    "Eggs (Dozen)": 60.0,
    "Rice (1kg)": 70.0,
    "Sugar (1kg)": 50.0,
    "Tea (250g)": 120.0,
    "Oil (1L)": 150.0,
    "Chilli Powder (100g)": 20.0
}

item_vars = {}
quantity_vars = {}
row_frames = []

# Scrollable area for items
items_canvas = tk.Canvas(left, bg=CARD, width=520, height=420, highlightthickness=0)
scrollbar = ttk.Scrollbar(left, orient="vertical", command=items_canvas.yview)
scrollable_frame = ttk.Frame(items_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: items_canvas.configure(scrollregion=items_canvas.bbox("all"))
)
items_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
items_canvas.configure(yscrollcommand=scrollbar.set)
items_canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns", padx=(4,0))

# Function to add a single item row. Uses grid so entries don't get hidden.
def add_item_row(name: str, price: float):
    r = len(row_frames)
    frame = ttk.Frame(scrollable_frame)
    frame.grid(row=r, column=0, sticky="ew", padx=6, pady=6)
    frame.columnconfigure(1, weight=1)

    var = tk.BooleanVar(value=False)
    qty_var = tk.IntVar(value=1)
    item_vars[name] = var
    quantity_vars[name] = qty_var
    row_frames.append(frame)

    # Checkbox
    chk = ttk.Checkbutton(frame, text=name + f" (₹{price:.2f})", variable=var)
    chk.grid(row=0, column=0, sticky="w", padx=(2,8))

    # Spacer to keep layout stable
    # Qty label and entry aligned right side of the row
    qty_frame = ttk.Frame(frame)
    qty_frame.grid(row=0, column=1, sticky="e")
    qty_lbl = ttk.Label(qty_frame, text="Qty:")
    qty_lbl.pack(side="left", padx=(0,6))
    qty_entry = ttk.Entry(qty_frame, textvariable=qty_var, width=5, justify="center")
    qty_entry.pack(side="left")

# populate default items
for n, p in items.items():
    add_item_row(n, p)

# ---------- Add custom item area (in right panel) ----------
add_frame = ttk.Frame(right)
add_frame.pack(fill="x", pady=(0,12))

ttk.Label(add_frame, text="Add Custom Item:", style="Small.TLabel").grid(row=0, column=0, sticky="w", pady=4)
entry_new_item = ttk.Entry(add_frame, width=20)
entry_new_item.grid(row=0, column=1, padx=6, pady=4)
entry_new_price = ttk.Entry(add_frame, width=10)
entry_new_price.grid(row=0, column=2, padx=6, pady=4)
add_btn = ttk.Button(add_frame, text="Add", width=12)
add_btn.grid(row=0, column=3, padx=6, pady=4)

def add_custom_item():
    name = entry_new_item.get().strip()
    price_text = entry_new_price.get().strip()
    if not name:
        messagebox.showwarning("Input required", "Enter item name.")
        return
    try:
        price = float(price_text)
    except ValueError:
        messagebox.showwarning("Invalid price", "Enter a valid numeric price.")
        return
    if name in items:
        messagebox.showinfo("Exists", f"'{name}' already exists.")
        return
    items[name] = price
    add_item_row(name, price)
    entry_new_item.delete(0, tk.END)
    entry_new_price.delete(0, tk.END)

add_btn.config(command=add_custom_item)

# ---------- Bill generation ----------
def generate_bill():
    total = 0.0
    lines = []
    for name, selected in item_vars.items():
        if selected.get():
            try:
                qty = int(quantity_vars[name].get())
            except Exception:
                qty = 1
            qty = max(1, qty)
            price = items.get(name, 0.0)
            cost = price * qty
            total += cost
            lines.append(f"{name} x {qty} = ₹{cost:.2f}")
            # save purchase
            save_purchase(name, price, qty, cost)

    if total <= 0:
        messagebox.showinfo("No items", "Please select at least one item.")
        return

    bill_text = "\n".join(lines) + f"\n\n---------------------------\nTotal: ₹{total:.2f}"
    messagebox.showinfo("🧾 Bill Summary", bill_text)

# ---------- Right panel buttons ----------
buttons_frame = ttk.Frame(right)
buttons_frame.pack(fill="x", pady=(6,8))

gen_btn = ttk.Button(buttons_frame, text="Generate Bill", command=generate_bill)
gen_btn.pack(fill="x", pady=8)
clear_btn = ttk.Button(buttons_frame, text="Clear Selections", command=lambda: [v.set(False) for v in item_vars.values()])
clear_btn.pack(fill="x", pady=8)
exit_btn = ttk.Button(buttons_frame, text="Exit", command=root.destroy)
exit_btn.pack(fill="x", pady=8)

# small footer
footer = ttk.Label(root, text="© 2025 Grocery Billing System — Stored in billing.db", style="Footer.TLabel")
footer.pack(side="bottom", pady=8)

# ---------- Minor polish: hover effect on buttons ----------
def _on_enter(e):
    e.widget.config(cursor="hand2")
def _on_leave(e):
    e.widget.config(cursor="")

for b in (gen_btn, clear_btn, exit_btn, add_btn):
    b.bind("<Enter>", _on_enter)
    b.bind("<Leave>", _on_leave)

# Start the app
root.mainloop()
