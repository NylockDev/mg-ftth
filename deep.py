import os
import re
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageColor
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import track
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime, timedelta
import glob
from collections import defaultdict

console = Console()

# Base de données JSON
DB_FILE = "mg_telecom_db.json"

THEMES = {
    "1": "NOIR & OR",
    "2": "BLEU NUIT",
    "3": "CYBERPUNK",
    "4": "BORDEAUX",
    "5": "VERT EMERAUDE",
    "6": "GRIS PRO",
    "7": "ORANGE ENERGIE",
    "8": "BLEU MTN",
    "9": "ROUGE PRESTIGE",
    "10": "VIOLET ROYAL",
    "11": "SABLE",
    "12": "CARBONE",
    "13": "CIAN TECH",
    "14": "IVOIRE GOLD",
    "15": "BLEU GLACIER",
    "16": "VERT OLIVE",
    "17": "ROSE GOLD",
    "18": "BLEU PÉTROLE",
    "19": "VERT MILITAIRE",
    "20": "JAUNE SAHARA",
    "21": "BLEU LAGON",
    "22": "GRIS ANTHRACITE",
    "23": "TURQUOISE SOFT",
    "24": "BRUN CAFÉ",
    "25": "BLEU ACIER",
    "26": "MENTHE FRAÎCHE",
    "27": "BLEU NÉON",
    "28": "NOIR MAT",
    "29": "VERT LIME TECH",
    "30": "BLEU CIEL PRO",
    "31": "ROUGE NOIR",
    "32": "OR IMPÉRIAL",
    "33": "BLEU COBALT",
    "34": "GRAPHITE",
    "35": "BLEU INDIGO",
    "36": "VERT FOREST",
    "37": "ORANGE OFFICIEL",
    "38": "MTN OFFICIEL",
    "39": "MOOV OFFICIEL"
}

# ==================== GESTION DE LA BASE DE DONNÉES ====================

def load_database():
    """Charge la base de données depuis le fichier JSON"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "dossiers": [],
                "equipes": {},
                "statistiques": {
                    "total_dossiers": 0,
                    "total_clients": 0,
                    "total_equipes": 0
                }
            }
    return {
        "dossiers": [],
        "equipes": {},
        "statistiques": {
            "total_dossiers": 0,
            "total_clients": 0,
            "total_equipes": 0
        }
    }

def save_database(db):
    """Sauvegarde la base de données dans le fichier JSON"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def add_dossier_to_db(date_rdv, base_dir, equipes_data):
    """Ajoute un nouveau dossier à la base de données"""
    db = load_database()
    
    # Vérifier si le dossier existe déjà
    existing = next((d for d in db["dossiers"] if d["date"] == date_rdv), None)
    if existing:
        # Mettre à jour le dossier existant
        existing["base_dir"] = base_dir
        existing["equipes"] = equipes_data
    else:
        # Ajouter un nouveau dossier
        db["dossiers"].append({
            "date": date_rdv,
            "base_dir": base_dir,
            "equipes": equipes_data,
            "created_at": datetime.now().isoformat()
        })
    
    # Mettre à jour les statistiques des équipes
    for equipe, dossiers in equipes_data.items():
        if equipe not in db["equipes"]:
            db["equipes"][equipe] = {
                "total_clients": 0,
                "dossiers_participes": []
            }
        db["equipes"][equipe]["total_clients"] += len(dossiers)
        if date_rdv not in db["equipes"][equipe]["dossiers_participes"]:
            db["equipes"][equipe]["dossiers_participes"].append(date_rdv)
    
    # Mettre à jour les statistiques globales
    db["statistiques"]["total_dossiers"] = len(db["dossiers"])
    db["statistiques"]["total_clients"] = sum(
        len(d["equipes"][e]) for d in db["dossiers"] for e in d["equipes"]
    )
    db["statistiques"]["total_equipes"] = len(db["equipes"])
    
    save_database(db)
    return db

# ==================== FONCTIONS UTILITAIRES ====================

def clean_val(val, placeholder=""):
    v = str(val).strip()
    if v.lower() in ['nan', 'none', 'null', '', 'nat']:
        return placeholder
    if v.endswith('.0'):
        v = v[:-2]
    return v

def format_tel(val):
    v = clean_val(val)
    if not v:
        return ""
    v = re.sub(r'\D', '', v)
    return "0" + v if len(v) == 9 else v

def get_termux_font(bold=True):
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(prefix, "share/fonts/TTF", font_name)
    return path if os.path.exists(path) else None

def generate_qr_https(url, filename, base_dir):
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"{base_dir}/{filename}_QR.png")

def draw_vertical_gradient(draw, width, height, top_color, bottom_color):
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def export_pdf(date_rdv, base_dir):
    pdf_path = f"{base_dir}/Fiches_Installation_{date_rdv}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    W, H = A4
    images = sorted([os.path.join(base_dir, f) for f in os.listdir(base_dir) 
                    if f.lower().endswith(".png") and not f.endswith("_QR.png")])
    card_width = W - 4 * cm
    card_height = (H - 8 * cm) / 2
    
    for i in range(0, len(images), 2):
        if os.path.exists("logo.png"):
            c.drawImage("logo.png", 2*cm, H-3*cm, width=3*cm, height=3*cm, mask='auto')
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(W / 2, H - 2.2*cm, f"FICHES D'INSTALLATION DU {date_rdv}")
        
        c.drawImage(images[i], 2*cm, H/2 + 0.5*cm, width=card_width, height=card_height, 
                   preserveAspectRatio=True, mask='auto')
        if i + 1 < len(images):
            c.drawImage(images[i + 1], 2*cm, 2*cm, width=card_width, height=card_height,
                       preserveAspectRatio=True, mask='auto')
        c.showPage()
    
    c.save()
    console.print(f"[green]✅ PDF généré : {pdf_path}[/green]")

# ==================== GÉNÉRATION DES PAGES CLIENT ====================

def generate_client_page(row, team, filename, date_rdv, site_dir):
    os.makedirs(site_dir, exist_ok=True)
    quart_col = [col for col in row.index if "Quartier" in col]
    quartier = clean_val(row.get(quart_col[0], "")) if quart_col else ""
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fiche Client FTTH - {clean_val(row.get("Nom et Prénoms du Client"))}</title>
    <style>
        :root {{
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #64748b;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1e293b 100%);
            color: var(--light);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            position: relative;
        }}
        
        .back-btn {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: var(--primary);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            z-index: 1000;
            transition: all 0.3s;
        }}
        
        .back-btn:hover {{
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
            border-radius: 24px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 32px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: var(--gray);
            font-size: 16px;
        }}
        
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 32px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
            transition: transform 0.3s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}
        
        .info-item {{
            background: rgba(30, 41, 59, 0.5);
            padding: 20px;
            border-radius: 16px;
            border-left: 4px solid var(--primary);
        }}
        
        .info-label {{
            font-size: 12px;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .info-value {{
            font-size: 18px;
            color: var(--light);
            font-weight: 500;
        }}
        
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 4px;
        }}
        
        .badge-primary {{
            background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
            color: white;
        }}
        
        .badge-success {{
            background: linear-gradient(135deg, var(--secondary) 0%, #059669 100%);
            color: white;
        }}
        
        .badge-warning {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }}
        
        .qr-section {{
            text-align: center;
            padding: 30px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 20px;
            margin-top: 30px;
        }}
        
        .qr-section img {{
            max-width: 200px;
            margin: 0 auto 20px;
            display: block;
            border-radius: 12px;
            padding: 10px;
            background: white;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: var(--gray);
            font-size: 14px;
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .back-btn {{
                position: static;
                margin-bottom: 20px;
                display: inline-block;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../../dashboard_{team}.html" class="back-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Dashboard {team}
        </a>
        
        <div class="header">
            <h1>📡 FICHE CLIENT FTTH</h1>
            <div class="subtitle">Dossier du {date_rdv} • Équipe {team}</div>
        </div>
        
        <div class="card">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Nom du client</div>
                    <div class="info-value">{clean_val(row.get("Nom et Prénoms du Client"))}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Contacts téléphoniques</div>
                    <div class="info-value">{format_tel(row.get("Contact du Client"))} / {format_tel(row.get("Second contact du Client"))}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Localisation</div>
                    <div class="info-value">{clean_val(row.get("Ville/Commune d'habitation du Client"))} – {quartier}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Provenance</div>
                    <div class="info-value">{clean_val(row.get("Provenance", "DIRECT"))}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Numéro de ticket</div>
                    <div class="info-value">{clean_val(row.get("Numéro Ticket", "NON FOURNI"))}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Offre souscrite</div>
                    <div class="info-value">
                        <span class="badge badge-success">{clean_val(row.get("Forfaits FTTH"))}</span>
                    </div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Numéro TN (Identifiant)</div>
                    <div class="info-value">{clean_val(row.get("Numéro FTTH (TN)", "À GÉNÉRER"))}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Équipe technique</div>
                    <div class="info-value">
                        <span class="badge badge-primary">{team}</span>
                    </div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Date de transmission</div>
                    <div class="info-value">{clean_val(row.get("Date de Transmission"))}</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <span class="badge badge-warning">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                    EN COURS D'INSTALLATION
                </span>
            </div>
        </div>
        
        <div class="qr-section">
            <h3 style="margin-bottom: 20px; color: var(--light);">QR Code d'accès</h3>
            <img src="../{filename}_QR.png" alt="QR Code">
            <p style="color: var(--gray); margin-top: 10px;">Scannez pour accéder à cette fiche</p>
        </div>
        
        <div class="footer">
            MG TELECOM • Système de gestion FTTH<br>
            Généré automatiquement le {datetime.now().strftime("%d/%m/%Y à %H:%M")}
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{site_dir}/client_{filename}.html", "w", encoding="utf-8") as f:
        f.write(html)

# ==================== GÉNÉRATION DES DASHBOARDS ====================
def generate_dashboard_equipe(team, db):
    """Génère le dashboard d'une équipe avec TOUS les dossiers de la DB"""
    # Récupérer TOUS les dossiers de l'équipe depuis la DB complète
    team_dossiers = []
    
    for dossier in db["dossiers"]:
        if team in dossier.get("equipes", {}):
            # Convertir les données brutes en format utilisable
            dossiers_list = []
            for row_data, filename in dossier["equipes"][team]:
                try:
                    # Si c'est déjà un dict, le convertir en Series
                    if isinstance(row_data, dict):
                        row = pd.Series(row_data)
                    else:
                        row = row_data
                    dossiers_list.append((row, filename))
                except Exception as e:
                    # En cas d'erreur, créer une ligne vide
                    console.print(f"[yellow]⚠️  Erreur avec {filename}: {e}[/yellow]")
                    row = pd.Series({"Nom et Prénoms du Client": "DONNÉES CORROMPUES"})
                    dossiers_list.append((row, filename))
            
            if dossiers_list:
                team_dossiers.append((dossier["date"], dossiers_list))
    
    total_installations = sum(len(dossiers) for _, dossiers in team_dossiers)
    
    # Récupérer les stats de l'équipe
    team_stats = db["equipes"].get(team, {})
    total_clients = team_stats.get("total_clients", 0)
    
    # Construction du HTML avec CSS COMPLET
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Équipe {team} - MG TELECOM</title>
    <style>
        :root {{
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #64748b;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1e293b 100%);
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Navigation */
        .nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--border);
        }}
        
        .nav-brand {{
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .nav-links {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        
        .nav-btn {{
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .nav-btn-primary {{
            background: var(--primary);
            color: white;
        }}
        
        .nav-btn-secondary {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--light);
        }}
        
        .nav-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }}
        
        /* Header */
        .header {{
            text-align: center;
            padding: 40px;
            margin-bottom: 40px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
            border-radius: 24px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header .subtitle {{
            color: var(--gray);
            font-size: 18px;
        }}
        
        /* Stats */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid var(--border);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
        }}
        
        .stat-icon {{
            font-size: 40px;
            margin-bottom: 15px;
        }}
        
        .stat-number {{
            font-size: 42px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: var(--gray);
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Dossiers */
        .dossiers-grid {{
            display: grid;
            gap: 25px;
        }}
        
        .dossier-section {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border);
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 600;
            color: var(--light);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-count {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        /* Clients Grid */
        .clients-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .client-card {{
            background: rgba(30, 41, 59, 0.5);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid transparent;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .client-card:hover {{
            border-color: var(--primary);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .client-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }}
        
        .client-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--light);
            margin-bottom: 5px;
        }}
        
        .client-badge {{
            background: linear-gradient(135deg, var(--secondary) 0%, #059669 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .client-info {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            margin: 8px 0;
        }}
        
        .info-label {{
            color: var(--gray);
            font-size: 13px;
            min-width: 120px;
            font-weight: 500;
        }}
        
        .info-value {{
            color: var(--light);
            font-size: 14px;
            flex: 1;
        }}
        
        .client-actions {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        
        .action-btn {{
            flex: 1;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .action-btn-primary {{
            background: var(--primary);
            color: white;
        }}
        
        .action-btn-secondary {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--light);
        }}
        
        .action-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }}
        
        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--gray);
        }}
        
        .empty-icon {{
            font-size: 60px;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .nav {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .nav-links {{
                flex-wrap: wrap;
                justify-content: center;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 28px;
            }}
            
            .clients-grid {{
                grid-template-columns: 1fr;
            }}
            
            .client-card {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div class="nav-brand">MG TELECOM FTTH</div>
            <div class="nav-links">
                <a href="dashboard_admin.html" class="nav-btn nav-btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
                        <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                    </svg>
                    Dashboard Admin
                </a>
                <a href="calendar.html" class="nav-btn nav-btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
                        <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    Calendrier
                </a>
            </div>
        </nav>
        
        <div class="header">
            <h1>👷 Dashboard Équipe {team}</h1>
            <div class="subtitle">Gestion centralisée des installations FTTH</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-number">{total_installations}</div>
                <div class="stat-label">Total Installations</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📅</div>
                <div class="stat-number">{len(team_dossiers)}</div>
                <div class="stat-label">Jours d'activité</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🚀</div>
                <div class="stat-number">{team}</div>
                <div class="stat-label">Équipe</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-number">{total_clients}</div>
                <div class="stat-label">Clients au total</div>
            </div>
        </div>
"""
    
    # Ajouter les dossiers par date
    if team_dossiers:
        for date_rdv, dossiers in sorted(team_dossiers, reverse=True):
            base_dir = f"dossier_{date_rdv}"
            html += f"""
        <div class="dossier-section">
            <div class="section-header">
                <div class="section-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    {date_rdv}
                </div>
                <div class="section-count">{len(dossiers)} installation(s)</div>
            </div>
            
            <div class="clients-grid">"""
            
            for row, filename in dossiers:
                # Utiliser clean_val avec gestion d'erreurs
                try:
                    nom = clean_val(row.get('Nom et Prénoms du Client', 'INCONNU'))
                    ville = clean_val(row.get("Ville/Commune d'habitation du Client", ""))
                    quart_col = [col for col in row.index if "Quartier" in col] if hasattr(row, 'index') else []
                    quartier = clean_val(row.get(quart_col[0], "")) if quart_col else ""
                    offre = clean_val(row.get('Forfaits FTTH', 'FIBRE'))
                    tel1 = format_tel(row.get('Contact du Client'))
                    tn = clean_val(row.get('Numéro FTTH (TN)', 'À GÉNÉRER'))
                except:
                    nom = "ERREUR DONNÉES"
                    ville = ""
                    quartier = ""
                    offre = "FIBRE"
                    tel1 = ""
                    tn = ""
                
                html += f"""
                <div class="client-card" onclick="window.location.href='{base_dir}/site/client_{filename}.html'">
                    <div class="client-header">
                        <div>
                            <div class="client-name">{nom}</div>
                            <div style="color: var(--gray); font-size: 14px;">{ville} - {quartier}</div>
                        </div>
                        <div class="client-badge">{offre}</div>
                    </div>
                    
                    <div class="client-info">
                        <div class="info-row">
                            <div class="info-label">📞 Contact:</div>
                            <div class="info-value">{tel1}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🔢 TN:</div>
                            <div class="info-value">{tn}</div>
                        </div>
                    </div>
                    
                    <div class="client-actions">
                        <a href="{base_dir}/site/client_{filename}.html" class="action-btn action-btn-primary">Voir Fiche</a>
                        <a href="{base_dir}/Fiche_{filename}.png" class="action-btn action-btn-secondary" download>Télécharger</a>
                    </div>
                </div>"""
            
            html += """
            </div>
        </div>"""
    else:
        html += """
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <h3 style="color: var(--light); margin-bottom: 10px;">Aucun dossier trouvé</h3>
            <p style="color: var(--gray);">Cette équipe n'a pas encore de dossiers d'installation.</p>
        </div>"""
    
    html += """
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.client-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>"""
    
    # Écrire le fichier
    with open(f"dashboard_{team}.html", "w", encoding="utf-8") as f:
        f.write(html)

def generate_dashboard_admin(db):    
    """génère le dashboard admin avec données de la db"""
    html = """<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dashboard admin - mg telecom ftth</title>
    <style>
        :root {
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --accent: #8b5cf6;
            --dark: #0f172a;
            --darker: #020617;
            --light: #f8fafc;
            --gray: #64748b;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border: rgba(255, 255, 255, 0.1);
            --sidebar-width: 280px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'inter', system-ui, -apple-system, sans-serif;
            background: var(--darker);
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
            display: flex;
        }
        
        /* sidebar */
        .sidebar {
            width: var(--sidebar-width);
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(2, 6, 23, 0.95) 100%);
            border-right: 1px solid var(--border);
            padding: 30px 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
        }
        
        .sidebar-brand {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 40px;
            padding-left: 10px;
        }
        
        .sidebar-nav {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .nav-item {
            padding: 15px 20px;
            border-radius: 12px;
            text-decoration: none;
            color: var(--gray);
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .nav-item:hover, .nav-item.active {
            background: rgba(59, 130, 246, 0.1);
            color: var(--light);
            border-left: 4px solid var(--primary);
        }
        
        .nav-item svg {
            width: 20px;
            height: 20px;
        }
        
        .sidebar-section {
            margin: 30px 0;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }
        
        .section-title {
            color: var(--gray);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            padding-left: 20px;
        }
        
        /* main content */
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 30px;
            max-width: calc(100vw - var(--sidebar-width));
        }
        
        /* top bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding: 20px;
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }
        
        .top-bar h1 {
            font-size: 28px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .top-bar-actions {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .search-box {
            position: relative;
        }
        
        .search-box input {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 20px 12px 45px;
            color: var(--light);
            font-size: 14px;
            width: 300px;
            transition: all 0.3s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .search-box svg {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translatey(-50%);
            color: var(--gray);
            width: 20px;
            height: 20px;
        }
        
        /* stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translatey(-5px);
            border-color: var(--primary);
            box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
        }
        
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .stat-icon {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .stat-number {
            font-size: 42px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label {
            color: var(--gray);
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }
        
        /* dossiers grid */
        .dossiers-grid {
            display: grid;
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .dossier-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }
        
        .dossier-card:hover {
            border-color: var(--primary);
            transform: translatey(-5px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }
        
        .dossier-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border);
        }
        
        .dossier-date {
            font-size: 22px;
            font-weight: 600;
            color: var(--light);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .dossier-count {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        
        /* équipes grid */
        .equipes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .equipe-card {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid transparent;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .equipe-card:hover {
            border-color: var(--primary);
            transform: translatey(-5px);
            background: rgba(59, 130, 246, 0.1);
        }
        
        .equipe-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .equipe-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 20px;
            color: white;
        }
        
        .equipe-name {
            font-size: 18px;
            font-weight: 600;
            color: var(--light);
        }
        
        .equipe-stats {
            color: var(--gray);
            font-size: 14px;
            margin-bottom: 20px;
        }
        
        .equipe-actions {
            display: flex;
            gap: 10px;
        }
        
        .equipe-btn {
            flex: 1;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.3s;
        }
        
        .equipe-btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .equipe-btn-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--light);
        }
        
        .equipe-btn:hover {
            transform: translatey(-2px);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }
        
        /* quick actions */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        
        .action-btn {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            text-decoration: none;
            color: var(--light);
            transition: all 0.3s;
        }
        
        .action-btn:hover {
            background: rgba(59, 130, 246, 0.2);
            border-color: var(--primary);
            transform: translatey(-3px);
        }
        
        /* responsive */
        @media (max-width: 1024px) {
            .sidebar {
                width: 250px;
            }
            
            .main-content {
                margin-left: 250px;
            }
        }
        
        @media (max-width: 768px) {
            body {
                flex-direction: column;
            }
            
            .sidebar {
                position: static;
                width: 100%;
                height: auto;
            }
            
            .main-content {
                margin-left: 0;
                max-width: 100%;
                padding: 20px;
            }
            
            .top-bar {
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }
            
            .search-box input {
                width: 100%;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .equipes-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* animations */
        @keyframes fadein {
            from { opacity: 0; transform: translatey(20px); }
            to { opacity: 1; transform: translatey(0); }
        }
        
        .fade-in {
            animation: fadein 0.5s ease forwards;
        }
    </style>
</head>
<body>
    <!-- sidebar -->
    <aside class="sidebar">
        <div class="sidebar-brand">mg telecom</div>
        
        <nav class="sidebar-nav">
            <a href="#" class="nav-item active">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m3 12l2-2m0 0l7-7 7 7m5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
                tableau de bord
            </a>
            <a href="calendar.html" class="nav-item">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m8 7v3m8 4v3m-9 8h10m5 21h14a2 2 0 002-2v7a2 2 0 00-2-2h5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                calendrier
            </a>
            <a href="#" class="nav-item">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m12 4.354a4 4 0 110 5.292m15 21h3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5 0c-.281.023-.562.035-.844.035a13.92 13.92 0 0112 16c-2.5 0-4.847.655-6.879 1.803m13.5 0a9 9 0 018.686 5.314m21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                équipes
            </a>
            <a href="#" class="nav-item">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                statistiques
            </a>
            <a href="#" class="nav-item">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path d="m15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                paramètres
            </a>
        </nav>
        
        <div class="sidebar-section">
            <div class="section-title">équipes actives</div>
"""
    
    # générer la liste des équipes dans la sidebar
    for equipe in sorted(db["equipes"].keys()):
        total = db["equipes"][equipe]["total_clients"]
        html += f"""
            <a href="dashboard_{equipe}.html" class="nav-item">
                <svg viewbox="0 0 24 24" fill="none" stroke="currentcolor" stroke-width="2">
                    <path d="m17 20h5v-2a3 3 0 00-5.356-1.857m17 20h7m10 0v-2c0-.656-.126-1.283-.356-1.857m7 20h2v-2a3 3 0 015.356-1.857m7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0m15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zm7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                {equipe} <span style="margin-left: auto; color: var(--primary);">{total}</span>
            </a>
"""
    
    html += """
        </div>
        
        <div class="sidebar-section">
            <div class="section-title">Dernières Actions</div>
            <div style="color: var(--gray); font-size: 13px; padding: 0 20px;">
                <div style="margin-bottom: 10px;">✅ Dernière mise à jour : <br><span style="color: var(--light);">"""
    
    if db["dossiers"]:
        last_dossier = sorted(db["dossiers"], key=lambda x: x.get("created_at", ""), reverse=True)[0]
        html += f"""Dossier du {last_dossier["date"]}</span></div>"""
    
    html += """
                <div>📊 Base de données : <br><span style="color: var(--light);">"""
    html += f"""{db["statistiques"]["total_clients"]} clients</span></div>
            </div>
        </div>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
        <!-- Top Bar -->
        <div class="top-bar">
            <h1>🎛️ Dashboard Administrateur</h1>
            <div class="top-bar-actions">
                <div class="search-box">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                    <input type="text" id="searchInput" placeholder="Rechercher un dossier, une équipe...">
                </div>
                <a href="#" class="action-btn" style="padding: 12px 24px;">+ Nouveau Dossier</a>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card fade-in">
                <div class="stat-header">
                    <div class="stat-icon">📊</div>
                    <div class="stat-number">""" + str(db["statistiques"]["total_dossiers"]) + """</div>
                </div>
                <div class="stat-label">Dossiers Actifs</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.1s;">
                <div class="stat-header">
                    <div class="stat-icon">📡</div>
                    <div class="stat-number">""" + str(db["statistiques"]["total_clients"]) + """</div>
                </div>
                <div class="stat-label">Installations</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.2s;">
                <div class="stat-header">
                    <div class="stat-icon">👥</div>
                    <div class="stat-number">""" + str(db["statistiques"]["total_equipes"]) + """</div>
                </div>
                <div class="stat-label">Équipes Actives</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.3s;">
                <div class="stat-header">
                    <div class="stat-icon">📈</div>
                    <div class="stat-number">""" + str(len([d for d in db["dossiers"] if datetime.now().strftime("%d-%m-%Y") == d["date"]])) + """</div>
                </div>
                <div class="stat-label">Dossiers Aujourd'hui</div>
            </div>
        </div>
        
        <!-- Dossiers -->
        <h2 style="color: var(--light); margin: 40px 0 20px 0; font-size: 24px;">📂 Dossiers par Date</h2>
        <div class="dossiers-grid" id="dossiersContainer">
"""
    
    # Grouper les dossiers par date
    dossiers_by_date = {}
    for dossier in db["dossiers"]:
        date_rdv = dossier["date"]
        if date_rdv not in dossiers_by_date:
            dossiers_by_date[date_rdv] = []
        dossiers_by_date[date_rdv].append(dossier)
    
    for date_rdv in sorted(dossiers_by_date.keys(), reverse=True):
        dossiers = dossiers_by_date[date_rdv]
        total_installs = sum(len(dossier["equipes"].get(e, [])) for dossier in dossiers for e in dossier["equipes"])
        
        html += f"""
            <div class="dossier-card fade-in" data-date="{date_rdv}">
                <div class="dossier-header">
                    <div class="dossier-date">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                        {date_rdv}
                    </div>
                    <div class="dossier-count">{total_installs} installation(s)</div>
                </div>
                
                <div class="equipes-grid">
"""
        
        # Collecter toutes les équipes pour cette date
        equipes_set = set()
        for dossier in dossiers:
            equipes_set.update(dossier["equipes"].keys())
        
        for equipe in sorted(equipes_set):
            equipe_total = sum(len(dossier["equipes"].get(equipe, [])) for dossier in dossiers)
            html += f"""
                    <div class="equipe-card" onclick="window.location.href='dashboard_{equipe}.html'">
                        <div class="equipe-header">
                            <div class="equipe-avatar">{equipe[0]}</div>
                            <div>
                                <div class="equipe-name">{equipe}</div>
                                <div class="equipe-stats">{equipe_total} installation(s)</div>
                            </div>
                        </div>
                        <div class="equipe-actions">
                            <a href="dashboard_{equipe}.html" class="equipe-btn equipe-btn-primary">Voir Dashboard</a>
                            <a href="calendar.html?date={date_rdv}" class="equipe-btn equipe-btn-secondary">Voir Détails</a>
                        </div>
                    </div>
"""
        
        html += """
                </div>
                
                <div class="quick-actions">
                    <a href="#" class="action-btn">📥 Exporter PDF</a>
                    <a href="#" class="action-btn">📊 Voir Statistiques</a>
                    <a href="#" class="action-btn">📋 Liste Complète</a>
                </div>
            </div>
"""
    
    html += """
        </div>
    </main>
    
    <script>
        // Recherche
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const dossierCards = document.querySelectorAll('.dossier-card');
            
            dossierCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                card.style.display = isVisible ? 'block' : 'none';
                card.style.opacity = isVisible ? '1' : '0';
                card.style.transform = isVisible ? 'translateY(0)' : 'translateY(20px)';
            });
        });
        
        // Animation au chargement
        document.addEventListener('DOMContentLoaded', function() {
            const fadeElements = document.querySelectorAll('.fade-in');
            fadeElements.forEach((el, index) => {
                el.style.animationDelay = (index * 0.1) + 's';
            });
            
            // Mettre à jour l'heure en temps réel
            function updateTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString('fr-FR', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                });
                const dateString = now.toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                const timeElement = document.querySelector('.top-bar h1');
                if (timeElement) {
                    timeElement.innerHTML = `🎛️ Dashboard Administrateur <small style="font-size: 14px; color: var(--gray); display: block; margin-top: 5px;">${dateString} • ${timeString}</small>`;
                }
            }
            
            updateTime();
            setInterval(updateTime, 1000);
        });
        
        // Filtre par date
        function filterByDate(date) {
            const dossierCards = document.querySelectorAll('.dossier-card');
            dossierCards.forEach(card => {
                const cardDate = card.getAttribute('data-date');
                if (date === 'all' || cardDate === date) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 10);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        }
    </script>
</body>
</html>"""
    
    with open("dashboard_admin.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    console.print("[green]✅ Dashboard Admin généré[/green]")

def generate_calendar(db):
    """Génère un calendrier interactif pour naviguer dans les dossiers"""
    # Collecter toutes les dates avec des dossiers
    dates_with_dossiers = {}
    for dossier in db["dossiers"]:
        date_rdv = dossier["date"]
        try:
            date_obj = datetime.strptime(date_rdv, "%d-%m-%Y")
            dates_with_dossiers[date_obj] = dossier
        except:
            continue
    
    # Générer le calendrier
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendrier - MG TELECOM FTTH</title>
    <style>
        :root {{
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #64748b;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1e293b 100%);
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Navigation */
        .nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 30px;
        }}
        
        .nav-brand {{
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .nav-links {{
            display: flex;
            gap: 15px;
        }}
        
        .nav-btn {{
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            color: var(--light);
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--border);
            transition: all 0.3s;
        }}
        
        .nav-btn:hover {{
            background: rgba(59, 130, 246, 0.2);
            transform: translateY(-2px);
        }}
        
        /* Calendar Header */
        .calendar-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px;
            background: var(--card-bg);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }}
        
        .month-navigation {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .nav-arrow {{
            width: 40px;
            height: 40px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--border);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .nav-arrow:hover {{
            background: rgba(59, 130, 246, 0.2);
            transform: scale(1.1);
        }}
        
        .current-month {{
            font-size: 28px;
            font-weight: 700;
            color: var(--light);
            min-width: 250px;
            text-align: center;
        }}
        
        .calendar-actions {{
            display: flex;
            gap: 15px;
        }}
        
        .action-btn {{
            padding: 12px 24px;
            border-radius: 10px;
            background: var(--primary);
            color: white;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .action-btn:hover {{
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }}
        
        /* Calendar Grid */
        .calendar-grid {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .calendar-day-header {{
            text-align: center;
            padding: 15px;
            color: var(--gray);
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
        }}
        
        .calendar-day {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 15px;
            min-height: 120px;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }}
        
        .calendar-day.empty {{
            background: transparent;
            border: 1px dashed var(--border);
            opacity: 0.5;
        }}
        
        .calendar-day.has-dossiers {{
            border-color: var(--primary);
            background: rgba(59, 130, 246, 0.05);
            cursor: pointer;
        }}
        
        .calendar-day.has-dossiers:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
            background: rgba(59, 130, 246, 0.1);
        }}
        
        .day-number {{
            font-size: 24px;
            font-weight: 700;
            color: var(--light);
            margin-bottom: 10px;
        }}
        
        .has-dossiers .day-number {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .dossier-count {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: var(--primary);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
        }}
        
        .dossier-list {{
            margin-top: 10px;
        }}
        
        .dossier-item {{
            background: rgba(30, 41, 59, 0.5);
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 5px;
            font-size: 12px;
            color: var(--light);
            border-left: 3px solid var(--primary);
        }}
        
        /* Dossiers List */
        .dossiers-section {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
            margin-top: 40px;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: var(--light);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .selected-date {{
            color: var(--primary);
            font-weight: 600;
        }}
        
        .dossiers-list {{
            display: grid;
            gap: 20px;
        }}
        
        .dossier-card {{
            background: rgba(30, 41, 59, 0.5);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }}
        
        .dossier-card:hover {{
            border-color: var(--primary);
            transform: translateY(-3px);
        }}
        
        .dossier-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }}
        
        .dossier-team {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .dossier-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .dossier-info {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .info-label {{
            font-size: 12px;
            color: var(--gray);
        }}
        
        .info-value {{
            font-size: 14px;
            color: var(--light);
            font-weight: 500;
        }}
        
        /* Responsive */
        @media (max-width: 1024px) {{
            .calendar-grid {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .calendar-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
            
            .calendar-header {{
                flex-direction: column;
                gap: 20px;
            }}
            
            .nav {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
        }}
        
        @media (max-width: 480px) {{
            .calendar-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease forwards;
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div class="nav-brand">📅 Calendrier FTTH</div>
            <div class="nav-links">
                <a href="dashboard_admin.html" class="nav-btn">Dashboard Admin</a>
                <a href="#" class="nav-btn">Aujourd'hui</a>
                <a href="#" class="nav-btn">Mois précédent</a>
                <a href="#" class="nav-btn">Mois suivant</a>
            </div>
        </nav>
        
        <div class="calendar-header">
            <div class="month-navigation">
                <div class="nav-arrow" onclick="changeMonth(-1)">←</div>
                <div class="current-month" id="currentMonth">""" + today.strftime("%B %Y").upper() + """</div>
                <div class="nav-arrow" onclick="changeMonth(1)">→</div>
            </div>
            <div class="calendar-actions">
                <a href="#" class="action-btn" onclick="showToday()">📅 Aujourd'hui</a>
                <a href="#" class="action-btn" onclick="exportCalendar()">📤 Exporter</a>
            </div>
        </div>
        
        <div class="calendar-grid" id="calendarGrid">
            <!-- Les jours de la semaine -->
            <div class="calendar-day-header">LUN</div>
            <div class="calendar-day-header">MAR</div>
            <div class="calendar-day-header">MER</div>
            <div class="calendar-day-header">JEU</div>
            <div class="calendar-day-header">VEN</div>
            <div class="calendar-day-header">SAM</div>
            <div class="calendar-day-header">DIM</div>
        </div>
        
        <div class="dossiers-section" id="dossiersSection">
            <div class="section-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                Dossiers du <span class="selected-date" id="selectedDate">""" + today.strftime("%d %B %Y") + """</span>
            </div>
            <div class="dossiers-list" id="dossiersList">
                <!-- Les dossiers seront chargés ici -->
            </div>
        </div>
    </div>
    
    <script>
        let currentDate = new Date();
        let currentYear = currentDate.getFullYear();
        let currentMonth = currentDate.getMonth();
        
        // Noms des mois en français
        const monthNames = [
            "JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN",
            "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DÉCEMBRE"
        ];
        
        // Données des dossiers (simulées - à remplacer par les vraies données)
        const dossiersData = {
"""
    
    # Ajouter les données des dossiers
    for date_obj, dossier in dates_with_dossiers.items():
        date_str = date_obj.strftime("%Y-%m-%d")
        dossiers_list = []
        for equipe, clients in dossier["equipes"].items():
            dossiers_list.append(f'{{"team": "{equipe}", "count": {len(clients)}, "clients": {min(len(clients), 3)}}}')
        
        html += f'            "{date_str}": [{", ".join(dossiers_list)}],\n'
    
    html += """        };
        
        function generateCalendar(year, month) {
            const calendarGrid = document.getElementById('calendarGrid');
            // Nettoyer le calendrier sauf les en-têtes
            while (calendarGrid.children.length > 7) {
                calendarGrid.removeChild(calendarGrid.lastChild);
            }
            
            // Mettre à jour le mois affiché
            document.getElementById('currentMonth').textContent = monthNames[month] + ' ' + year;
            
            // Premier jour du mois
            const firstDay = new Date(year, month, 1);
            // Dernier jour du mois
            const lastDay = new Date(year, month + 1, 0);
            // Jour de la semaine du premier jour (0 = dimanche, 1 = lundi, etc.)
            const firstDayOfWeek = firstDay.getDay();
            // Nombre de jours dans le mois
            const daysInMonth = lastDay.getDate();
            
            // Ajuster pour commencer le lundi
            let startDay = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
            
            // Ajouter les jours vides avant le premier jour
            for (let i = 0; i < startDay; i++) {
                const emptyDay = document.createElement('div');
                emptyDay.className = 'calendar-day empty';
                calendarGrid.appendChild(emptyDay);
            }
            
            // Ajouter les jours du mois
            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                const date = new Date(year, month, day);
                const dateString = date.toISOString().split('T')[0];
                
                dayElement.className = 'calendar-day fade-in';
                dayElement.style.animationDelay = (day * 0.02) + 's';
                
                // Vérifier si cette date a des dossiers
                const hasDossiers = dossiersData[dateString];
                if (hasDossiers) {
                    dayElement.classList.add('has-dossiers');
                    dayElement.onclick = () => showDossiers(date);
                    
                    const dossierCount = hasDossiers.reduce((sum, dossier) => sum + dossier.count, 0);
                    
                    const dossierCountBadge = document.createElement('div');
                    dossierCountBadge.className = 'dossier-count';
                    dossierCountBadge.textContent = dossierCount;
                    dayElement.appendChild(dossierCountBadge);
                    
                    // Afficher les premières équipes
                    const dossierList = document.createElement('div');
                    dossierList.className = 'dossier-list';
                    hasDossiers.slice(0, 2).forEach(dossier => {
                        const dossierItem = document.createElement('div');
                        dossierItem.className = 'dossier-item';
                        dossierItem.textContent = dossier.team + ' (' + dossier.count + ')';
                        dossierList.appendChild(dossierItem);
                    });
                    if (hasDossiers.length > 2) {
                        const moreItem = document.createElement('div');
                        moreItem.className = 'dossier-item';
                        moreItem.textContent = '+' + (hasDossiers.length - 2) + ' autres';
                        dossierList.appendChild(moreItem);
                    }
                    dayElement.appendChild(dossierList);
                }
                
                const dayNumber = document.createElement('div');
                dayNumber.className = 'day-number';
                dayNumber.textContent = day;
                
                // Marquer aujourd'hui
                const today = new Date();
                if (date.getDate() === today.getDate() && 
                    date.getMonth() === today.getMonth() && 
                    date.getFullYear() === today.getFullYear()) {
                    dayElement.style.borderColor = '#10b981';
                    dayElement.style.boxShadow = 'inset 0 0 0 2px #10b981';
                }
                
                dayElement.appendChild(dayNumber);
                calendarGrid.appendChild(dayElement);
            }
            
            // Afficher les dossiers d'aujourd'hui
            showDossiers(currentDate);
        }
        
        function showDossiers(date) {
            const dateString = date.toISOString().split('T')[0];
            const dossiers = dossiersData[dateString] || [];
            const dossiersList = document.getElementById('dossiersList');
            const selectedDate = document.getElementById('selectedDate');
            
            // Mettre à jour la date sélectionnée
            selectedDate.textContent = date.toLocaleDateString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).toUpperCase();
            
            // Vider la liste
            dossiersList.innerHTML = '';
            
            if (dossiers.length === 0) {
                const emptyMessage = document.createElement('div');
                emptyMessage.style.textAlign = 'center';
                emptyMessage.style.padding = '40px';
                emptyMessage.style.color = 'var(--gray)';
                emptyMessage.innerHTML = `
                    <div style="font-size: 48px; margin-bottom: 20px;">📭</div>
                    <h3 style="color: var(--light); margin-bottom: 10px;">Aucun dossier</h3>
                    <p>Aucune installation programmée pour cette date.</p>
                `;
                dossiersList.appendChild(emptyMessage);
                return;
            }
            
            // Afficher chaque dossier
            dossiers.forEach(dossier => {
                const dossierCard = document.createElement('div');
                dossierCard.className = 'dossier-card fade-in';
                
                dossierCard.innerHTML = `
                    <div class="dossier-header">
                        <div style="font-weight: 600; color: var(--light);">${dossier.team}</div>
                        <div class="dossier-team">${dossier.count} installation(s)</div>
                    </div>
                    <div class="dossier-content">
                        <div class="dossier-info">
                            <div class="info-label">Équipe</div>
                            <div class="info-value">${dossier.team}</div>
                        </div>
                        <div class="dossier-info">
                            <div class="info-label">Installations</div>
                            <div class="info-value">${dossier.count} client(s)</div>
                        </div>
                        <div class="dossier-info">
                            <div class="info-label">Statut</div>
                            <div class="info-value" style="color: #10b981;">● EN COURS</div>
                        </div>
                    </div>
                `;
                
                dossierCard.onclick = () => {
                    window.location.href = 'dashboard_' + dossier.team + '.html';
                };
                
                dossiersList.appendChild(dossierCard);
            });
        }
        
        function changeMonth(delta) {
            currentMonth += delta;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            } else if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            generateCalendar(currentYear, currentMonth);
        }
        
        function showToday() {
            currentDate = new Date();
            currentYear = currentDate.getFullYear();
            currentMonth = currentDate.getMonth();
            generateCalendar(currentYear, currentMonth);
        }
        
        function exportCalendar() {
            alert('Fonction d\'export à implémenter');
        }
        
        // Initialiser le calendrier
        generateCalendar(currentYear, currentMonth);
        
        // Animation
        document.addEventListener('DOMContentLoaded', function() {
            const calendarDays = document.querySelectorAll('.calendar-day');
            calendarDays.forEach((day, index) => {
                day.style.animationDelay = (index * 0.02) + 's';
            });
        });
    </script>
</body>
</html>"""
    
    with open("calendar.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    console.print("[green]✅ Calendrier généré : calendar.html[/green]")

# ==================== CRÉATION DES CARTES ====================

def create_card(row, team, theme_name, date_rdv, base_dir, site_dir):
    W, H = 1200, 1250
    colors = {
        "NOIR & OR": {"bg": "#050505", "head": "#111", "accent": "#D4AF37", "text": "white", "lab": "#666", "tn_text": "black"},
        "BLEU NUIT": {"bg": "#0A192F", "head": "#112240", "accent": "#64FFDA", "text": "white", "lab": "#8892B0", "tn_text": "black"},
        "CYBERPUNK": {"bg": "#000", "head": "#111", "accent": "#FF00E0", "text": "#33FF00", "lab": "#FF00E0", "tn_text": "white"},
        "MTN OFFICIEL": {"bg": "#002147", "head": "#FFD100", "accent": "#002147", "text": "white", "lab": "#FFF2A6", "tn_text": "black"},
        "MOOV OFFICIEL": {"bg": "#001A0F", "head": "#00A859", "accent": "#FFFFFF", "text": "white", "lab": "#9FF5C8", "tn_text": "black"}
    }
    
    c = colors.get(theme_name, colors["NOIR & OR"])
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    
    top = ImageColor.getrgb(c["bg"])
    bottom = ImageColor.getrgb(c["head"])
    draw_vertical_gradient(draw, W, H, top, bottom)
    
    f_bold = get_termux_font(bold=True)
    f_reg = get_termux_font(bold=False)
    
    try:
        f_h = ImageFont.truetype(f_bold, 55) if f_bold else ImageFont.load_default()
        f_l = ImageFont.truetype(f_bold, 22) if f_bold else ImageFont.load_default()
        f_v = ImageFont.truetype(f_reg, 35) if f_reg else ImageFont.load_default()
        f_tn = ImageFont.truetype(f_bold, 45) if f_bold else ImageFont.load_default()
    except:
        f_h = f_l = f_v = f_tn = ImageFont.load_default()
    
    # En-tête
    draw.rectangle([0, 0, W, 160], fill=c["head"])
    draw.line([0, 160, W, 160], fill=c["accent"], width=5)
    draw.text((50, 50), "FICHE D'INSTALLATION FTTH", fill=c["accent"], font=f_h)
    
    # Zone TN
    tn_val = clean_val(row.get('Numéro FTTH (TN)', ''))
    draw.rectangle([750, 190, 1150, 320], fill=c["accent"])
    draw.text((770, 205), "IDENTIFIANT TN", fill=c["tn_text"], font=f_l)
    draw.text((770, 245), tn_val if tn_val else "À GÉNÉRER", fill=c["tn_text"], font=f_tn)
    draw.text((770, 295), f"RDV : {date_rdv}", fill=c["tn_text"], font=f_l)
    
    # Informations client
    ville = clean_val(row.get("Ville/Commune d'habitation du Client", ""))
    quart_col = [col for col in row.index if "Quartier" in col]
    quartier = clean_val(row.get(quart_col[0], "")) if quart_col else ""
    
    data = [
        ("NOM DU CLIENT", clean_val(row.get('Nom et Prénoms du Client', ''), "NOM INCONNU").upper()),
        ("CONTACTS TÉLÉPHONIQUES", f"{format_tel(row.get('Contact du Client'))} / {format_tel(row.get('Second contact du Client'))}"),
        ("LOCALISATION", f"{ville} - {quartier}"),
        ("PROVENANCE", clean_val(row.get('Provenance', 'DIRECT')).upper()),
        ("NUMÉRO DE TICKET", clean_val(row.get('Numéro Ticket', 'NON FOURNI')).upper()),
        ("OFFRE SOUSCRITE", clean_val(row.get('Forfaits FTTH', 'FIBRE')).upper()),
        ("ÉQUIPE TECHNIQUE", team.upper()),
        ("DATE DE TRANSMISSION", clean_val(row.get('Date de Transmission', 'À CONFIRMER')))
    ]
    
    current_y = 200
    for label, val in data:
        draw.text((50, current_y), label, fill=c["lab"], font=f_l)
        draw.text((50, current_y + 40), str(val), fill=c["text"], font=f_v)
        draw.line([50, current_y + 95, 720, current_y + 95], fill=c["lab"], width=1)
        current_y += 130
    
    # Pied de page
    draw.rectangle([0, H - 70, W, H], fill=c["accent"])
    draw.text((50, H - 55), "MG TELECOM - GÉNÉRÉ DEPUIS TERMUX", fill=c["tn_text"], font=f_l)
    
    # Générer les fichiers associés
    client_name = "".join(filter(str.isalnum, clean_val(row.get('Nom et Prénoms du Client', 'Client'))))[:15]
    filename = f"{client_name}_{team}"
    
    generate_client_page(row, team, filename, date_rdv, site_dir)
    url = f"https://Nylockdev.github.io/mg-ftth/{base_dir}/site/client_{filename}.html"
    generate_qr_https(url, filename, base_dir)
    
    img.save(f"{base_dir}/Fiche_{filename}.png")

# ==================== FONCTION PRINCIPALE ====================
def main():  
    console.print("\n[bold gold1]📱 MG TELECOM : GÉNÉRATEUR PROFESSIONNEL FTTH[/bold gold1]\n")
    
    # Charger la base de données
    db = load_database()
    console.print(f"[dim]📊 Base de données chargée : {db['statistiques']['total_dossiers']} dossiers, {db['statistiques']['total_clients']} clients[/dim]")
    
    # Sélection du fichier
    files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.csv'))]
    if not files:
        console.print("[red]❌ Aucun fichier Excel/CSV trouvé.[/red]")
        return
    
    console.print("📂 Fichiers disponibles :")
    for i, f in enumerate(files, 1):
        console.print(f"  {i}. {f}")
    
    choix = Prompt.ask("Choisir le fichier", choices=[str(i) for i in range(1, len(files) + 1)])
    file_path = files[int(choix) - 1]
    
    df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
    
    # Filtre par ville
    v_col = "Ville/Commune d'habitation du Client"
    villes = ["TOUTES"] + sorted([str(v).strip().upper() for v in df[v_col].unique() if pd.notna(v)])
    v_sel = Prompt.ask("📍 Filtrer par ville", choices=villes, default="TOUTES")
    
    if v_sel != "TOUTES":
        df = df[df[v_col].str.contains(v_sel, case=False, na=False)]
    
    # Sélection du thème
    console.print("\n🎨 Thèmes disponibles :")
    for k, v in THEMES.items():
        console.print(f"  {k}. {v}")
    
    theme_name = THEMES[Prompt.ask("Choisir un thème", choices=list(THEMES.keys()), default="1")]
    
    # Tri des données
    df = df.sort_values(by=v_col)
    final_list = []
    derniere_eq = "WINAT"
    
    console.print(f"\n[bold cyan]📋 Attribution de {len(df)} dossiers :[/bold cyan]")
    
    # Attribution des équipes
    for i, (_, row) in enumerate(df.iterrows(), 1):
        nom = clean_val(row.get('Nom et Prénoms du Client', 'INCONNU')).upper()
        console.print(f"\n[white][{i}/{len(df)}][/white] [cyan]{nom}[/cyan]")
        eq = Prompt.ask("👉 Équipe", default=derniere_eq)
        derniere_eq = eq
        final_list.append((row, eq))
    
    # Détermination de la date
    horodateur = clean_val(final_list[0][0].get("Horodateur", ""))
    if horodateur:
        try:
            from dateutil import parser
            date_obj = parser.parse(horodateur)
            date_pdf = date_obj.strftime("%d-%m-%Y")
        except:
            date_pdf = datetime.now().strftime("%d-%m-%Y")
    else:
        date_pdf = datetime.now().strftime("%d-%m-%Y")
    
    base_dir = f"dossier_{date_pdf}"
    site_dir = f"{base_dir}/site"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(site_dir, exist_ok=True)
    
    if Confirm.ask(f"\n✅ Générer les {len(final_list)} fiches dans '{base_dir}' ?"):
        # Préparer les données pour la DB
        equipes_data = {}
        for r, t in final_list:
            if t not in equipes_data:
                equipes_data[t] = []
            client_name = "".join(filter(str.isalnum, clean_val(r.get('Nom et Prénoms du Client', 'Client'))))[:15]
            filename = f"{client_name}_{t}"
            # Convertir la Series en dict pour la DB
            row_dict = r.to_dict()
            equipes_data[t].append((row_dict, filename))
        
        # Générer les cartes
        for r, t in track(final_list, description="🔄 Génération en cours..."):
            create_card(r, t, theme_name, date_pdf, base_dir, site_dir)
        
        # Mettre à jour la base de données
        db = add_dossier_to_db(date_pdf, base_dir, equipes_data)
        
        console.print("\n[cyan]📊 Génération des dashboards...[/cyan]")
        
        # Générer les dashboards des équipes
        for equipe in equipes_data.keys():
            generate_dashboard_equipe(equipe, db)
            console.print(f"  ✓ Dashboard {equipe} créé")
        
        # Générer le dashboard admin
        generate_dashboard_admin(db)
        
        # Générer le calendrier
        generate_calendar(db)
        
        # Exporter en PDF
        export_pdf(date_pdf, base_dir)
        
        # Affichage du récapitulatif
        console.print(f"\n[bold green]✅ SUCCÈS ! Dossier créé : {base_dir}/[/bold green]")
        console.print(f"  📄 Fiches PNG : {base_dir}/")
        console.print(f"  📱 QR Codes : {base_dir}/")
        console.print(f"  🌐 Pages HTML : {site_dir}/")
        console.print(f"  📋 PDF complet : {base_dir}/Fiches_Installation_{date_pdf}.pdf")
        console.print(f"  📊 Dashboards équipes : dashboard_[EQUIPE].html")
        console.print(f"  📅 Calendrier : calendar.html")
        console.print(f"\n[bold yellow]🎛️ DASHBOARD ADMIN : dashboard_admin.html[/bold yellow]")
        
        console.print("\n[bold yellow]📊 RÉCAPITULATIF PAR ÉQUIPE :[/bold yellow]")
        for eq, dossiers in sorted(equipes_data.items()):
            console.print(f"  • {eq} : {len(dossiers)} fiche(s) → dashboard_{eq}.html")
        
        console.print("\n[bold cyan]💡 PROCHAINES ÉTAPES :[/bold cyan]")
        console.print(f"  1. Ouvrir 'dashboard_admin.html' pour voir tous les dossiers")
        console.print(f"  2. Naviguer via 'calendar.html' pour voir les dossiers par date")
        console.print(f"  3. Uploader le dossier '{base_dir}/' sur GitHub Pages")
        console.print(f"  4. Les QR codes pointent vers : https://Nylockdev.github.io/mg-ftth/{base_dir}/site/")
        console.print(f"\n[dim]Base de données sauvegardée dans : {DB_FILE}[/dim]")
        console.print("\n[dim]Généré avec ❤️ par MG TELECOM - Termux Edition[/dim]\n")

if __name__ == "__main__":
    main()
