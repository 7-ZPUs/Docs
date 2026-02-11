# Istruzioni per l'uso:
# Scarica il file .xml e mettilo nel cartella analisi, la stessa di questo file .py
# Esegui questo script:   python3 rinumera.py
# Ti chiederà di inserire un numero intero e da quello UC in poi, tutte le etichette UC{n} saranno scalate di 1 
# (es. se inserisci 3, UC3 diventerà UC2, UC4 diventerà UC3, ecc.)

import xml.etree.ElementTree as ET
import re

def decrementa_uc(file_input, file_output, soglia_uc):
    """
    Legge un file XML di draw.io, cerca pattern UC{n}.{...}
    e decrementa {n} di 1 se {n} >= soglia_uc.
    """
    
    try:
        # Carica il file XML
        tree = ET.parse(file_input)
        root = tree.getroot()
        
        # Regex per trovare UC seguito da un numero.
        # Spiegazione Regex:
        # UC      -> Cerca letteralmente "UC"
        # (\d+)   -> Gruppo 1: il numero principale (es. 3 in UC3.4.2)
        # ([\.\d]*) -> Gruppo 2: il resto del suffisso (es. .4.2)
        pattern = re.compile(r"UC(\d+)([\.\d]*)")
        
        conteggio_modifiche = 0

        # Itera su tutte le celle (mxCell) in tutti i diagrammi/pagine
        for cell in root.iter('mxCell'):
            valore_attuale = cell.get('value')
            
            if valore_attuale and "UC" in valore_attuale:
                
                # Funzione interna per la sostituzione logica
                def logica_sostituzione(match):
                    numero_principale = int(match.group(1))
                    suffisso = match.group(2) # es. ".1" o vuoto
                    
                    # Se il numero trovato è >= al numero inserito dall'utente
                    if numero_principale >= soglia_uc:
                        nuovo_numero = numero_principale - 1
                        return f"UC{nuovo_numero}{suffisso}"
                    
                    # Altrimenti lascia invariato
                    return match.group(0)

                # Applica la modifica se necessario
                nuovo_valore = pattern.sub(logica_sostituzione, valore_attuale)
                
                # Se è cambiato qualcosa, aggiorna l'XML
                if nuovo_valore != valore_attuale:
                    cell.set('value', nuovo_valore)
                    print(f"Modificato: '{valore_attuale}' -> '{nuovo_valore}'")
                    conteggio_modifiche += 1

        # Salva il nuovo file
        tree.write(file_output, encoding="UTF-8", xml_declaration=True)
        print(f"\nOperazione completata! {conteggio_modifiche} etichette aggiornate.")
        print(f"File salvato come: {file_output}")

    except FileNotFoundError:
        print(f"Errore: Il file '{file_input}' non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

# --- CONFIGURAZIONE ---
if __name__ == "__main__":
    # Nome del tuo file (assicurati che sia nella stessa cartella dello script)
    nome_file_input = "Diagrammi Pazzi.drawio.xml"
    nome_file_output = "Diagrammi_Pazzi_Rinumerati.xml"

    print(f"Script di rinumerazione per {nome_file_input}")
    try:
        input_utente = input("Inserisci il numero dello UC da cui partire a scalare (es. inserisci 3 per trasformare UC3 in UC2): ")
        soglia = int(input_utente)
        
        decrementa_uc(nome_file_input, nome_file_output, soglia)
        
    except ValueError:
        print("Errore: Per favore inserisci un numero intero valido.")