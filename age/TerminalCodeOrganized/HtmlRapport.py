import os
import webbrowser
from datetime import datetime

def generate_snapshot_report(engine, generals):
    """
    Génère un fichier HTML listant l'état complet de la bataille.
    Requis par le PDF (Section 69, point 11).
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    filename = "battle_snapshot.html"
    
    # Statistiques globales
    p1_units = engine.get_units_for_player(1)
    p2_units = engine.get_units_for_player(2)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rapport de Bataille - {timestamp}</title>
        <style>
            body {{ font-family: sans-serif; background-color: #f0f0f0; padding: 20px; }}
            h1 {{ color: #333; }}
            .stats {{ background: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .p1 {{ color: red; font-weight: bold; }}
            .p2 {{ color: blue; font-weight: bold; }}
            .dead {{ color: gray; text-decoration: line-through; }}
        </style>
    </head>
    <body>
        <h1>Rapport Tactique (Snapshot)</h1>
        <div class="stats">
            <p><strong>Temps écoulé (Tick) :</strong> {engine.tick:.2f}</p>
            <p><strong>Unités Joueur 1 :</strong> {len(p1_units)} survivants</p>
            <p><strong>Unités Joueur 2 :</strong> {len(p2_units)} survivants</p>
        </div>

        <h2>Détail des Unités</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Joueur</th>
                <th>Type</th>
                <th>Position (X, Y)</th>
                <th>PV</th>
                <th>Cible Actuelle (ID)</th>
                <th>État</th>
            </tr>
    """

    # On trie les unités par joueur puis par ID
    sorted_units = sorted(engine.units, key=lambda u: (u.player, u.id))

    for u in sorted_units:
        p_class = "p1" if u.player == 1 else "p2"
        state = "Vivant" if u.alive else "Mort"
        row_class = "" if u.alive else "dead"
        
        target_info = u.target_id if u.target_id is not None else "-"
        
        html += f"""
            <tr class="{row_class}">
                <td>{u.id}</td>
                <td class="{p_class}">Joueur {u.player}</td>
                <td>{u.unit_type}</td>
                <td>{u.x:.1f}, {u.y:.1f}</td>
                <td>{u.hp:.1f}</td>
                <td>{target_info}</td>
                <td>{state}</td>
            </tr>
        """

    html += """
        </table>
        <p><em>Généré par MedievAIl Engine</em></p>
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Report généré : {os.path.abspath(filename)}")
    
    # Optionnel : Ouvrir automatiquement dans le navigateur
    try:
        webbrowser.open('file://' + os.path.realpath(filename))
    except:
        pass