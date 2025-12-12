# app/services/invoice_extractor.py
import base64
import json
from pathlib import Path
from typing import Union

from datapizza.clients.openai import OpenAIClient
from datapizza.type import Media, MediaBlock, TextBlock

from app.config import settings
from app.schemas.invoice import InvoiceExtraction


class DatapizzaInvoiceExtractor:
    """
    Usa Datapizza (OpenAIClient + multimodality) per leggere una fattura
    da PDF/immagine e restituire una InvoiceExtraction.
    """

    def __init__(self):
        self.client = OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4.1-mini",
        )

    def _try_fix_json(self, raw_text: str) -> str:
        """
        Tenta di riparare un JSON malformato, specialmente stringhe non terminate.
        """
        # Rimuovi eventuali blocchi markdown ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json", "", 1).strip()
        
        # Se il JSON termina con una stringa non chiusa, prova a chiuderla
        if raw_text.count('"') % 2 != 0:
            # Numero dispari di virgolette = stringa non chiusa
            # Trova l'ultima virgoletta di apertura non chiusa
            last_quote_pos = raw_text.rfind('"')
            if last_quote_pos != -1:
                # Controlla se dopo l'ultima virgoletta c'è già una chiusura
                after_quote = raw_text[last_quote_pos + 1:]
                # Se dopo la virgoletta non c'è una virgoletta di chiusura prima di :, }, ], o fine stringa
                # allora dobbiamo chiudere la stringa
                needs_closing = True
                for char in after_quote:
                    if char == '"':
                        needs_closing = False
                        break
                    if char in [':', '}', ']', ',', '\n']:
                        break
                
                if needs_closing:
                    # Trova dove dovrebbe terminare la stringa (prima di :, }, ], , o fine riga)
                    end_pos = len(raw_text)
                    for i in range(last_quote_pos + 1, len(raw_text)):
                        char = raw_text[i]
                        if char in [':', '}', ']', ',']:
                            # Inserisci la virgoletta di chiusura prima di questo carattere
                            raw_text = raw_text[:i] + '"' + raw_text[i:]
                            break
                    else:
                        # Se non troviamo un carattere di terminazione, chiudi alla fine
                        raw_text = raw_text.rstrip() + '"'
        
        # Prova a chiudere oggetti/array non chiusi
        open_braces = raw_text.count('{') - raw_text.count('}')
        open_brackets = raw_text.count('[') - raw_text.count(']')
        
        if open_braces > 0:
            raw_text = raw_text.rstrip() + '\n' + '}' * open_braces
        if open_brackets > 0:
            raw_text = raw_text.rstrip() + '\n' + ']' * open_brackets
        
        return raw_text

    def _extract_json_from_text(self, raw_text: str) -> str:
        """
        Estrae il JSON dalla risposta, anche se circondato da testo.
        """
        # Rimuovi eventuali blocchi markdown ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json", "", 1).strip()
        
        # Cerca il primo { e l'ultimo } per estrarre solo il JSON
        first_brace = raw_text.find('{')
        if first_brace == -1:
            return raw_text
        
        # Trova l'ultima } corrispondente
        last_brace = raw_text.rfind('}')
        if last_brace == -1 or last_brace <= first_brace:
            return raw_text
        
        return raw_text[first_brace:last_brace + 1]

    # --- costruzione Media ---

    def _build_media_from_bytes(self, file_bytes: bytes, mime_ext: str) -> Media:
        """
        mime_ext: 'pdf', 'png', 'jpg', 'jpeg', ...
        """
        ext = mime_ext.lower()

        if ext in {"png", "jpg", "jpeg", "webp"}:
            media_type = "image"
        elif ext == "pdf":
            media_type = "pdf"
        else:
            raise ValueError(f"Estensione non supportata: {ext}")

        b64 = base64.b64encode(file_bytes).decode("utf-8")

        return Media(
            media_type=media_type,
            source_type="base64",
            source=b64,
            extension=ext,
        )

    def _build_system_prompt(self) -> str:
        schema = InvoiceExtraction.model_json_schema()

        return f"""
Sei un assistente contabile specializzato in lettura di fatture di acquisto.

Riceverai come input una fattura (PDF o immagine).
    Devi estrarre in modo strutturato:
    - dati del fornitore
    - numero fattura
    - data fattura
    - valuta (se presente)
    - totale documento (campo "Totale documento" comprensivo di IVA, se presente)
    - righe (codice articolo, descrizione, quantità, unità di misura, prezzo unitario, totale riga, IVA)

    Regole IMPORTANTI per le righe:
    - Nelle fatture c'è spesso una colonna "Cod. articolo" o simile che contiene il codice prodotto/fornitore.
    - DEVI SEPARARE il codice articolo dalla descrizione prodotto:
      * Il campo "product_code" deve contenere SOLO il codice articolo (es. "0015179.01", "2PAN161", "0015904.01")
      * Il campo "raw_description" deve contenere SOLO la descrizione del prodotto SENZA il codice articolo
      * Esempio ERRATO: raw_description="0015179.01 - B.A. CAMPANELLO S/V F"
      * Esempio CORRETTO: product_code="0015179.01", raw_description="B.A. CAMPANELLO S/V F"
    - Se il codice articolo non è presente o non è chiaramente separato, metti product_code a null.
    - Se un valore non è chiaramente visibile, mettilo a null.
    - Non inventare dati.
    - Se quantità o prezzo non sono chiari, usa null.
    - L'unità di misura (UM) può essere "kg", "pz", "L", "conf", ecc. Se non indicata, null.
    - La valuta di default è "EUR" se non è indicata ma è ragionevole.
    - Il totale documento (total_amount) è il campo "Totale documento" che appare nella fattura, comprensivo di IVA.

Devi rispondere SOLO con un JSON che rispetti ESATTAMENTE questo schema:

{json.dumps(schema, indent=2, ensure_ascii=False)}

IMPORTANTE: 
- Il JSON deve essere COMPLETO e VALIDO
- Assicurati di chiudere tutte le stringhe, oggetti e array
- Non troncare la risposta a metà di una stringa o di un campo
- Se una stringa contiene caratteri speciali, usali correttamente escapati
        """.strip()

    # --- entry point principale ---

    def extract_from_bytes(self, file_bytes: bytes, mime_ext: str) -> InvoiceExtraction:
        """
        Usa base64 come da esempio ufficiale Datapizza.
        mime_ext: estensione del file (png, jpg, jpeg, pdf)
        """
        
        media = self._build_media_from_bytes(file_bytes, mime_ext)

        system_prompt = self._build_system_prompt()

        blocks = [
            TextBlock(content=system_prompt),
            MediaBlock(media=media),
        ]

        response = self.client.invoke(
            input=blocks,
            max_tokens=8000,  # Aumentato per gestire fatture complesse
        )
        raw_text = response.text.strip()

        # Estrai solo la parte JSON dalla risposta
        raw_text = self._extract_json_from_text(raw_text)

        # Prova prima il parsing diretto
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            # Se fallisce, prova a riparare il JSON
            try:
                fixed_text = self._try_fix_json(raw_text)
                data = json.loads(fixed_text)
            except (json.JSONDecodeError, ValueError) as fix_error:
                # Se anche la riparazione fallisce, solleva un errore dettagliato
                error_pos = getattr(e, 'pos', None)
                error_line = getattr(e, 'lineno', None)
                error_col = getattr(e, 'colno', None)
                
                # Mostra il contesto intorno all'errore
                context_start = max(0, error_pos - 200) if error_pos else 0
                context_end = min(len(raw_text), error_pos + 200) if error_pos else 400
                context = raw_text[context_start:context_end]
                
                error_msg = (
                    f"Errore nel parsing JSON della risposta AI: {e}\n"
                    f"Posizione errore: linea {error_line}, colonna {error_col}, carattere {error_pos}\n"
                    f"Contesto intorno all'errore:\n{context}\n"
                    f"Primi 500 caratteri della risposta:\n{raw_text[:500]}"
                )
                raise ValueError(error_msg) from e

        invoice = InvoiceExtraction(**data)
        invoice.raw_text = raw_text
        return invoice


