from db import SessionLocal
from repo import create_faq
from schemas import FAQCreate

seed = [
    ("¿Cómo restablezco mi contraseña?", "Ve a Perfil → Seguridad → Restablecer y sigue el correo de verificación.", "cuentas,seguridad"),
    ("¿Cuál es el horario de soporte?", "Lunes a viernes 8:00–18:00 (GMT-6). Incidencias críticas 24/7 por correo.", "soporte,horarios"),
    ("¿Dónde veo mis facturas?", "Configuración → Facturación: descarga de facturas y método de pago.", "facturacion,pagos"),
    ("¿Qué planes tienen y precios?", "Básico $9, Pro $19, Empresa a medida. Prueba gratis 7 días.", "planes,precios"),
    ("¿Cómo contacto con ventas?", "Escríbenos a ventas@ejemplo.com o usa /contacto.", "ventas,contacto"),
]

if __name__ == "__main__":
    db = SessionLocal()
    for q,a,t in seed:
        create_faq(db, FAQCreate(question=q, answer=a, tags=t))
    db.close()
    print("Seed listo.")
