import os
import shutil
import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tqdm import tqdm
import threading

# Directorio de salida predeterminado
DEFAULT_OUTPUT_DIR = "card_assets"

# Distribución de rarezas (ajustable)
RARITY_DISTRIBUTION = {
    "Common": 0.35,
    "Uncommon": 0.25,
    "Rare": 0.15,
    "Rare Holo": 0.1,
    "Promo": 0.05,
    "Rare Holo EX": 0.03,
    "Ultra Rare": 0.025,
    "Rare Secret": 0.02,
    "Rare Holo GX": 0.015,
    "Rare Shiny": 0.01,
    "Rare Holo V": 0.005,
    "Rare BREAK": 0.005,
    "Rare Ultra": 0.005,
    "Rare Prism Star": 0.005,
    "Amazing Rare": 0.005,
    "Rare Shining": 0.005
}

API_URL = "https://api.pokemontcg.io/v2/cards"
HEADERS = {}

# Lógica de descarga y guardado
def fetch_and_save_cards(total_cards, output_dir, clear_images, log_callback):
    image_dir = os.path.join(output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    if clear_images:
        shutil.rmtree(image_dir)
        os.makedirs(image_dir, exist_ok=True)
        log_callback("🧹 Se ha limpiado el contenido de la carpeta de imágenes")

    all_cards = []
    for rarity, ratio in RARITY_DISTRIBUTION.items():
        count = max(1, int(round(total_cards * ratio)))
        log_callback(f"📦 Obteniendo {rarity} (objetivo {count} cartas)")
        rarity_cards = []
        page = 1
        while len(rarity_cards) < count:
            params = {"q": f"rarity:\"{rarity}\"", "page": page, "pageSize": 250}
            try:
                response = requests.get(API_URL, headers=HEADERS, params=params)
                data = response.json().get("data", [])
            except Exception as e:
                log_callback(f"❌ Error en la solicitud: {e}")
                break

            if not data:
                break
            for card in data:
                if len(rarity_cards) >= count:
                    break
                if "images" not in card or "small" not in card["images"]:
                    continue
                rarity_cards.append(card)
            page += 1
        all_cards.extend(rarity_cards)
        log_callback(f"✅ Obtenidas {len(rarity_cards)} cartas de rareza {rarity}")

    # Descargar imágenes
    for card in tqdm(all_cards, desc="⬇️ Descargando imágenes"):
        image_url = card.get("images", {}).get("small")
        if not image_url:
            continue
        image_path = os.path.join(image_dir, f"{card['id']}.png")
        try:
            img_data = requests.get(image_url).content
            with open(image_path, "wb") as f:
                f.write(img_data)
            card["image"] = os.path.relpath(image_path, output_dir)
        except Exception as e:
            log_callback(f"[Error] Fallo al descargar {card['id']}: {e}")

    # Guardar JSON
    simplified = []
    for card in all_cards:
        simplified.append({
            "id": card["id"],
            "name": card.get("name", ""),
            "hp": int(card.get("hp", "0")) if card.get("hp", "0").isdigit() else 0,
            "types": card.get("types", []),
            "rarity": card.get("rarity", "Desconocido"),
            "attacks": [{
                "name": atk.get("name", ""),
                "damage": atk.get("damage", ""),
                "text": atk.get("text", "")
            } for atk in card.get("attacks", [])],
            "image": card.get("image", "")
        })
    json_path = os.path.join(output_dir, "cards.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(simplified, f, indent=2, ensure_ascii=False)

    log_callback(f"🎉 ¡Hecho! Se han guardado {len(simplified)} cartas en {json_path}")

# Interfaz gráfica
def launch_gui():
    def update_clear_checkbox_state(*_):
        img_dir = os.path.join(dir_var.get(), "images")
        if os.path.exists(img_dir) and os.listdir(img_dir):
            clear_check.config(state="normal")
        else:
            clear_check.config(state="disabled")
            clear_var.set(False)

    def choose_directory():
        selected = filedialog.askdirectory()
        if selected:
            dir_var.set(selected)
            update_clear_checkbox_state()

    def start_download():
        try:
            total = int(entry_var.get())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número válido de cartas (entero positivo)")
            return

        raw_dir = dir_var.get().strip()
        out_dir = raw_dir if raw_dir and all(c not in raw_dir for c in '<>:"|?*') else DEFAULT_OUTPUT_DIR
        os.makedirs(out_dir, exist_ok=True)

        text_area.insert(tk.END, f"🚀 Iniciando descarga, objetivo: {total} cartas, directorio de salida: {out_dir}\n")
        text_area.see(tk.END)

        def log_callback(msg):
            text_area.insert(tk.END, msg + "\n")
            text_area.see(tk.END)
            text_area.update()

        threading.Thread(target=lambda: fetch_and_save_cards(
            total_cards=total,
            output_dir=out_dir,
            clear_images=clear_var.get(),
            log_callback=log_callback
        ), daemon=True).start()

    root = tk.Tk()
    root.title("Herramienta de Generación de Pool de Cartas")

    frm = ttk.Frame(root, padding=12)
    frm.grid()

    ttk.Label(frm, text="🎴 Número de cartas objetivo:").grid(column=0, row=0, sticky="w")
    entry_var = tk.StringVar(value="500")
    ttk.Entry(frm, width=10, textvariable=entry_var).grid(column=1, row=0, sticky="w")

    ttk.Label(frm, text="📁 Directorio de salida (opcional):").grid(column=0, row=1, sticky="w")
    dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
    ttk.Entry(frm, width=30, textvariable=dir_var).grid(column=1, row=1, sticky="w")
    ttk.Button(frm, text="Elegir...", command=choose_directory).grid(column=2, row=1, padx=5)

    clear_var = tk.BooleanVar()
    clear_check = ttk.Checkbutton(frm, text="🧹 Borrar imágenes existentes", variable=clear_var)
    clear_check.grid(column=1, row=2, sticky="w")
    update_clear_checkbox_state()

    ttk.Button(frm, text="Iniciar generación", command=start_download).grid(column=1, row=3, pady=10)

    text_area = tk.Text(frm, width=70, height=20)
    text_area.grid(column=0, row=4, columnspan=3, pady=5)

    root.mainloop()

launch_gui()
