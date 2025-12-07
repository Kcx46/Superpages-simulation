'''
Este trabajo tiene  como fin el ser una simulacion interactiva y visuaL
de un mecanismo llamado Preferred Superpage Size Policy del paper
Practical, transparent operating system support for superpages
'''
import tkinter as tk
import math

#Mecanismo principal: PPage Allocation
counter_4mb = 0
counter_512kb = 0
counter_64kb = 0
counter_8kb = 0
superpages_sizes = [8*1024, 64*1024, 512*1024, 4*1024*1024]  #los tamaños son los mismos usados en el paper
base_page = 8*1024
drwaing_constants = {
    "x_start": 20, "y_start": 50,
    "block_width": 40, "block_height": 30,
    "canvas_width": 1000, "spacing": 5,
    "65536": 355, "524288": 64*40+315,
    "4194304": 512*40+(511*5), "8192": 40
}



  #inicialización de estructura para TLB     
global_time_counter = 0
tlb = []   # lista de diccionarios


def global_time():
    """Contador global para implementar LRU."""
    global global_time_counter
    global_time_counter += 1
    return global_time_counter


def tlb_lookup(vpn, page_size): 
    """Busca la entrada en el TLB.
    Esta función se usaría en dado caso que se tenga que buscar una traducción
    """
    
    for entry in tlb:
        if entry["valid"] and entry["vpn"] == vpn and entry["size"] == page_size:
            entry["last_used"] = global_time()
            return entry["ppn"]   
    return None 


def tlb_insert(vpn, ppn, page_size,TLB_SIZE):
    """Inserta una nueva entrada en el TLB usando LRU si está lleno."""
    # hay espacio libre
    if len(tlb) < TLB_SIZE:
        tlb.append({
            "vpn": vpn,
            "ppn": ppn,
            "size": page_size,
            "valid": True,
            "last_used": global_time()
        })
        return

    # reemplazo LRU
    victim = min(tlb, key=lambda e: e["last_used"])
    victim.update({
        "vpn": vpn,
        "ppn": ppn,
        "size": page_size,
        "valid": True,
        "last_used": global_time()
    })


def generate_vpn_ppn(page_size):
    """Genera VPN y PPN simples para demostrar la traducción."""
    vpn = global_time() * 10 + (page_size // 1024)
    ppn = global_time() * 20 + (page_size // 1024)
    return vpn, ppn


def draw_tlb():
    """Dibuja el contenido del TLB debajo del resto de la simulación."""
    x = 20
    y = 550  # parte baja del canvas

    canvas.create_text(x, y - 20, text="TLB (Traducciones activas):",
                       anchor="w", font=("Arial", 12, "bold"))

    for entry in tlb:
        if not entry["valid"]:
            continue

        rect_w = 260
        rect_h = 28

        canvas.create_rectangle(x, y, x + rect_w, y + rect_h, fill="yellow")
        canvas.create_text(
            x + rect_w / 2,
            y + rect_h / 2,
            text=f"VPN:{entry['vpn']}  PPN:{entry['ppn']}  SIZE:{entry['size']//1024}KB",
            font=("Arial", 9)
        )
        y += rect_h + 4

    update_scroll()






#  función para actualizar scroll ---
def update_scroll():
    canvas.configure(scrollregion=canvas.bbox("all"))


def preferred_superpage_policy(size_memory_object, isdynamic, superpages_sizes):
    if isdynamic == 1:
        preferred_superpage = base_page
        for i in superpages_sizes:
            if i > size_memory_object:
                break
            preferred_superpage = i
        return preferred_superpage


def draw_map(size_memory_object):
    x = drwaing_constants["x_start"]
    y = drwaing_constants["y_start"]
    i = 0
    blocks = math.ceil(size_memory_object/base_page)
    while i < blocks:

        canvas.create_rectangle(x,y,x+drwaing_constants["block_width"],
                                y+drwaing_constants["block_height"], fill="lightblue")
        canvas.create_text(x+drwaing_constants["block_width"],
                           y+drwaing_constants["block_height"]*0.7, text="MAP")

        x += drwaing_constants["block_width"] + drwaing_constants["spacing"]

        if x + drwaing_constants["block_width"] > drwaing_constants["canvas_width"]:
                x = drwaing_constants["x_start"]
                y += drwaing_constants["block_height"] + drwaing_constants["spacing"]
        i += 1
    
    update_scroll()


def draw_superpages(size_memory_object, tlb_size):
    """
    Éste fue uno de los algoritmos que más me entretuvo porque tenía que tomar en cuenta el cómo seleccionar la superpagina
    ideal, sino dibujarla y dado que no cuento con espacio vertical infinito, tuve que hacer los calculos para que,
    en dado caso de pasasrse del ancho, ajustarse debajo. 
    """
    x = drwaing_constants["x_start"]
    y = drwaing_constants["y_start"]

    remaining = size_memory_object
    while remaining > 0:
        superpages_sizes2 = [4*1024*1024, 512*1024, 64*1024, 8*1024]
        for i in superpages_sizes2:
            if i <= remaining:
                page_size = i
                break
            else:
                page_size = superpages_sizes2[-1]

        total_width = drwaing_constants[f"{page_size}"]
        width_left = total_width

        # insertar en TLB
        vpn, ppn = generate_vpn_ppn(page_size)
        tlb_insert(vpn, ppn, page_size,tlb_size)

        while width_left > 0:
            available = 965 - x
            
            if available <= 0:
                x = drwaing_constants["x_start"]
                y += drwaing_constants["block_height"] + drwaing_constants["spacing"]
                available = 965 - x

            draw_width = min(available, width_left)

            canvas.create_rectangle(x,y, x + draw_width,
                                    y+drwaing_constants["block_height"], fill="lightblue")
            canvas.create_text(x + draw_width/2 ,
                               y + drwaing_constants["block_height"]/2,
                               text=f"{page_size//1024}KB")

            x += draw_width + drwaing_constants["spacing"]
            width_left -= draw_width

        remaining -= page_size

    update_scroll()


def draw_reservation(size_memory_object):
    x = drwaing_constants["x_start"]
    y = drwaing_constants["y_start"]
    blocks = math.ceil(size_memory_object/base_page)
    numero = blocks % 8

    if numero != 0:
        remaining = abs(numero - 8)

        for i in range(blocks + remaining):
            canvas.create_rectangle(x, y, x + drwaing_constants["block_width"],
                                    y + drwaing_constants["block_height"],
                                    tags=("map_block"), fill="lightblue")
            canvas.create_text(x+drwaing_constants["block_width"]/2,
                               y+drwaing_constants["block_height"]/6, text="Free")
            canvas.create_text(x+drwaing_constants["block_width"]/2,
                               y+drwaing_constants["block_height"]*0.7, text="8KB")
            x += drwaing_constants["block_width"] + drwaing_constants["spacing"]

            if x + drwaing_constants["block_width"] > drwaing_constants["canvas_width"]:
                x = drwaing_constants["x_start"]
                y += drwaing_constants["block_height"] + drwaing_constants["spacing"]
    
    update_scroll()


def draw_base_pages(memory):
    canvas.delete("all")
    blocks = memory // base_page
    x = drwaing_constants["x_start"]
    y = drwaing_constants["y_start"]
    
    for i in range(blocks):
        canvas.create_rectangle(x,y,x+drwaing_constants["block_width"],
                                y+drwaing_constants["block_height"], fill="lightgreen")
        canvas.create_text(x+drwaing_constants["block_width"]/2,
                           y+drwaing_constants["block_height"]*0.7, text="8KB")
        
        x += drwaing_constants["block_width"] + drwaing_constants["spacing"]
        if x + drwaing_constants["block_width"] > drwaing_constants["canvas_width"]:
            x = drwaing_constants["x_start"]
            y += drwaing_constants["block_height"] + drwaing_constants["spacing"]

    update_scroll()


###########################################################
#                     SIMULAR
###########################################################

def simular():
    global tlb
    tlb = []   # limpiar TLB cada simulación

    counter_512kb = 0
    counter_4mb = 0
    counter_512kb = 0
    counter_64kb = 0
    counter_8kb = 0

    mem_comp = int(entry_memoria.get()) * 1024
    mem_obj = int(entry_memory_object.get()) * 1024
    TLB_SIZE = int(entry_tamaño_TLB.get())

    draw_base_pages(mem_comp)
    #draw_superpages(mem_obj)
    draw_reservation(mem_obj)
    draw_superpages(mem_obj, TLB_SIZE)

    # estadísticas
    remaining = mem_obj
    while remaining > 0:
        superpages_sizes2 = [4*1024*1024, 512*1024, 64*1024, 8*1024]
        for i in superpages_sizes2:
            if i <= remaining:
                page_size = i
                if page_size ==4*1024*1024:
                    counter_4mb += 1
                elif page_size ==  512*1024:
                    counter_512kb += 1
                elif page_size == 64*1024:
                    counter_64kb += 1
                elif page_size <= 8*1024:
                    counter_8kb
                break
        remaining -= page_size    

    page_to_use = preferred_superpage_policy(mem_obj,1,superpages_sizes)
    valor.set(f"{page_to_use//1024} KB")
    var_8kb.set(f"({counter_8kb})")
    var_64kb.set(f"({counter_64kb})")
    var_512kb.set(f"({counter_512kb})")
    var_4mb.set(f"({counter_4mb})")

    draw_tlb()


#############################################
#   INTERFAZ + SCROLL
#############################################

root = tk.Tk() 
root.title("Simulacion de superpages")

canvas_frame = tk.Frame(root)
canvas_frame.pack()

scrollbar = tk.Scrollbar(canvas_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

canvas = tk.Canvas(canvas_frame, width=1000, height=600, yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, expand=True)
scrollbar.config(command=canvas.yview)

form = tk.Frame(root)
form.pack(pady=10)

tk.Label(form, text="Tamaño total de memoria (KB): ").grid(row=0, column=0) #etiqueta de tamaño total de memoria
tk.Label(form, text="Tamaño de TLB (entradas): ").grid(row=3, column=0)  #etiqueta de tamaño total de entradas de la tlb
tk.Label(form, text="Tamaño del memory object (KB): ").grid(row=1, column=0) #etiqueta del tamaño del memory object
tk.Label(form, text="Tamaño de pagina elegido (KB):").grid(row=2, column=0) #etiqueta del tamaño MAX de superpagiuna elegido

valor = tk.StringVar()
var_8kb = tk.StringVar()
var_64kb = tk.StringVar()
var_512kb = tk.StringVar()
var_4mb = tk.StringVar()

tk.Label(form, textvariable=valor).grid(row=2, column=1)
tk.Label(form, textvariable=var_64kb).grid(row=4, column=1)
tk.Label(form, textvariable=var_512kb).grid(row=5, column=1)
tk.Label(form, textvariable=var_4mb).grid(row=6, column=1)

tk.Label(form, text="Paginas de 64 (KB): ").grid(row=4, column=0)
tk.Label(form, text="Paginas de 512 (KB): ").grid(row=5, column=0)
tk.Label(form, text="Paginas de 4192 (KB): ").grid(row=6, column=0)

entry_memoria = tk.Entry(form)  #entrada del total de memoria
entry_memoria.grid(row=0, column=1) 

entry_memory_object = tk.Entry(form) #entrada del tamaño del memory object
entry_memory_object.grid(row=1, column=1)

entry_tamaño_TLB = tk.Entry(form) #entrada del tamaño de la TLB
entry_tamaño_TLB.grid(row=3, column=1)

tk.Button(root, text="Simular", command=simular).pack(pady=10)

root.mainloop()
