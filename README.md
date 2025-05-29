# API CVR

Et simpelt REST‑API til opslag i CVR. En kørende version findes på [apicvr.dk](https://apicvr.dk).

Dokumentation: [Docs](https://apicvr.dk/docs) · [ReDoc](https://apicvr.dk/redoc)

# Hvad er API CVR?

API CVR gør det lettere at integrere med det danske CVR‑register. Koden er open source og forslag til forbedringer er meget velkomne.

## Hvorfor ikke bruge System-Til-System-adgang?

Det er også en mulighed, men Elastic Search er bare noget bøvl

# API CVR er open source <3

API CVR er open source.
Hvis du nakker vores kode, så må du gerne kredittere os, men det betyder ikke det store.

Hvis du mener dine Python-skills er bedre end vores slam-kode, så lav et pull request, så skal vi nok læse det igennem.

# Opsæt din egen instans

1. Kopiér `env.example` til `.env` og indsæt dit API token.
2. Start serveren med Docker:

   ```bash
   docker compose up --build
   ```

Du skal have System-Til-System-adgang fra Erhvervsstyrelsen for at kunne forespørge CVR.

