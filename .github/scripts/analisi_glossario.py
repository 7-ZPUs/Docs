import os
import re
import glob
from datetime import datetime

# --- CONFIGURAZIONE ---
# Percorso relativo per arrivare alla cartella dei documenti dallo script:
PATH_DOCUMENTI = os.path.join("..", "..", "2_RTB") 
NOME_FILE_GLOSSARIO = "Glossario.tex"
OUTPUT_LOG = "log_glossario.txt" 
COMANDO_GLOSSARIO_DOCS = r'\\glossario\{' 
REGEX_DEFINIZIONE_GLOSSARIO = r'\\item\s*\\textbf\{(.+?)\}'

def estrai_contenuto_graffe(riga, start_keyword):
    """Estrae il contenuto bilanciato tra graffe."""
    termini = []
    cursore = 0
    keyword = start_keyword.replace('\\', '') 
    
    while True:
        start_index = riga.find(keyword, cursore)
        if start_index == -1:
            break
        
        content_start = start_index + len(keyword)
        current_pos = content_start
        parentesi_aperte = 1
        
        while current_pos < len(riga) and parentesi_aperte > 0:
            char = riga[current_pos]
            if char == '{':
                parentesi_aperte += 1
            elif char == '}':
                parentesi_aperte -= 1
            current_pos += 1
        
        if parentesi_aperte == 0:
            raw_term = riga[content_start : current_pos - 1]
            termini.append(raw_term)
            cursore = current_pos
        else:
            break
    return termini

def pulisci_latex_tags(testo):
    """Rimuove ricorsivamente i comandi LaTeX mantenendo il testo interno."""
    regex_nested = r'\\[a-zA-Z]+\{([^{}]+)\}'
    prev_text = None
    curr_text = testo
    while prev_text != curr_text:
        prev_text = curr_text
        curr_text = re.sub(regex_nested, r'\1', curr_text)
    return curr_text.strip()

def indicizza_glossario(contenuto_glossario):
    """Crea un indice dei termini definiti nel Glossario.tex"""
    indice = {}
    matches = re.findall(REGEX_DEFINIZIONE_GLOSSARIO, contenuto_glossario)
    for match in matches:
        termine_pulito = pulisci_latex_tags(match)
        termine_lower = termine_pulito.lower()
        if termine_lower in indice:
            indice[termine_lower] += 1
        else:
            indice[termine_lower] = 1
    return indice

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    target_dir = os.path.normpath(os.path.join(base_dir, PATH_DOCUMENTI))
    path_glossario = os.path.join(target_dir, NOME_FILE_GLOSSARIO)

    print(f"--- ANALISI GLOSSARIO (Controllo Ripetizioni) ---")
    print(f"Target: {target_dir}")

    # 1. Verifica e Indicizzazione Glossario
    if not os.path.exists(path_glossario):
        print(f"\n[ERRORE] Non trovo '{NOME_FILE_GLOSSARIO}'")
        return

    try:
        with open(path_glossario, 'r', encoding='utf-8') as f:
            contenuto_glossario = f.read()
        indice_termini_definiti = indicizza_glossario(contenuto_glossario)
        print(f"Termini definiti nel Glossario: {len(indice_termini_definiti)}")
    except Exception as e:
        print(f"[ERRORE] Lettura glossario: {e}")
        return

    # 3. Trova file .tex
    files_tex = glob.glob(os.path.join(target_dir, "*.tex"))
    if path_glossario in files_tex:
        files_tex.remove(path_glossario)

    # Preparazione Log
    log_lines = []
    header = f"--- REPORT ANALISI GLOSSARIO ---\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"Legenda:\n"
    header += f" [ OK (1°) ] -> Termine presente e citato per la prima volta nel file.\n"
    header += f" [ RIPETUTO] -> Termine già citato in precedenza nello stesso file (ridondante?).\n"
    header += f" [ MISSING ] -> Termine citato ma NON definito nel Glossario.\n"
    header += f" [ AMBIGUO ] -> Termine definito 2+ volte nel Glossario (errore grave).\n"
    header += "-"*85 + "\n"
    header += f"{'STATUS':<14} | {'TERMINE':<35} | {'FILE':<25} | {'RIGA':<5}\n"
    header += "-"*85
    log_lines.append(header)
    
    totale_mancanti = 0
    totale_ok = 0
    totale_ripetuti = 0
    totale_ambigui_glossario = 0

    # 4. Scansione Documenti
    for file_path in files_tex:
        nome_file_solo = os.path.basename(file_path)
        
        # SET per tracciare i termini già visti IN QUESTO FILE
        termini_visti_nel_file = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for numero_riga, riga in enumerate(lines, start=1):
                termini_grezzi = estrai_contenuto_graffe(riga, COMANDO_GLOSSARIO_DOCS)
                
                for termine_grezzo in termini_grezzi:
                    termine_pulito = pulisci_latex_tags(termine_grezzo)
                    if not termine_pulito: continue 

                    termine_search = termine_pulito.lower()
                    
                    # Logica di controllo
                    occorrenze_glossario = indice_termini_definiti.get(termine_search, 0)
                    status_simbolo = ""

                    if occorrenze_glossario == 0:
                        status_simbolo = "[MISSING]"
                        totale_mancanti += 1
                        
                    elif occorrenze_glossario > 1:
                        # Errore nel Glossario.tex (definito più volte)
                        status_simbolo = f"[AMBIGUO:{occorrenze_glossario}]"
                        totale_ambigui_glossario += 1
                        
                    else:
                        # Presente nel glossario 1 volta (Corretto).
                        # Ora controlliamo se lo stiamo ripetendo nel documento corrente.
                        if termine_search in termini_visti_nel_file:
                            status_simbolo = "[ RIPETUTO ]"
                            totale_ripetuti += 1
                        else:
                            status_simbolo = "[ OK (1\u00B0) ]" # 1° volta
                            totale_ok += 1
                            termini_visti_nel_file.add(termine_search)

                    riga_log = f"{status_simbolo:<14} | {termine_pulito:<35} | {nome_file_solo:<25} | {numero_riga:<5}"
                    log_lines.append(riga_log)

        except Exception as e:
            print(f"[ERRORE] File {nome_file_solo}: {e}")

    # Riepilogo
    riepilogo = "\n" + "-"*85 + "\n"
    riepilogo += f"RIEPILOGO:\n"
    riepilogo += f" Citazioni Valide (Prima occorrenza): {totale_ok}\n"
    riepilogo += f" Citazioni RIDONDANTI (Ripetute nel file): {totale_ripetuti}\n"
    riepilogo += f" Termini MANCANTI (Non in Glossario): {totale_mancanti}\n"
    riepilogo += f" Definizioni AMBIGUE (Duplicate in Glossario): {totale_ambigui_glossario}\n"
    
    log_lines.append(riepilogo)

    path_log_completo = os.path.join(base_dir, OUTPUT_LOG)
    with open(path_log_completo, 'w', encoding='utf-8') as f_log:
        f_log.write("\n".join(log_lines))

    print(f"\nAnalisi completata! Log: {path_log_completo}")
    print(riepilogo)

if __name__ == "__main__":
    main()