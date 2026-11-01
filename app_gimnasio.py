import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc

# Configuración visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Configuración de conexión a la base de datos en Docker
DB_CONFIG = {
    'server': 'localhost,1433',
    'database': 'GimnasioDB',
    'username': 'sa',
    'password': 'PasswordSeguro123!',
    'driver': '{ODBC Driver 18 for SQL Server}'
}

def obtener_conexion():
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a Docker:\n{e}")
        return None

class GimnasioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Administración - GimnasioDB")
        self.geometry("950;620".replace(";", "x"))
        self.resizable(False, False)

        self.planes_map = {}  # Relación: "Nombre Plan" -> IdPlan

        self.crear_layout()
        self.cargar_planes()
        self.listar_socios()

    def crear_layout(self):
        # Panel izquierdo: Formulario de Registro
        self.frame_form = ctk.CTkFrame(self, width=320, corner_radius=10)
        self.frame_form.pack(side="left", fill="y", padx=15, pady=15)

        titulo_form = ctk.CTkLabel(self.frame_form, text="Registrar Nuevo Socio", font=("Arial", 18, "bold"))
        titulo_form.pack(pady=(15, 10))

        # Inputs
        self.txt_dni = ctk.CTkEntry(self.frame_form, placeholder_text="DNI (8 dígitos)")
        self.txt_dni.pack(fill="x", padx=15, pady=8)

        self.txt_nombre = ctk.CTkEntry(self.frame_form, placeholder_text="Nombres")
        self.txt_nombre.pack(fill="x", padx=15, pady=8)

        self.txt_apellido = ctk.CTkEntry(self.frame_form, placeholder_text="Apellidos")
        self.txt_apellido.pack(fill="x", padx=15, pady=8)

        # Selector de Planes
        lbl_plan = ctk.CTkLabel(self.frame_form, text="Seleccionar Plan:", anchor="w")
        lbl_plan.pack(fill="x", padx=15, pady=(5, 2))
        self.combo_planes = ctk.CTkComboBox(self.frame_form, values=["Cargando..."])
        self.combo_planes.pack(fill="x", padx=15, pady=8)

        # Botón Guardar
        btn_guardar = ctk.CTkButton(self.frame_form, text="Guardar en Base de Datos", fg_color="#28a745", hover_color="#218838", command=self.guardar_socio)
        btn_guardar.pack(fill="x", padx=15, pady=(15, 8))

        # Botón Limpiar
        btn_limpiar = ctk.CTkButton(self.frame_form, text="Limpiar Formulario", fg_color="#6c757d", hover_color="#5a6268", command=self.limpiar_formulario)
        btn_limpiar.pack(fill="x", padx=15, pady=5)

        # Panel derecho: Visualización y Acciones
        self.frame_tabla = ctk.CTkFrame(self, corner_radius=10)
        self.frame_tabla.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        titulo_tabla = ctk.CTkLabel(self.frame_tabla, text="Panel de Socios Activos / Inactivos", font=("Arial", 18, "bold"))
        titulo_tabla.pack(pady=(15, 10))

        # Tabla estilo Treeview
        columns = ("id", "dni", "socio", "plan", "precio", "estado")
        self.tree = ttk.Treeview(self.frame_tabla, columns=columns, show="headings", height=18)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("socio", text="Socio")
        self.tree.heading("plan", text="Plan")
        self.tree.heading("precio", text="Precio (S/.)")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("dni", width=90, anchor="center")
        self.tree.column("socio", width=180)
        self.tree.column("plan", width=120)
        self.tree.column("precio", width=80, anchor="center")
        self.tree.column("estado", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        # Acciones inferiores
        frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=15, pady=(0, 15))

        btn_refrescar = ctk.CTkButton(frame_acciones, text="Actualizar Lista", command=self.listar_socios)
        btn_refrescar.pack(side="left", padx=5)

        btn_cambiar_estado = ctk.CTkButton(frame_acciones, text="Alternar Estado (Activo/Inactivo)", fg_color="#e0a800", hover_color="#c69500", command=self.alternar_estado)
        btn_cambiar_estado.pack(side="left", padx=5)

    def cargar_planes(self):
        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT IdPlan, Nombre, Precio FROM Planes")
        filas = cursor.fetchall()
        conn.close()

        self.planes_map = {}
        opciones = []
        for id_plan, nombre, precio in filas:
            label = f"{nombre} - S/.{precio:.2f}"
            self.planes_map[label] = id_plan
            opciones.append(label)

        if opciones:
            self.combo_planes.configure(values=opciones)
            self.combo_planes.set(opciones[0])

    def listar_socios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        query = """
            SELECT 
                s.IdSocio,
                s.Dni,
                s.Nombre + ' ' + s.Apellido AS Socio,
                p.Nombre AS PlanElegido,
                p.Precio,
                s.Estado
            FROM Socios s
            INNER JOIN Planes p ON s.IdPlan = p.IdPlan
            ORDER BY s.IdSocio DESC;
        """
        cursor.execute(query)
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], f"{fila[4]:.2f}", fila[5]))
        conn.close()

    def guardar_socio(self):
        dni = self.txt_dni.get().strip()
        nombre = self.txt_nombre.get().strip()
        apellido = self.txt_apellido.get().strip()
        plan_sel = self.combo_planes.get()

        if not dni or not nombre or not apellido:
            messagebox.showwarning("Atención", "Por favor completa todos los campos.")
            return

        if len(dni) != 8 or not dni.isdigit():
            messagebox.showwarning("DNI Inválido", "El DNI debe contener exactamente 8 números.")
            return

        id_plan = self.planes_map.get(plan_sel)
        if not id_plan:
            messagebox.showwarning("Atención", "Selecciona un plan válido.")
            return

        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Socios (Dni, Nombre, Apellido, IdPlan, Estado) VALUES (?, ?, ?, ?, 'Activo')",
                (dni, nombre, apellido, id_plan)
            )
            conn.commit()
            messagebox.showinfo("Éxito", f"Socio {nombre} {apellido} registrado en la base de datos.")
            self.limpiar_formulario()
            self.listar_socios()
        except pyodbc.IntegrityError:
            messagebox.showerror("Error", f"El DNI {dni} ya se encuentra registrado.")
        except Exception as e:
            messagebox.showerror("Error SQL", f"No se pudo insertar el registro:\n{e}")
        finally:
            conn.close()

    def alternar_estado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un socio de la tabla para cambiar su estado.")
            return

        item = self.tree.item(seleccion[0])
        id_socio = item["values"][0]
        estado_actual = item["values"][5]
        nuevo_estado = "Inactivo" if estado_actual == "Activo" else "Activo"

        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("UPDATE Socios SET Estado = ? WHERE IdSocio = ?", (nuevo_estado, id_socio))
        conn.commit()
        conn.close()
        self.listar_socios()

    def limpiar_formulario(self):
        self.txt_dni.delete(0, "end")
        self.txt_nombre.delete(0, "end")
        self.txt_apellido.delete(0, "end")

if __name__ == "__main__":
    app = GimnasioApp()
    app.mainloop()