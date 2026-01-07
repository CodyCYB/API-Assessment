import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

# ================= API =================

BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def get_pokemon(query):
    try:
        r = requests.get(BASE_URL + str(query).lower())
        r.raise_for_status()
        return r.json()
    except:
        return None

# ================= UTILITIES =================

def stat_color(value):
    if value < 60:
        return "#FBC02D"  # yellow
    elif value < 100:
        return "#F57C00"  # orange
    else:
        return "#D32F2F"  # red

# ================= MODEL =================

class Pokemon:
    def __init__(self, name, stats, sprite, abilities, moves):
        self.name = name
        self.stats = stats
        self.sprite = sprite
        self.abilities = abilities
        self.moves = moves

    @classmethod
    def from_api(cls, data):
        return cls(
            data["name"].capitalize(),
            {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            data["sprites"]["front_default"],
            [a["ability"]["name"] for a in data["abilities"]],
            [m["move"]["name"] for m in data["moves"][:12]]
        )

# ================= SCROLLABLE FRAME =================

class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, bg="#FFFDE7", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.frame = tk.Frame(canvas, bg="#FFFDE7")

        self.frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# ================= GUI =================

BG_RED = "#D32F2F"
BG_YELLOW = "#FFEB3B"
BOX_BG = "#FFFDE7"
BLACK = "#000000"

class PokedexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex")
        self.root.geometry("520x760")
        self.root.config(bg=BG_RED)
        self.build()

    def build(self):
        tk.Label(
            self.root,
            text="POKÉDEX",
            font=("Arial", 26, "bold"),
            bg=BG_RED,
            fg=BG_YELLOW
        ).pack(pady=10)

        search = tk.Frame(self.root, bg=BG_RED)
        search.pack()

        self.entry = tk.Entry(search, font=("Arial", 14), width=20)
        self.entry.pack(side="left", padx=10)
        self.entry.bind("<Return>", lambda e: self.search())

        tk.Button(
            search,
            text="Search",
            bg=BG_YELLOW,
            fg="black",
            font=("Arial", 12, "bold"),
            relief="solid",
            borderwidth=2,
            command=self.search
        ).pack(side="left")

        self.status = tk.Label(self.root, bg=BG_RED, fg="white")
        self.status.pack()

        # Sprite
        self.sprite_box = tk.Frame(self.root, bg=BOX_BG, relief="solid", borderwidth=3)
        self.sprite_box.pack(pady=10)

        self.sprite_label = tk.Label(self.sprite_box, bg=BOX_BG)
        self.sprite_label.pack(padx=20, pady=20)

        self.name_label = tk.Label(
            self.root, font=("Arial", 20, "bold"),
            bg=BG_RED, fg=BG_YELLOW
        )
        self.name_label.pack()

        # Scrollable info box
        container = tk.Frame(self.root, bg=BG_RED)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.info = ScrollableFrame(container)
        self.info.pack(fill="both", expand=True)

    def search(self):
        data = get_pokemon(self.entry.get())
        if not data:
            self.status.config(text="Pokémon not found")
            return

        self.status.config(text="")
        self.pokemon = Pokemon.from_api(data)
        self.display()

    def display(self):
    # Sprite
     if self.pokemon.sprite:
        img = Image.open(BytesIO(requests.get(self.pokemon.sprite).content))
        img = img.resize((180, 180))
        self.sprite_img = ImageTk.PhotoImage(img)
        self.sprite_label.config(image=self.sprite_img)

    self.name_label.config(text=self.pokemon.name)

    frame = self.info.frame
    for w in frame.winfo_children():
        w.destroy()

    # ===== Stats =====
    tk.Label(
        frame,
        text="Stats",
        font=("Arial", 14, "bold"),
        bg=BOX_BG
    ).pack(pady=10)

    stats_container = tk.Frame(frame, bg=BOX_BG)
    stats_container.pack(anchor="center")

    for stat, value in self.pokemon.stats.items():
        row = tk.Frame(stats_container, bg=BOX_BG)
        row.pack(pady=4)

        tk.Label(
            row,
            text=stat.upper(),
            width=12,           # FIX: reserved space
            anchor="e",
            bg=BOX_BG
        ).pack(side="left", padx=5)

        bar = tk.Canvas(
            row,
            width=220,
            height=18,
            bg="white",
            highlightthickness=1
        )
        bar.pack(side="left", padx=8)

        fill_width = min(int((value / 255) * 220), 220)
        bar.create_rectangle(
            0, 0, fill_width, 18,
            fill=stat_color(value),
            outline=""
        )

        tk.Label(
            row,
            text=value,
            width=4,
            bg=BOX_BG
        ).pack(side="left", padx=5)

    # ===== Abilities =====
    tk.Label(
        frame,
        text="Abilities",
        font=("Arial", 14, "bold"),
        bg=BOX_BG
    ).pack(pady=10)

    abilities_container = tk.Frame(frame, bg=BOX_BG)
    abilities_container.pack(anchor="center")

    for ability in self.pokemon.abilities:
        tk.Label(
            abilities_container,
            text=ability,
            bg=BOX_BG
        ).pack()

    # ===== Moves =====
    tk.Label(
        frame,
        text="Moves",
        font=("Arial", 14, "bold"),
        bg=BOX_BG
    ).pack(pady=10)

    moves_container = tk.Frame(frame, bg=BOX_BG)
    moves_container.pack(anchor="center")

    for move in self.pokemon.moves:
        tk.Label(
            moves_container,
            text=move,
            bg=BOX_BG
        ).pack()


# ================= RUN =================

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexGUI(root)
    root.mainloop()
