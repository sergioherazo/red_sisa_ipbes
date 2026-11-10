"""Descarga las respuestas del formulario y las deja en un Excel plano (sin formato).

Uso:
    export SUPABASE_URL="https://xxxx.supabase.co"
    export SUPABASE_SERVICE_KEY="..."        # clave secreta "service_role": NO la subas a GitHub
    python exportar_respuestas.py

Prueba sin conexión:  python exportar_respuestas.py --json respuestas.json
"""
import argparse, json, os, re, urllib.request
import pandas as pd

CATEGORIAS = {
    'naturaleza': 'Naturaleza',
    'contribuciones': 'Contribuciones de la naturaleza a las personas',
    'calidad_vida': 'Buena calidad de vida',
    'activos': 'Activos antropogénicos',
    'instituciones': 'Instituciones y gobernanza',
    'motores_antropogenicos': 'Motores de cambio directos antropogénicos',
    'motores_naturales': 'Motores de cambio directos naturales',
    'socioecologicos': 'Sistemas socioecológicos',
}

def cargar_semilleros(ruta='datos.js'):
    txt = open(ruta, encoding='utf-8').read()
    m = re.search(r'window\.SEMILLEROS\s*=\s*(\[.*?\]);\s*\n', txt, re.S)
    return {s['nombre']: s for s in json.loads(m.group(1))}

def descargar():
    url, key = os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_KEY')
    if not url or not key:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY (ver README, paso 6).')
    req = urllib.request.Request(url.rstrip('/') + '/rest/v1/respuestas?select=*&order=created_at.asc',
                                 headers={'apikey': key, 'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def nombre_cat(c):
    return CATEGORIAS.get(c, c or '')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='archivo JSON con las filas (para probar sin conexión)')
    ap.add_argument('--salida', default='respuestas_ipbes_red_sisa.xlsx')
    a = ap.parse_args()
    filas = json.load(open(a.json, encoding='utf-8')) if a.json else descargar()
    sems = cargar_semilleros()
    df = pd.DataFrame(filas)
    if df.empty:
        raise SystemExit('Todavía no hay respuestas.')
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert('America/Bogota').dt.tz_localize(None)
    df = df.sort_values('created_at')
    act = df.drop_duplicates('semillero', keep='last').copy()

    def previa(n):
        s = sems.get(n); return nombre_cat(s['previa']) if s and s.get('previa') else ''
    def coincide(r):
        s = sems.get(r['semillero'])
        if not s or not s.get('previa'): return ''
        if r['principal'] == s['previa']: return 'Sí'
        if s['previa'] in (r['secundarias'] or []) or (s.get('previaSec') and r['principal'] == s['previaSec']): return 'Parcial'
        return 'No'

    out = pd.DataFrame({
        'Semillero': act['semillero'],
        'Fuera de la lista base': act['semillero_otro'].map({True: 'Sí', False: ''}),
        'Categoría principal': act['principal'].map(nombre_cat),
        'Categorías secundarias': act['secundarias'].map(lambda l: '; '.join(nombre_cat(x) for x in (l or []))),
        'Asignación previa del equipo': act['semillero'].map(previa),
        'Coincide': act.apply(coincide, axis=1),
        'Comentario': act['motivo'].fillna(''),
        'Contacto': act['contacto_nombre'].fillna(''),
        'Correo': act['contacto_correo'].fillna(''),
        'Fecha de respuesta': act['created_at'].dt.strftime('%d/%m/%Y %H:%M'),
    }).sort_values('Semillero', key=lambda s: s.str.lower())

    pend = pd.DataFrame({'Semillero sin responder': sorted(set(sems) - set(act['semillero']), key=str.lower)})
    hist = df.assign(principal=df['principal'].map(nombre_cat),
                     secundarias=df['secundarias'].map(lambda l: '; '.join(nombre_cat(x) for x in (l or []))))
    hist['created_at'] = hist['created_at'].dt.strftime('%d/%m/%Y %H:%M')
    with pd.ExcelWriter(a.salida, engine='openpyxl') as w:
        out.to_excel(w, 'Respuestas actuales', index=False)
        pend.to_excel(w, 'Pendientes', index=False)
        hist.to_excel(w, 'Historial', index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(60, max(12, max(len(str(c.value or '')) for c in col) + 2))
    print(f'{len(act)} semilleros con respuesta, {len(pend)} pendientes, {len(df)} envíos en total -> {a.salida}')

if __name__ == '__main__':
    main()
