# Configurazione dell'assistente Vapi

Questa cartella contiene la configurazione dell'assistente, da importare o ricreare su Vapi.

Il file `assistant.json` con l'export verrà aggiunto quando l'assistente è finalizzato, con chiavi e
identificativi rimossi. Per ricrearlo manualmente:

- Modello: GPT-4o (OpenAI)
- Trascrizione: Deepgram, lingua italiano
- Voce: una voce italiana
- Primo messaggio e prompt di sistema in italiano
- Tre tool di tipo API Request che puntano agli endpoint del backend:
  - informazioni sui servizi
  - verifica disponibilità
  - prenotazione

Il prompt di sistema istruisce l'assistente a rispondere solo in base alle informazioni recuperate
dal backend e a non inventare orari o procedure. L'URL dei tool è quello fornito da ngrok e va
aggiornato a ogni riavvio del tunnel.
