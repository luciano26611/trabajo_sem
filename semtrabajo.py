import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import random

# Cargar el archivo CSV
df = pd.read_csv("books.csv")

# Inicializar vectores TF-IDF y matriz de similitud coseno
tfidf_vectorizer = TfidfVectorizer(stop_words="english")
df["description"] = df["description"].fillna("")
tfidf_matrix = tfidf_vectorizer.fit_transform(df["description"])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Inicializar variables para almacenar las calificaciones de los usuarios
experiencias_usuario = {}

# Función para obtener recomendaciones basadas en el título de un libro

libros_con_ids = []

# Cantidad de libros por pagina

libros_por_pagina = 50


def mostrar_calificaciones():
    calificaciones_texto = "\n".join(
        [
            f"{libro}: {calificacion}"
            for libro, calificacion in experiencias_usuario.items()
        ]
    )
    messagebox.showinfo("Calificaciones Registradas", calificaciones_texto)


def obtener_recomendaciones():
    titulo_libro = entry_titulo.get()

    if titulo_libro not in indices:
        messagebox.showerror(
            "Error", f"El libro '{titulo_libro}' no se encontró en la base de datos."
        )
        return

    idx = indices[titulo_libro]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(
        sim_scores, key=lambda x: x[1], reverse=True if sim_scores else False
    )

    # Obtener las 10 mejores recomendaciones
    libro_indices = [i[0] for i in sim_scores[1:11]]

    # Crear una lista de libros recomendados con títulos y IDs
    recomendaciones = [(df["title"].iloc[i], i) for i in libro_indices]

    # Actualizar el label de recomendaciones para mostrar solo los títulos
    texto_recomendaciones = f"Recomendaciones para '{titulo_libro}':\n"
    texto_recomendaciones += "\n".join([libro[0] for libro in recomendaciones])
    resultado_recomendaciones.config(text=texto_recomendaciones)

    # Almacenar los libros recomendados con títulos y IDs
    libros_con_ids = recomendaciones


# Función para registrar la calificación del usuario


def on_lista_doble_clic(event):
    widget = event.widget
    seleccion = widget.curselection()
    if seleccion:
        libro_seleccionado = widget.get(seleccion[0])
        entry_titulo.delete(0, tk.END)
        entry_titulo.insert(0, libro_seleccionado)
        entry_titulo_calificaciones.delete(0, tk.END)
        entry_titulo_calificaciones.insert(0, libro_seleccionado)


def calificar_libro():
    titulo_libro = entry_titulo.get()
    calificacion = entry_calificacion.get()
    if titulo_libro and calificacion:
        try:
            calificacion = float(calificacion)
            if 1.0 <= calificacion <= 5.0:
                experiencias_usuario[titulo_libro] = calificacion
                resultado_calificaciones.config(
                    text=f"Calificación registrada para '{titulo_libro}': {calificacion}",
                    foreground="green",
                )

                # Limpiar el campo de calificación
                entry_calificacion.delete(0, tk.END)
            else:
                resultado_calificaciones.config(
                    resultado_calificaciones.config(
                        text="La calificación debe estar entre 1.0 y 5.0",
                        foreground="red",
                    )
                )
        except ValueError:
            resultado_calificaciones.config(
                text="La calificación debe ser un número válido", foreground="red"
            )


# Crear un índice para rastrear la página actual
pagina_actual = 1


# Función para avanzar a la siguiente página de libros
def avanzar_pagina():
    global pagina_actual
    pagina_actual += 1
    mostrar_libros_en_lista()


# Función para retroceder a la página anterior de libros
def retroceder_pagina():
    global pagina_actual
    if pagina_actual > 1:
        pagina_actual -= 1
        mostrar_libros_en_lista()


# Función para mostrar los libros en la lista según la página actual
def mostrar_libros_en_lista():
    lista_libros.delete(0, tk.END)  # Limpiar la lista
    inicio = (pagina_actual - 1) * libros_por_pagina
    fin = inicio + libros_por_pagina
    for title in df["title"].iloc[inicio:fin]:
        lista_libros.insert(tk.END, title)


# Crear ventana
ventana = tk.Tk()
ventana.title("Recomendador de Libros")

# Crear pestañas
pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="both", expand="yes")


# pestaña_recomendaciones = ttk.Frame(pestanas)
# pestanas.add(pestaña_recomendaciones, text="Calificaciones")


# Crear un índice de títulos de libros
indices = pd.Series(df.index, index=df["title"]).drop_duplicates()


# Pestaña de recomendaciones y lista de libros
pestaña_recomendaciones = ttk.Frame(pestanas)
pestanas.add(pestaña_recomendaciones, text="Recomendaciones y Lista de Libros")

# Crear y configurar elementos de la interfaz para recomendaciones
label_titulo = ttk.Label(pestaña_recomendaciones, text="Título del Libro:")
entry_titulo = ttk.Combobox(pestaña_recomendaciones, values=df["title"])
boton_recomendar = ttk.Button(
    pestaña_recomendaciones,
    text="Obtener Recomendaciones",
    command=obtener_recomendaciones,
)
resultado_recomendaciones = ttk.Label(
    pestaña_recomendaciones, text="", wraplength=400, justify="left"
)

# Crear y configurar elementos de la interfaz para la lista de libros
label_lista_libros = ttk.Label(
    pestaña_recomendaciones, text="Hasta 50 libros de la base de datos:"
)
lista_libros = tk.Listbox(pestaña_recomendaciones)
for i, title in enumerate(df["title"].head(50)):
    lista_libros.insert(i, title)

lista_libros.bind("<Double-1>", on_lista_doble_clic)

# Botones para avanzar y retroceder páginas
boton_avanzar = ttk.Button(
    pestaña_recomendaciones, text="Avanzar página", command=avanzar_pagina
)
boton_retroceder = ttk.Button(
    pestaña_recomendaciones, text="Retroceder página", command=retroceder_pagina
)


# Crear un índice de títulos de libros
indices = pd.Series(df.index, index=df["title"]).drop_duplicates()

# Sección para Recomendar Libros
frame_recomendar = ttk.LabelFrame(pestaña_recomendaciones, text="Recomendar Libros")
frame_recomendar.pack(fill="both", expand="yes", padx=10, pady=10)

label_titulo = ttk.Label(frame_recomendar, text="Título del Libro:")
entry_titulo = ttk.Combobox(frame_recomendar, values=df["title"])
boton_recomendar = ttk.Button(
    frame_recomendar, text="Obtener Recomendaciones", command=obtener_recomendaciones
)
resultado_recomendaciones = ttk.Label(
    frame_recomendar, text="", wraplength=400, justify="left"
)

label_titulo.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_titulo.grid(row=0, column=1, padx=5, pady=5)
boton_recomendar.grid(row=0, column=2, padx=5, pady=5)
resultado_recomendaciones.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

# Sección para Lista de Libros
frame_lista_libros = ttk.LabelFrame(pestaña_recomendaciones, text="Lista de Libros")
frame_lista_libros.pack(fill="both", expand="yes", padx=10, pady=10)

label_lista_libros = ttk.Label(
    frame_lista_libros, text="Hasta 50 libros de la base de datos:"
)
lista_libros = tk.Listbox(frame_lista_libros)
for i, title in enumerate(df["title"].head(50)):
    lista_libros.insert(i, title)

lista_libros.bind("<Double-1>", on_lista_doble_clic)

boton_avanzar = ttk.Button(
    frame_lista_libros, text="Avanzar página", command=avanzar_pagina
)
boton_retroceder = ttk.Button(
    frame_lista_libros, text="Retroceder página", command=retroceder_pagina
)

label_lista_libros.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky="w")
lista_libros.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
boton_avanzar.grid(row=2, column=0, padx=5, pady=5)
boton_retroceder.grid(row=2, column=1, padx=5, pady=5)

# Pestaña para Calificaciones
# pestaña_recomendaciones = ttk.Frame(pestanas)
# pestanas.add(pestaña_recomendaciones, text="Calificaciones")

# Sección para Calificaciones
frame_calificaciones = ttk.LabelFrame(pestaña_recomendaciones, text="Calificaciones")
frame_calificaciones.pack(fill="both", expand="yes", padx=10, pady=10)

label_titulo_calificaciones = ttk.Label(frame_calificaciones, text="Título del Libro:")
entry_titulo_calificaciones = ttk.Entry(frame_calificaciones)
label_calificacion = ttk.Label(frame_calificaciones, text="Calificación (1.0 - 5.0):")
entry_calificacion = ttk.Entry(frame_calificaciones)
boton_calificar = ttk.Button(
    frame_calificaciones, text="Calificar Libro", command=calificar_libro
)
boton_mostrar_calificaciones = ttk.Button(
    frame_calificaciones, text="Mostrar Calificaciones", command=mostrar_calificaciones
)
resultado_calificaciones = ttk.Label(
    frame_calificaciones, text="", wraplength=400, justify="left"
)

label_titulo_calificaciones.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_titulo_calificaciones.grid(row=0, column=1, ipadx=5, padx=5, pady=5)
label_calificacion.grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_calificacion.grid(row=1, column=1, padx=5, pady=5)
boton_calificar.grid(row=2, column=0, padx=5, pady=5)
boton_mostrar_calificaciones.grid(row=2, column=1, padx=5, pady=5)
resultado_calificaciones.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Iniciar la aplicación
ventana.mainloop()
