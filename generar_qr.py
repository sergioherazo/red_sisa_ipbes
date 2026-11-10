"""Genera el código QR de la página.

Uso:   python generar_qr.py https://TU-USUARIO.github.io/red-sisa-ipbes/
Salida: qr_red_sisa.png (alta resolución, listo para la lona)
Requiere:  pip install "qrcode[pil]"
"""
import sys
import qrcode
from qrcode.constants import ERROR_CORRECT_Q

if len(sys.argv) < 2 or not sys.argv[1].startswith('http'):
    raise SystemExit('Uso: python generar_qr.py https://TU-USUARIO.github.io/red-sisa-ipbes/')
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=24, border=4)
qr.add_data(sys.argv[1])
qr.make(fit=True)
qr.make_image(fill_color='#3f5a39', back_color='white').save('qr_red_sisa.png')
print('Listo: qr_red_sisa.png')
