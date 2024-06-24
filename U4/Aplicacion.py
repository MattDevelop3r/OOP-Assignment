from gestorJugadores import GestorJugadores
from funcionesAnexadas import centrar_ventana
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, Tk, Canvas, IntVar, Menu, Entry, Button, CENTER
from functools import partial
import random

class Aplicacion(tk.Tk):
    __ventana: object
    __canvas_frame: object
    __boton_verde: object
    __boton_rojo: object
    __boton_amarillo: object
    __boton_azul: object
    __puntaje: IntVar
    __botones_habilitados: bool
     #COLORES      VERDE       ROJO     AMARILLO     AZUL
    __colores = ['#009900', '#990000', '#AAAA00', '#000099']
    __colores_claros = ['#88FF88', '#FF8888', '#FFFF66', '#6666FF']
    __colores_oscuros = ['#007700', '#770000', '#777700', '#000077']
    __secuencia: list
    __indice_actual: int
    __ventana_nombre: object
    __nombre_jugador: str
    __ventana_puntajes: object

    def __init__(self):
        self.__botones_habilitados = False
        self.__secuencia = []
        self.__indice_actual = 0
        self.__nombre_jugador = "" 
        self.__boton_reintentar = None

        # inicializar la ventana principal
        self.__ventana = Tk()
        self.__ventana.geometry("720x720")
        self.__ventana.title("Simon Game - JugateYa")
        self.__ventana.withdraw() 
        self.__puntaje = IntVar(value=0)
        
        # inicializar la ventana de ingresar el nombre
        self.__ventana_nombre = Tk()
        self.__ventana_nombre.geometry("400x150")
        self.__ventana_nombre.resizable(0,0)
        centrar_ventana(self.__ventana_nombre)
        self.__ventana_nombre.title("Ingresar Nombre")
        self.__ventana_nombre.configure(bg='#AABBCC')     

        ttk.Label(self.__ventana_nombre, text = 'Datos del jugador', font=('Noto Sans Bold', 12), background= '#AABBCC').grid(row = 0, column= 0, sticky="w", padx= 20, pady= 10)
        ttk.Label(self.__ventana_nombre, text = 'Jugador: ', font=('Noto Sans Bold', 12), background= '#AABBCC').grid(row = 1, column=0,  sticky="w", padx= 20)
        self.__entrada_nombre = Entry(self.__ventana_nombre, font=('Noto Sans', 11), width= 21, background= "#DDDDDD")
        self.__entrada_nombre.grid(row = 1, column=1, columnspan= 2, sticky="w")
        Button(self.__ventana_nombre, text='Iniciar Juego', command=self.iniciar_juego, bg='red', fg='white', font=('Noto Sans Bold', 12)).grid(row=2, columnspan= 10, sticky="ns", pady= 10)
        self.__ventana_nombre.bind("<Return>", self.iniciar_juego)

        # barra de menu
        barraMenu = Menu(self.__ventana, font=('Noto Sans', 12))
        menuPuntajes = Menu(barraMenu, tearoff=0, font=('Noto Sans', 10)) 
        menuPuntajes.add_separator()
        menuPuntajes.add_command(label="Ver puntajes", command=self.ver_puntajes, accelerator='P')
        menuPuntajes.add_command(label="Salir", command=self.salir, accelerator='Alt+F4')
        barraMenu.add_cascade(label="Puntajes", menu=menuPuntajes)
        self.__ventana.config(menu=barraMenu)
        self.__ventana.bind("P", self.ver_puntajes)
        self.__ventana.bind("p", self.ver_puntajes)

        # frame de puntaje 
        style = ttk.Style()
        style.configure("Puntaje.TFrame", background="#222222")
        self.__frame_puntaje = ttk.Frame(self.__ventana, padding="5 5 5 5", style="Puntaje.TFrame")
        self.__frame_puntaje.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.__frame_puntaje.grid_columnconfigure(0, weight=1)
        self.__frame_puntaje.grid_columnconfigure(1, weight=1)
        self.__puntaje_texto = ttk.Label(self.__frame_puntaje, font=('Noto Sans', 16), background='#222222', foreground='#FFFFFF')
        self.__puntaje_texto.grid(row=0, ipadx=0, column=0, sticky="s")
        self.__puntaje_label = ttk.Label(self.__frame_puntaje, textvariable=self.__puntaje, font=('Noto Sans', 16), background='#222222', foreground='#FFFFFF')
        self.__puntaje_label.grid(row=0, ipadx=0, column=1, sticky="s")

        # frame de botones
        self.__canvas_frame = tk.Frame(self.__ventana, bg='#222222')
        self.__canvas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.__ventana.grid_rowconfigure(1, weight=1)
        self.__ventana.grid_columnconfigure(0, weight=1)
        self.__ventana.grid_columnconfigure(1, weight=1)
        self.__canvas_frame.grid_rowconfigure(0, weight=1)
        self.__canvas_frame.grid_rowconfigure(1, weight=1)
        self.__canvas_frame.grid_columnconfigure(0, weight=1)
        self.__canvas_frame.grid_columnconfigure(1, weight=1)
        
        self.__boton_verde = Canvas(self.__canvas_frame, bg=self.__colores[0], relief="raised", bd=3)
        self.__boton_verde.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.__boton_rojo = Canvas(self.__canvas_frame, bg=self.__colores[1], relief="raised", bd=3)
        self.__boton_rojo.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.__boton_amarillo = Canvas(self.__canvas_frame, bg=self.__colores[2], relief="raised", bd=3)
        self.__boton_amarillo.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.__boton_azul = Canvas(self.__canvas_frame, bg=self.__colores[3], relief="raised", bd=3)
        self.__boton_azul.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        for color in self.__colores:
            boton = self.obtener_boton_por_color(color)
            boton.bind("<Button-1>", partial(self.apretar_boton, color))
            boton.bind("<Enter>", partial(self.al_entrar_mouse, color))
            boton.bind("<Leave>", partial(self.al_salir_mouse, color))

    def iniciar_juego(self, event=None):
        self.__nombre_jugador = self.__entrada_nombre.get().strip()
        if self.__nombre_jugador == "":
            messagebox.showerror("Error", "Ingrese el nombre del jugador")
            return
        self.__puntaje_texto.config(text=f"{self.__nombre_jugador}")
        self.__ventana_nombre.destroy()
        centrar_ventana(self.__ventana)
        self.__ventana.deiconify()
        
        self.__ventana.after(1000, self.agregar_a_secuencia)
    
    def al_entrar_mouse(self, color, event=None):
        if self.__botones_habilitados:
            boton = self.obtener_boton_por_color(color)
            indice = self.__colores.index(color)
            boton.config(bg=self.__colores_claros[indice])

    def al_salir_mouse(self, color, event=None):
        if self.__botones_habilitados:
            boton = self.obtener_boton_por_color(color)
            boton.config(bg=color)

    def apretar_boton(self, color, event=None):
        if not self.__botones_habilitados:
            return
        indice = self.__colores.index(color)
        boton = self.obtener_boton_por_color(color)
        boton.config(bg=self.__colores_oscuros[indice])
        self.__ventana.after(100, partial(boton.config, bg=color))
        
        if color == self.__secuencia[self.__indice_actual]:
            self.__indice_actual += 1
            if self.__indice_actual == len(self.__secuencia):
                self.__puntaje.set(self.__puntaje.get() + 1)
                self.__indice_actual = 0
                self.__botones_habilitados = False
                self.__ventana.after(1000, self.agregar_a_secuencia)
        else:
            self.guardar_puntaje()
            messagebox.showinfo("GAME OVER", f"El Puntaje obtenido es: {self.__puntaje.get()}")
            self.mostrar_boton_reintentar()

    def mostrar_boton_reintentar(self):
        self.__overlay = Canvas(self.__ventana, bg='#000000', highlightthickness=0)
        self.__overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.__overlay.create_rectangle(0, 0, self.__ventana.winfo_width(), self.__ventana.winfo_height(), 
                                        fill='black', stipple='gray50')

        if self.__boton_reintentar is None:
            self.__boton_reintentar = Button(self.__ventana, text="Volver a Jugar", command=self.reiniciar_juego, 
                                        bg='green', fg='white', font=('Noto Sans Bold', 20), 
                                        width=15, height=2)
            self.__boton_reintentar.bind("<Enter>", self.entrar_boton_reintentar)
            self.__boton_reintentar.bind("<Leave>", self.salir_boton_reintentar)

        self.__boton_reintentar.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.__botones_habilitados = False
    
    def entrar_boton_reintentar(self, event):
        try:
            self.__boton_reintentar.config(bg='dark green')
        except AttributeError as e:
            print(e)

    def salir_boton_reintentar(self, event):
        try:
            self.__boton_reintentar.config(bg='green')
        except AttributeError as e:
            print(e)

    def reiniciar_juego(self):
        self.__puntaje.set(0)
        self.__secuencia = []
        self.__indice_actual = 0
        self.__botones_habilitados = False
        if self.__boton_reintentar:
            self.__boton_reintentar.place_forget()
        if self.__overlay:
            self.__overlay.place_forget()
        self.__ventana.after(1000, self.agregar_a_secuencia)
        self.__boton_reintentar = None
        self.__overlay = None

    def agregar_a_secuencia(self):
        self.__secuencia.append(random.choice(self.__colores))
        self.mostrar_secuencia(self.__secuencia)
    
    def mostrar_secuencia(self, secuencia):
        self.__botones_habilitados = False
        for i, color in enumerate(secuencia):
            boton = self.obtener_boton_por_color(color)
            self.__ventana.after(i * 1000, partial(self.cambiar_color, boton, color))
        if (len(secuencia) > 1):
            self.__ventana.after((len(secuencia) - 1) * 1000, self.habilitar_botones)
        else: self.__ventana.after(len(secuencia) * 1000, self.habilitar_botones)

    def cambiar_color(self, boton, color):
        boton.config(bg='white')
        self.__ventana.after(500, partial(boton.config, bg=color))
    
    def habilitar_botones(self):
        self.__botones_habilitados = True

    def obtener_boton_por_color(self, color):
        if color == self.__colores[0]:
            return self.__boton_verde
        elif color == self.__colores[1]:
            return self.__boton_rojo
        elif color == self.__colores[2]:
            return self.__boton_amarillo
        elif color == self.__colores[3]:
            return self.__boton_azul

    def guardar_puntaje(self):
        fecha_actual = datetime.now()
        datos_puntaje = { "jugador": self.__nombre_jugador, "fecha": fecha_actual.strftime("%Y-%m-%d"), "hora": fecha_actual.strftime("%H:%M:%S"), "puntuacion": self.__puntaje.get()}
        
        try:
            with open("pysimonpuntajes.json", "r") as archivo:
                puntajes = json.load(archivo)
        except FileNotFoundError:
            puntajes = []
        
        puntajes.append(datos_puntaje)
        
        with open("pysimonpuntajes.json", "w") as archivo:
            json.dump(puntajes, archivo, indent=4)
        
    def ver_puntajes(self, evento=None):
        gestor = GestorJugadores()
        gestor.lee_json()
        gestor.ordena_lista() 
        jugadores = gestor.obtener_lista()
        
        if jugadores is False:
            messagebox.showinfo("Puntajes", "No hay puntajes registrados aun")
            return     
        self.__ventana_puntajes = tk.Toplevel(self.__ventana)
        self.__ventana_puntajes.title("Puntajes")
        self.__ventana_puntajes.geometry("1000x500")
        centrar_ventana(self.__ventana_puntajes)
        ttk.Label(self.__ventana_puntajes, text='   Galeria de Puntajes').pack(side="top", fill="x")
        marco = ttk.Frame(self.__ventana_puntajes)
        marco.pack(expand=True, fill='both')
        columnas = ("Nombre", "Fecha", "Hora", "Puntaje")
        tree = ttk.Treeview(marco, columns=columnas, show="headings")
        barra_desplazamiento = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand = barra_desplazamiento.set)  
        barra_desplazamiento.pack(side='right', fill='y')
        tree.pack(side='left', expand=True, fill='both')
        
        for columna in columnas:
            tree.heading(columna, text=columna, anchor="center")
            tree.column(columna, anchor="center", width=200 if columna == "Nombre" else 150)
        
        for jugador in jugadores:
            tree.insert("", "end", values=jugador.obtener_datos())
        
        self.__ventana_puntajes.mainloop()

    def salir(self):
        self.__ventana.quit()

    def ejecutar(self):
        self.__ventana_nombre.mainloop()   

if __name__ == '__main__':
    simon_game = Aplicacion()
    simon_game.ejecutar()
