# API CVR – gratis CVR API uden API-nøgle

Et gratis REST‑API til opslag i det danske CVR-register. Ingen API-nøgle, ingen konto, ingen dagskvote. Brug det direkte på **[apicvr.dk](https://apicvr.dk)**.

```bash
curl https://apicvr.dk/api/v1/24256790
```

- [API-dokumentation](https://apicvr.dk/api-dokumentation/) · [API reference (English)](https://apicvr.dk/en/api-reference/) · [Swagger](https://apicvr.dk/docs)
- [Guides og kodeeksempler](https://apicvr.dk/guides/): [Python](https://apicvr.dk/guides/cvr-api-python), [JavaScript](https://apicvr.dk/guides/cvr-api-javascript), [PHP](https://apicvr.dk/guides/cvr-api-php), [C#](https://apicvr.dk/guides/cvr-api-csharp), [Java](https://apicvr.dk/guides/cvr-api-java), [Go](https://apicvr.dk/guides/cvr-api-go), [Ruby](https://apicvr.dk/guides/cvr-api-ruby), [Excel](https://apicvr.dk/guides/cvr-opslag-excel)
- [Sammenligning: apicvr.dk vs. cvrapi.dk vs. cvr.dev](https://apicvr.dk/guides/cvr-api-sammenligning) · [Skift fra cvrapi.dk](https://apicvr.dk/guides/skift-fra-cvrapi-dk)
- [llms.txt](https://apicvr.dk/llms.txt) til AI-agenter

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

