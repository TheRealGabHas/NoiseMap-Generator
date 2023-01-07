import datetime
import time
import tkinter as tk
from tkinter import ttk
from lib import noise
from PIL import Image, ImageTk
import os

# Create the main window
window = tk.Tk()
window.title("NoiseMap Generator")
window.geometry(f"1080x720")  # 1080x720
window.resizable(False, False)  # Window is now not resizable
window.grid_columnconfigure(0, weight=1)
window.wm_iconphoto(True, tk.PhotoImage(file="./asset/treasure-map.ico"))

menu = tk.Menu(window)
item = tk.Menu(menu)
item.add_command(label='Open')
menu.add_cascade(label='File', menu=item)
window.config(menu=menu)


class GUI:

    def __init__(self, master, clear_cache=True):
        self.master = master
        self.octave = 0
        self.size = (512, 512)
        self.seed = 0
        self.path = "./asset/cache"
        self.default_path = "./asset/cache"
        self.name = "sample"
        self.preview = True
        self.default_img = ImageTk.PhotoImage(Image.open(f"./asset/blank.png"))
        self.current_img = self.default_img
        self.clear = clear_cache

    def create_img(self) -> None:

        generate_btn.configure(text="Generating...", state="disabled")

        beggining = time.time()

        img = noise.Noise()
        img.set_octave(self.octave)
        img.set_size(self.size)
        img.set_path(self.default_path)
        img.set_seed(self.seed)

        img.create_canvas()
        img.apply_noise()

        end = time.time()

        generate_btn.configure(text="Generate", state="enabled")
        gen_label.configure(text=f"Generation done in {end - beggining:.2f}s")
        # Save the image in the cache folder
        img.save_img(self.name)
        self.current_img = ImageTk.PhotoImage(Image.open(f"{self.default_path}/{self.name}.png"))
        save_btn.configure(state="enabled")

    def display_img(self) -> None:
        if not self.preview:
            console.log("Image generated but too large to be previewed in this window.")
            Image.open(f"{self.path}/{self.name}.png").show()
            console.log("Image successfully previewed in a separated window.")
            return

        # Delete the last image
        window.winfo_children()[-1].destroy()

        r_img = self.current_img
        lbl = ttk.Label(self.master, image=r_img)
        lbl.image = r_img
        lbl.grid(column=1, row=0, sticky=tk.NS, pady=35, padx=10)

    def save_file(self):
        img = Image.open(rf'{self.default_path}/{self.name}.png')

        if os.path.exists(f"{self.path}/{self.name}.png"):
            self.name += f"{datetime.datetime.now().strftime('-%b-%d-%Y-%H%M%S')}"

        try:
            img.save(f"{self.path}/{self.name}.png")
            console.log(f"Image saved as {self.path}/{self.name}.png")
        except PermissionError:
            console.log(f"Don't have permission to save in this directory")

    def clear_cache(self):
        if self.clear:
            cache_path = './asset/cache'
            for f in os.listdir(cache_path):
                os.remove(os.path.join(cache_path, f))

            console.log("Cache successfully cleared")


class Console:

    def __init__(self, entry: ttk.Label):
        self.entry_field = entry
        self.content = ""
        self.total_content = []
        self.line_index = 0
        self.clear_session_logs()

    @staticmethod
    def clear_session_logs():
        f = open("./logs/session.txt", "w")
        f.close()

    def update(self) -> None:
        if self.content == "":
            return

        txt = ""
        with open("./logs/session.txt", "r") as logs:
            for line in logs.readlines()[-5:]:
                txt += line

        self.entry_field.configure(text=txt)

    def log(self, content):
        self.content = content

        with open("./logs/session.txt", "a") as session_logs:
            session_logs.write(f"[{datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}] {content}\n")

        with open("./logs/all_time.txt", "a") as all_time_logs:
            all_time_logs.write(f"[{datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}] {content}\n")

        self.update()


gui = GUI(window)
gui.display_img()


def is_valid(expected: str, content: str) -> bool:
    if expected == "int" and content.isdigit() and int(content) > 0:
        return True
    else:
        console.log("Invalid field found in : 'width', 'height', 'octave', 'seed'")
        return False


def gen_img():
    # Get all data needed to generate an image
    width = ask_width_entry.get()
    height = ask_height_entry.get()
    octave = ask_octave_entry.get()
    seed = ask_seed_entry.get()

    allowed = True

    save_name = ask_fname_entry.get()
    for char in save_name:
        if char in ["\\", "/", ":", "*", "?", "<", ">", "|"]:
            allowed = False
            console.log("Invalid file name given (contains \\ / : * ? \" < > | )")
            break

    validity: dict = {
        "width": is_valid("int", width),
        "height": is_valid("int", height),
        "octave": is_valid("int", octave),
        "seed": is_valid("int", seed),
    }

    # check if every field is valid and allow or not the generation
    for line in validity.values():
        if not line:
            allowed = False

    # Process if there are invalid field
    if not allowed:
        return

    width, height, octave, seed = int(width), int(height), int(octave), int(seed)

    gui.preview = True
    if width > 512 or height > 512:
        gui.preview = False

    if save_name == "" or save_name is None:
        save_name = "my_image"

    gui.size = (width, height)
    gui.seed = seed
    gui.octave = octave
    gui.name = save_name

    gui.create_img()
    console.log(f"Image successfully generated. ({gui.size[0]}x{gui.size[1]})")
    gui.display_img()
    console.log(f"Image successfully displayed.")
    save_btn.configure(text="Save")


def save_img():
    save_foler = ask_save_foler_entry.get()
    save_name = ask_fname_entry.get()

    if not os.path.exists(save_foler):
        console.log("Invalid path given")
        return

    for char in save_name:
        if char in ["\\", "/", ":", "*", "?", "<", ">", "|"]:
            console.log("Invalid file name given (contains \\ / : * ? \" < > | )")
            break

    if save_name == "" or save_name is None:
        save_name = "my_image"
        console.log("No name given. Default is \"my_image\"")

    if gui.name == "my_image" and save_name != "my_image":
        os.rename(f"{gui.path}/{gui.name}.png", f"{gui.path}/{save_name}.png")
        gui.name = save_name

    gui.name = save_name
    gui.path = save_foler

    gui.save_file()
    # Get all data needed to save the image
    save_btn.configure(text="Saved !")


def change_color(arg):
    print(arg)
    entry_lst = [ask_width_entry, ask_height_entry, ask_octave_entry, ask_seed_entry]
    for entries in entry_lst:
        if entries.get().isdigit() and len(list(entries.get())) > 0:
            if int(entries.get()) > 0:
                entries.configure(foreground="black")
        else:
            entries.configure(foreground="red")


# Column title
left_title = ttk.Label(window, text="Configure Map Settings")
left_title.grid(column=0, row=0, sticky=tk.N)

right_title = ttk.Label(window, text="Map Preview")
right_title.grid(column=1, row=0, sticky=tk.N)

# Configuration Label/ Entries
# Width label/ entry
ask_width_label = ttk.Label(window, text="width :")
ask_width_label.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=50)

ask_width_entry = ttk.Entry(window, width=10, foreground="black")
ask_width_entry.bind("<FocusOut>", change_color)
ask_width_entry.grid(column=0, row=0, sticky=tk.NW, padx=70, pady=50)

# Height label/ entry
ask_height_label = ttk.Label(window, text="height :")
ask_height_label.grid(column=0, row=0, sticky=tk.NW, padx=150, pady=50)

ask_height_entry = ttk.Entry(window, width=10, foreground="black")
ask_height_entry.bind("<FocusOut>", change_color)
ask_height_entry.grid(column=0, row=0, sticky=tk.NW, padx=200, pady=50)

# Size warning
size_caution_label = ttk.Label(window, text="Note: Inputting size values greater than 512 will result in the preview being in another window")
size_caution_label.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=80)

# Seed and octave label/ entry
ask_octave_label = ttk.Label(window, text="octave :")
ask_octave_label.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=110)

ask_octave_entry = ttk.Entry(window, width=10, foreground="black")
ask_octave_entry.insert(0, "1")
ask_octave_entry.bind("<FocusOut>", change_color)
ask_octave_entry.grid(column=0, row=0, sticky=tk.NW, padx=70, pady=110)

ask_seed_label = ttk.Label(window, text="seed :")
ask_seed_label.grid(column=0, row=0, sticky=tk.NW, padx=150, pady=110)

ask_seed_entry = ttk.Entry(window, width=20, foreground="black")
ask_seed_entry.bind("<FocusOut>", change_color)
ask_seed_entry.grid(column=0, row=0, sticky=tk.NW, padx=200, pady=110)

# Save config title
save_title = ttk.Label(window, text="Saving Configuration")
save_title.grid(column=0, row=0, sticky=tk.N, pady=150)

# File name and path to save folder
ask_fname_label = ttk.Label(window, text="Save file as :")
ask_fname_label.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=180)

ask_fname_entry = ttk.Entry(window, width=30, foreground="black")
ask_fname_entry.grid(column=0, row=0, sticky=tk.NW, padx=100, pady=180)

ask_save_foler_label = ttk.Label(window, text="Path to saving directory :")
ask_save_foler_label.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=210)

ask_save_foler_entry = ttk.Entry(window, width=50, foreground="black")
ask_save_foler_entry.grid(column=0, row=0, sticky=tk.NW, padx=170, pady=210)

# Generation label
gen_label = ttk.Label(window, text="")
gen_label.grid(column=1, row=1, sticky=tk.NE, ipadx=10)

# Generation button
generate_btn = ttk.Button(window, text="Generate", command=gen_img)
generate_btn.grid(column=1, row=1, sticky=tk.N)

# Save button
save_btn = ttk.Button(window, text="Save", command=save_img, state="disabled")
save_btn.grid(column=1, row=1, sticky=tk.W)

# Separator
left_separator = ttk.Separator(window, orient="vertical")
left_separator.grid(column=0, row=0)

# Log title
log_title = ttk.Label(window, text="Logs :")
log_title.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=250)


log_cons = ttk.Label(window, text="")
log_cons.grid(column=0, row=0, sticky=tk.NW, padx=20, pady=280)

# Init the console with "log_cons" as output label
console = Console(log_cons)
console.log("Software launched successfully")
gui.clear_cache()

# to_kill
to_kill = ttk.Label(window, text="")

# Welcome logs
console.log("----------")
console.log("NoiseMap Generator")
console.log("-- By GabHas")


# Run the Tkinter event loop
window.mainloop()
