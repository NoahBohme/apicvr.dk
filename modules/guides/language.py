"""Language guides: CVR lookups from Python, JavaScript, PHP, C#, Excel and Google Sheets."""

_PY_LOOKUP = '''import json
import urllib.request

def get_company(cvr):
    url = f"{site}/api/v1/{cvr}"
    with urllib.request.urlopen(url, timeout=15) as res:
        return json.load(res)

company = get_company(24256790)
print(company["name"], company["zipcode"], company["city"])
print(company["industrydesc"], "-", company["companydesc"])'''

_PY_SEARCH = '''import json
import urllib.parse
import urllib.request

def search(name):
    url = f"{site}/api/v1/search/fuzzy/" + urllib.parse.quote(name)
    with urllib.request.urlopen(url, timeout=15) as res:
        return json.load(res)

for hit in search("novo nordisk")[:5]:
    print(hit["cvr_number"], hit["name"], "-", hit["industrytext"])'''

_PY_ERRORS = '''import json
import urllib.error
import urllib.request

def get_company(cvr):
    try:
        with urllib.request.urlopen(f"{site}/api/v1/{cvr}", timeout=15) as res:
            return json.load(res)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None  # no company with that CVR number
        raise  # 422 = not a number, 502 = the CVR register did not answer

print(get_company(99999999))  # None'''

_PY_OWNERS = '''company = get_company(24256790)

for owner in company["ejere"]:
    print(owner["name"], owner["ownership_range"])

for person in company["direktion"]:
    print(person["role"], person["name"])

if company["protected"]:
    print("Reklamebeskyttet - må ikke bruges til direkte markedsføring")'''

_PY_REQUESTS = '''import requests

res = requests.get("{site}/api/v1/24256790", timeout=15)
res.raise_for_status()
print(res.json()["name"])'''

_JS_LOOKUP = '''async function getCompany(cvr) {
  const res = await fetch(`{site}/api/v1/${cvr}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`CVR-API svarede ${res.status}`);
  return res.json();
}

const company = await getCompany(24256790);
console.log(company.name, company.zipcode, company.city);'''

_JS_SEARCH = '''async function searchCompanies(name) {
  const res = await fetch(`{site}/api/v1/search/fuzzy/${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error(`CVR-API svarede ${res.status}`);
  return res.json();
}

const hits = await searchCompanies("novo nordisk");
for (const hit of hits.slice(0, 5)) {
  console.log(hit.cvr_number, hit.name, "-", hit.industrytext);
}'''

_JS_OWNERS = '''const { ejere, direktion, protected: isProtected } = await getCompany(24256790);

for (const owner of ejere) {
  console.log(owner.name, owner.ownership_range);
}
for (const person of direktion) {
  console.log(person.role, person.name);
}
if (isProtected) {
  console.log("Reklamebeskyttet");
}'''

_PHP_LOOKUP = '''<?php
function get_company(int $cvr): ?array
{
    $ch = curl_init("{site}/api/v1/$cvr");
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
    $body = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if ($status === 404) {
        return null;
    }
    if ($status !== 200) {
        throw new RuntimeException("CVR-API svarede $status");
    }
    return json_decode($body, true);
}

$company = get_company(24256790);
echo $company["name"] . ", " . $company["zipcode"] . " " . $company["city"] . PHP_EOL;'''

_PHP_SEARCH = '''<?php
$name = rawurlencode("novo nordisk");
$hits = json_decode(file_get_contents("{site}/api/v1/search/fuzzy/$name"), true);

foreach (array_slice($hits, 0, 5) as $hit) {
    echo $hit["cvr_number"] . " " . $hit["name"] . PHP_EOL;
}'''

_PHP_OWNERS = '''<?php
$company = get_company(24256790);

foreach ($company["ejere"] as $owner) {
    echo $owner["name"] . " " . $owner["ownership_range"] . PHP_EOL;
}
foreach ($company["direktion"] as $person) {
    echo $person["role"] . ": " . $person["name"] . PHP_EOL;
}
if ($company["protected"]) {
    echo "Reklamebeskyttet" . PHP_EOL;
}'''

_CS_LOOKUP = '''using System.Net;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

var http = new HttpClient { BaseAddress = new Uri("{site}/") };

async Task<Company?> GetCompany(int cvr)
{
    var res = await http.GetAsync($"api/v1/{cvr}");
    if (res.StatusCode == HttpStatusCode.NotFound) return null;
    res.EnsureSuccessStatusCode(); // 422 or 502 throws
    return await res.Content.ReadFromJsonAsync<Company>();
}

var company = await GetCompany(24256790);
Console.WriteLine($"{company!.Name}, {company.Zipcode} {company.City}");

foreach (var owner in company.Ejere)
    Console.WriteLine($"{owner.Name} {owner.OwnershipRange}");

record Company(
    [property: JsonPropertyName("vat")] int Vat,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("zipcode")] int? Zipcode,
    [property: JsonPropertyName("city")] string? City,
    [property: JsonPropertyName("protected")] bool? Protected,
    [property: JsonPropertyName("ejere")] List<Owner> Ejere);

record Owner(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("ownership_range")] string? OwnershipRange);'''

_CS_SEARCH = '''var hits = await http.GetFromJsonAsync<List<Hit>>(
    "api/v1/search/fuzzy/" + Uri.EscapeDataString("novo nordisk"));

foreach (var hit in hits!.Take(5))
    Console.WriteLine($"{hit.CvrNumber} {hit.Name}");

record Hit(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("cvr_number")] int CvrNumber,
    [property: JsonPropertyName("industrytext")] string? IndustryText);'''

_JAVA_LOOKUP = '''import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;

public class Cvr {
    record Owner(String name, String ownership_range) {}
    record Company(int vat, String name, Integer zipcode, String city,
                   String industrydesc, List<Owner> ejere) {}

    static final HttpClient HTTP = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10)).build();
    static final ObjectMapper JSON = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    static Company getCompany(int cvr) throws Exception {
        HttpRequest req = HttpRequest.newBuilder(URI.create("{site}/api/v1/" + cvr)).GET().build();
        HttpResponse<String> res = HTTP.send(req, HttpResponse.BodyHandlers.ofString());
        if (res.statusCode() == 404) return null;
        if (res.statusCode() != 200) throw new RuntimeException("CVR-API svarede " + res.statusCode());
        return JSON.readValue(res.body(), Company.class);
    }

    public static void main(String[] args) throws Exception {
        Company c = getCompany(24256790);
        System.out.println(c.name() + ", " + c.zipcode() + " " + c.city());
        for (Owner o : c.ejere()) System.out.println(o.name() + " " + o.ownership_range());
    }
}'''

_JAVA_SEARCH = '''import com.fasterxml.jackson.core.type.TypeReference;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

record Hit(String name, Integer cvr_number, String industrytext) {}

static List<Hit> search(String name) throws Exception {
    String q = URLEncoder.encode(name, StandardCharsets.UTF_8).replace("+", "%20");
    HttpRequest req = HttpRequest.newBuilder(URI.create("{site}/api/v1/search/fuzzy/" + q)).build();
    String body = HTTP.send(req, HttpResponse.BodyHandlers.ofString()).body();
    return JSON.readValue(body, new TypeReference<List<Hit>>() {});
}

// search("novo nordisk").stream().limit(5)
//     .forEach(h -> System.out.println(h.cvr_number() + " " + h.name()));'''

_JAVA_MAVEN = '''<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.17.2</version>
</dependency>'''

_GO_LOOKUP = '''package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"
)

type Owner struct {
	Name           string `json:"name"`
	Type           string `json:"type"`
	OwnershipRange string `json:"ownership_range"`
}

type Company struct {
	Vat          int     `json:"vat"`
	Name         string  `json:"name"`
	Address      string  `json:"address"`
	Zipcode      int     `json:"zipcode"`
	City         string  `json:"city"`
	IndustryDesc string  `json:"industrydesc"`
	Protected    bool    `json:"protected"`
	Ejere        []Owner `json:"ejere"`
}

var ErrNotFound = errors.New("cvr: company not found")

var client = &http.Client{Timeout: 15 * time.Second}

func GetCompany(cvr int) (*Company, error) {
	res, err := client.Get(fmt.Sprintf("{site}/api/v1/%d", cvr))
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	switch res.StatusCode {
	case http.StatusOK:
		var c Company
		return &c, json.NewDecoder(res.Body).Decode(&c)
	case http.StatusNotFound:
		return nil, ErrNotFound
	default:
		return nil, fmt.Errorf("cvr: unexpected status %d", res.StatusCode)
	}
}

func main() {
	c, err := GetCompany(24256790)
	if err != nil {
		panic(err)
	}
	fmt.Println(c.Name, c.Zipcode, c.City)
	for _, o := range c.Ejere {
		fmt.Println(o.Name, o.OwnershipRange)
	}
}'''

_GO_SEARCH = '''type Hit struct {
	Name         string `json:"name"`
	CvrNumber    int    `json:"cvr_number"`
	IndustryText string `json:"industrytext"`
}

func Search(name string) ([]Hit, error) {
	res, err := client.Get("{site}/api/v1/search/fuzzy/" + url.PathEscape(name))
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var hits []Hit
	return hits, json.NewDecoder(res.Body).Decode(&hits)
}

// Kræver import af "net/url".'''

_RUBY_LOOKUP = '''require "net/http"
require "json"

def get_company(cvr)
  uri = URI("{site}/api/v1/#{cvr}")
  res = Net::HTTP.get_response(uri)

  case res
  when Net::HTTPOK       then JSON.parse(res.body)
  when Net::HTTPNotFound then nil
  else raise "CVR-API svarede #{res.code}" # 422 eller 502
  end
end

company = get_company(24256790)
puts "#{company["name"]}, #{company["zipcode"]} #{company["city"]}"

company["ejere"].each do |owner|
  puts "#{owner["name"]} #{owner["ownership_range"]}"
end'''

_RUBY_SEARCH = '''require "net/http"
require "json"
require "erb"

def search(name)
  uri = URI("{site}/api/v1/search/fuzzy/#{ERB::Util.url_encode(name)}")
  JSON.parse(Net::HTTP.get(uri))
end

search("novo nordisk").first(5).each do |hit|
  puts "#{hit["cvr_number"]} #{hit["name"]} - #{hit["industrytext"]}"
end'''

_RUBY_RAILS = '''# app/services/cvr_lookup.rb
class CvrLookup
  def self.call(cvr)
    Rails.cache.fetch("cvr/#{cvr}", expires_in: 6.hours) do
      res = Net::HTTP.get_response(URI("{site}/api/v1/#{cvr}"))
      res.is_a?(Net::HTTPOK) ? JSON.parse(res.body) : nil
    end
  end
end'''

_PQ_LOOKUP = '''let
    Source = Json.Document(Web.Contents("{site}/api/v1/24256790")),
    Company = Record.SelectFields(Source,
        {"vat", "name", "address", "zipcode", "city", "industrydesc", "companydesc", "status"}),
    Table = Table.FromRecords({Company})
in
    Table'''

_PQ_FUNCTION = '''(cvr as text) =>
let
    Source = Json.Document(Web.Contents("{site}/api/v1/", [RelativePath = cvr])),
    Result = [
        name = Source[name],
        city = Source[city],
        industry = Source[industrydesc],
        protected = Source[protected]
    ]
in
    Result'''

_PQ_OWNERS = '''let
    Source = Json.Document(Web.Contents("{site}/api/v1/24256790")),
    Owners = Table.FromRecords(Source[ejere]),
    Selected = Table.SelectColumns(Owners, {"name", "type", "ownership_range"})
in
    Selected'''

_GS_SCRIPT = '''/**
 * Henter et felt fra CVR-registret.
 * Eksempel: =CVR(A2; "name")
 *
 * @param {number} cvr CVR-nummer (8 cifre)
 * @param {string} field Feltnavn, fx "name", "city" eller "industrydesc"
 * @customfunction
 */
function CVR(cvr, field) {
  const cache = CacheService.getScriptCache();
  const key = "cvr_" + cvr;
  let json = cache.get(key);

  if (!json) {
    const res = UrlFetchApp.fetch("{site}/api/v1/" + cvr, { muteHttpExceptions: true });
    if (res.getResponseCode() === 404) return "Ikke fundet";
    if (res.getResponseCode() !== 200) return "Fejl " + res.getResponseCode();
    json = res.getContentText();
    cache.put(key, json, 21600); // 6 timer
  }

  const company = JSON.parse(json);
  const value = company[field || "name"];
  return Array.isArray(value) ? value.map(v => v.name).join(", ") : value;
}'''

_GS_SEARCH = '''/**
 * Søger virksomheder på navn og returnerer CVR-nummer og navn.
 * Eksempel: =CVRSOEG("novo nordisk")
 * @customfunction
 */
function CVRSOEG(name) {
  const url = "{site}/api/v1/search/fuzzy/" + encodeURIComponent(name);
  const hits = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  return hits.slice(0, 10).map(h => [h.cvr_number, h.name, h.industrytext]);
}'''


def _errors_table(lang):
    if lang == "da":
        return ("table", ["Status", "Betydning"], [
            ["<code>200</code>", "Virksomheden blev fundet. Svaret er JSON."],
            ["<code>404</code>", "Der findes ingen virksomhed med det CVR-nummer. Body: <code>{\"detail\": {\"error\": \"NOT_FOUND\"}}</code>"],
            ["<code>422</code>", "CVR-nummeret er ikke et tal."],
            ["<code>502</code>", "CVR-registret svarede ikke. Prøv igen om lidt."],
        ])
    return ("table", ["Status", "Meaning"], [
        ["<code>200</code>", "The company was found. The body is JSON."],
        ["<code>404</code>", "No company has that CVR number. Body: <code>{\"detail\": {\"error\": \"NOT_FOUND\"}}</code>"],
        ["<code>422</code>", "The CVR number isn't a number."],
        ["<code>502</code>", "The CVR register didn't answer. Try again shortly."],
    ])


_PROTECTED_DA = (
    "Tjek altid <code>protected</code>, før du bruger data til markedsføring. Er feltet <code>true</code>, "
    "har virksomheden frabedt sig reklamehenvendelser."
)
_PROTECTED_EN = (
    "Always check <code>protected</code> before using the data for marketing. When it's <code>true</code>, "
    "the company has opted out of direct marketing."
)

PAGES = [
    {
        "id": "python",
        "family": "language",
        "slug": {"da": "cvr-api-python", "en": "cvr-api-python"},
        "related": ["javascript", "owners-management", "validate-cvr"],
        "da": {
            "title": "CVR API i Python – slå virksomheder op på få linjer",
            "description": "Slå danske virksomheder op med Python og et gratis CVR API. Kodeeksempler til CVR-opslag, navnesøgning, ejere, direktion og fejlhåndtering.",
            "h1": "CVR-opslag i Python",
            "lead": "Med CVR-API kan du hente virksomhedsdata i Python med et enkelt HTTP-kald. Du behøver ingen API-nøgle eller SDK. Standardbiblioteket er nok.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("p", "Kald <code>/api/v1/{cvr}</code> og læs JSON-svaret. Eksemplet bruger kun <code>urllib</code> fra standardbiblioteket."),
                ("code", "python", _PY_LOOKUP),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Fuzzy-søgningen finder virksomheder, selv om navnet er stavet lidt forkert. Hvert hit har <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> og <code>industrytext</code>."),
                ("code", "python", _PY_SEARCH),
                ("h2", "Håndter fejl"),
                ("p", "API'et bruger almindelige HTTP-statuskoder, så du kan reagere på dem direkte:"),
                _errors_table("da"),
                ("code", "python", _PY_ERRORS),
                ("h2", "Ejere, direktion og reklamebeskyttelse"),
                ("p", "Det fulde opslag indeholder legale ejere med ejerandel i intervaller og den nuværende direktion."),
                ("code", "python", _PY_OWNERS),
                ("note", _PROTECTED_DA),
                ("h2", "Foretrækker du requests?"),
                ("code", "python", _PY_REQUESTS),
            ],
            "faq": [
                ("Skal jeg bruge en API-nøgle i Python?", "Nej. CVR-API kræver hverken nøgle eller konto. Et almindeligt GET-kald er nok."),
                ("Hvilken Python-version kræves?", "Eksemplerne virker med Python 3.6 og nyere, fordi de kun bruger standardbiblioteket og f-strings."),
                ("Kan jeg slå mange virksomheder op på én gang?", "Lav ét kald pr. CVR-nummer, og hold tempoet nede. Har du brug for vedvarende høj trafik, så skriv til noah@noahbohme.com."),
            ],
        },
        "en": {
            "title": "CVR API in Python – look up Danish companies",
            "description": "Look up Danish companies from Python with a free CVR API. Code examples for CVR lookup, name search, owners, management and error handling.",
            "h1": "CVR lookups in Python",
            "lead": "CVR-API lets you fetch Danish company data in Python with a single HTTP request. You don't need an API key or an SDK. The standard library is enough.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("p", "Call <code>/api/v1/{cvr}</code> and read the JSON response. This example only uses <code>urllib</code> from the standard library."),
                ("code", "python", _PY_LOOKUP),
                ("h2", "Search by company name"),
                ("p", "Fuzzy search finds companies even when the name is slightly misspelled. Each hit has <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> and <code>industrytext</code>."),
                ("code", "python", _PY_SEARCH),
                ("h2", "Handle errors"),
                ("p", "The API uses standard HTTP status codes, so you can act on them directly:"),
                _errors_table("en"),
                ("code", "python", _PY_ERRORS),
                ("h2", "Owners, management and marketing protection"),
                ("p", "The full lookup includes legal owners with ownership share in ranges, and the current management."),
                ("code", "python", _PY_OWNERS),
                ("note", _PROTECTED_EN),
                ("h2", "Prefer requests?"),
                ("code", "python", _PY_REQUESTS),
            ],
            "faq": [
                ("Do I need an API key in Python?", "No. CVR-API needs no key and no account. A plain GET request is enough."),
                ("Which Python version is required?", "The examples work on Python 3.6 and later, since they only use the standard library and f-strings."),
                ("Can I look up many companies at once?", "Make one request per CVR number and keep the pace reasonable. If you need sustained heavy traffic, email noah@noahbohme.com."),
            ],
        },
    },
    {
        "id": "javascript",
        "family": "language",
        "slug": {"da": "cvr-api-javascript", "en": "cvr-api-javascript"},
        "related": ["react-form", "python", "find-by-email"],
        "da": {
            "title": "CVR API i JavaScript – opslag med fetch i browser og Node",
            "description": "Slå danske virksomheder op med JavaScript og fetch. Virker i browseren og i Node.js. Eksempler på CVR-opslag, navnesøgning, ejere og fejlhåndtering.",
            "h1": "CVR-opslag i JavaScript",
            "lead": "CVR-API sender CORS-headers, så du kan kalde det direkte fra browseren. Samme kode virker i Node.js 18 og nyere, hvor fetch er indbygget.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("code", "javascript", _JS_LOOKUP),
                ("p", "<code>getCompany</code> returnerer <code>null</code>, når CVR-nummeret ikke findes (404). Andre fejl kaster en exception."),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Fuzzy-søgningen er velegnet til autocomplete. Husk at <code>encodeURIComponent</code> navnet."),
                ("code", "javascript", _JS_SEARCH),
                ("note", "Bruger du søgningen i et inputfelt, så vent ca. 300 ms efter sidste tastetryk (debounce), før du kalder API'et."),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("h2", "Ejere, direktion og reklamebeskyttelse"),
                ("code", "javascript", _JS_OWNERS),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Kan jeg kalde CVR-API direkte fra browseren?", "Ja. API'et tillader CORS fra alle domæner, så du behøver ingen proxy."),
                ("Virker eksemplerne i Node.js?", "Ja, i Node.js 18 og nyere, hvor <code>fetch</code> er indbygget. I ældre versioner kan du bruge pakken <code>node-fetch</code>."),
                ("Kan jeg bruge det med TypeScript?", "Ja. Den fulde OpenAPI-specifikation ligger på <a href=\"/openapi.json\">/openapi.json</a>, så du kan generere typer ud fra den."),
            ],
        },
        "en": {
            "title": "CVR API in JavaScript – fetch from browser and Node",
            "description": "Look up Danish companies with JavaScript and fetch. Works in the browser and in Node.js. Examples for CVR lookup, name search, owners and errors.",
            "h1": "CVR lookups in JavaScript",
            "lead": "CVR-API sends CORS headers, so you can call it straight from the browser. The same code works in Node.js 18 and later, where fetch is built in.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("code", "javascript", _JS_LOOKUP),
                ("p", "<code>getCompany</code> returns <code>null</code> when the CVR number doesn't exist (404). Any other error throws."),
                ("h2", "Search by company name"),
                ("p", "Fuzzy search works well for autocomplete. Remember to <code>encodeURIComponent</code> the name."),
                ("code", "javascript", _JS_SEARCH),
                ("note", "If you search from an input field, wait about 300 ms after the last keystroke (debounce) before calling the API."),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("h2", "Owners, management and marketing protection"),
                ("code", "javascript", _JS_OWNERS),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Can I call CVR-API directly from the browser?", "Yes. The API allows CORS from any origin, so you don't need a proxy."),
                ("Do the examples work in Node.js?", "Yes, in Node.js 18 and later, where <code>fetch</code> is built in. On older versions you can use the <code>node-fetch</code> package."),
                ("Can I use it with TypeScript?", "Yes. The full OpenAPI specification is at <a href=\"/openapi.json\">/openapi.json</a>, so you can generate types from it."),
            ],
        },
    },
    {
        "id": "php",
        "family": "language",
        "slug": {"da": "cvr-api-php", "en": "cvr-api-php"},
        "related": ["woocommerce", "validate-cvr", "python"],
        "da": {
            "title": "CVR API i PHP – slå virksomheder op med cURL",
            "description": "Hent danske virksomhedsdata i PHP med et gratis CVR API. Eksempler med cURL og file_get_contents til CVR-opslag, navnesøgning og ejere.",
            "h1": "CVR-opslag i PHP",
            "lead": "Uanset om du bygger en webshop, et CRM eller en faktureringsløsning, kan du hente CVR-data i PHP med cURL eller file_get_contents. Der er ingen nøgle at holde styr på.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("p", "Med cURL kan du se HTTP-statuskoden og skelne mellem en ukendt virksomhed og en egentlig fejl."),
                ("code", "php", _PHP_LOOKUP),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Til hurtige scripts er <code>file_get_contents</code> nok. Brug <code>rawurlencode</code>, så mellemrum og æøå bliver kodet korrekt."),
                ("code", "php", _PHP_SEARCH),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("h2", "Ejere, direktion og reklamebeskyttelse"),
                ("code", "php", _PHP_OWNERS),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Virker det med Laravel og Symfony?", "Ja. Brug Laravels <code>Http::get()</code> eller Symfonys HttpClient på samme URL. Svaret er almindelig JSON."),
                ("Bør jeg cache svarene?", "Ja, hvis du slår de samme virksomheder op tit. Virksomhedsdata ændrer sig sjældent, så en cache på et par timer er fin."),
            ],
        },
        "en": {
            "title": "CVR API in PHP – look up Danish companies with cURL",
            "description": "Fetch Danish company data in PHP with a free CVR API. Examples using cURL and file_get_contents for CVR lookup, name search and owners.",
            "h1": "CVR lookups in PHP",
            "lead": "Whether you're building a web shop, a CRM or an invoicing tool, you can fetch CVR data in PHP with cURL or file_get_contents. There's no key to manage.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("p", "With cURL you can read the HTTP status code and tell an unknown company apart from a real error."),
                ("code", "php", _PHP_LOOKUP),
                ("h2", "Search by company name"),
                ("p", "For quick scripts, <code>file_get_contents</code> is enough. Use <code>rawurlencode</code> so spaces and Danish letters are encoded correctly."),
                ("code", "php", _PHP_SEARCH),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("h2", "Owners, management and marketing protection"),
                ("code", "php", _PHP_OWNERS),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Does it work with Laravel and Symfony?", "Yes. Use Laravel's <code>Http::get()</code> or Symfony's HttpClient against the same URL. The response is plain JSON."),
                ("Should I cache responses?", "Yes, if you look up the same companies often. Company data changes rarely, so caching for a few hours is fine."),
            ],
        },
    },
    {
        "id": "csharp",
        "family": "language",
        "slug": {"da": "cvr-api-csharp", "en": "cvr-api-csharp"},
        "related": ["java", "owners-management", "validate-cvr"],
        "da": {
            "title": "CVR API i C# og .NET – opslag med HttpClient",
            "description": "Slå danske virksomheder op i C# og .NET med HttpClient og System.Text.Json. Eksempler på CVR-opslag, navnesøgning, ejere og fejlhåndtering.",
            "h1": "CVR-opslag i C# og .NET",
            "lead": "I .NET kan du hente CVR-data med HttpClient og deserialisere svaret direkte til dine egne records. Du behøver ingen NuGet-pakker ud over det, der følger med .NET.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("p", "Eksemplet er et top-level program til .NET 6 og nyere. Records'ene indeholder kun de felter, du har brug for. Resten ignoreres."),
                ("code", "csharp", _CS_LOOKUP),
                ("h2", "Søg på virksomhedsnavn"),
                ("code", "csharp", _CS_SEARCH),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("p", "<code>EnsureSuccessStatusCode()</code> kaster en <code>HttpRequestException</code> ved 422 og 502. Fang den, hvis du vil prøve igen."),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Hvordan bruger jeg HttpClient i ASP.NET Core?", "Registrér en typed client med <code>builder.Services.AddHttpClient&lt;CvrClient&gt;()</code> i stedet for at oprette nye HttpClient-instanser pr. kald."),
                ("Hvorfor er feltnavnene på dansk?", "Felter som <code>ejere</code> og <code>direktion</code> følger CVR-registrets egne begreber. Med <code>JsonPropertyName</code> kan du give dem engelske navne i din kode."),
            ],
        },
        "en": {
            "title": "CVR API in C# and .NET – lookups with HttpClient",
            "description": "Look up Danish companies in C# and .NET with HttpClient and System.Text.Json. Examples for CVR lookup, name search, owners and error handling.",
            "h1": "CVR lookups in C# and .NET",
            "lead": "In .NET you can fetch CVR data with HttpClient and deserialize the response straight into your own records. You don't need any NuGet packages beyond what ships with .NET.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("p", "This is a top-level program for .NET 6 and later. The records only include the fields you need. The rest is ignored."),
                ("code", "csharp", _CS_LOOKUP),
                ("h2", "Search by company name"),
                ("code", "csharp", _CS_SEARCH),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("p", "<code>EnsureSuccessStatusCode()</code> throws an <code>HttpRequestException</code> on 422 and 502. Catch it if you want to retry."),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("How do I use HttpClient in ASP.NET Core?", "Register a typed client with <code>builder.Services.AddHttpClient&lt;CvrClient&gt;()</code> instead of creating a new HttpClient per request."),
                ("Why are some field names Danish?", "Fields like <code>ejere</code> (owners) and <code>direktion</code> (management) follow the CVR register's own terms. With <code>JsonPropertyName</code> you can give them English names in your code."),
            ],
        },
    },
    {
        "id": "java",
        "updated": "2026-11-06",
        "family": "language",
        "slug": {"da": "cvr-api-java", "en": "cvr-api-java"},
        "related": ["csharp", "owners-management", "validate-cvr"],
        "da": {
            "title": "CVR API i Java – opslag med HttpClient og Jackson",
            "description": "Slå danske virksomheder op i Java med den indbyggede HttpClient og Jackson. Kodeeksempler på CVR-opslag, navnesøgning, ejere og fejlhåndtering.",
            "h1": "CVR-opslag i Java",
            "lead": "Fra Java 11 og frem har du en HTTP-klient i standardbiblioteket, så et CVR-opslag kræver kun ét kald og en JSON-parser. Du behøver ingen API-nøgle.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("p", "Eksemplet bruger <code>java.net.http.HttpClient</code> og records fra Java 16+. Jackson mapper JSON-svaret til records'ene og ignorerer de felter, du ikke har taget med."),
                ("code", "java", _JAVA_LOOKUP),
                ("p", "Bemærk: <code>protected</code> er et reserveret ord i Java. Vil du læse feltet, så annotér komponenten med <code>@JsonProperty(\"protected\")</code>."),
                ("h2", "Tilføj Jackson"),
                ("p", "Java har ingen indbygget JSON-parser. Jackson er det mest udbredte valg. Med Maven:"),
                ("code", "xml", _JAVA_MAVEN),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Fuzzy-søgningen returnerer et slankt svar med <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> og <code>industrytext</code>, også når navnet er stavet lidt forkert."),
                ("code", "java", _JAVA_SEARCH),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Virker det i Spring Boot?", "Ja. Du kan bruge <code>RestClient</code> eller <code>WebClient</code> i stedet for HttpClient. Spring Boot har allerede Jackson med, så du skal kun definere dine records."),
                ("Hvilken Java-version kræves?", "HttpClient kræver Java 11. Records kræver Java 16. På ældre versioner kan du bruge almindelige klasser med getters i stedet."),
                ("Skal jeg bruge en API-nøgle?", "Nej. CVR-API kræver hverken nøgle eller konto."),
            ],
        },
        "en": {
            "title": "CVR API in Java – lookups with HttpClient and Jackson",
            "description": "Look up Danish companies in Java with the built-in HttpClient and Jackson. Code examples for CVR lookup, name search, owners and error handling.",
            "h1": "CVR lookups in Java",
            "lead": "Since Java 11 the standard library has an HTTP client, so a CVR lookup only takes one request and a JSON parser. You don't need an API key.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("p", "This example uses <code>java.net.http.HttpClient</code> and records from Java 16+. Jackson maps the JSON response onto the records and ignores the fields you left out."),
                ("code", "java", _JAVA_LOOKUP),
                ("p", "Note: <code>protected</code> is a reserved word in Java. To read the field, annotate the component with <code>@JsonProperty(\"protected\")</code>."),
                ("h2", "Add Jackson"),
                ("p", "Java has no built-in JSON parser. Jackson is the most common choice. With Maven:"),
                ("code", "xml", _JAVA_MAVEN),
                ("h2", "Search by company name"),
                ("p", "Fuzzy search returns a slim response with <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> and <code>industrytext</code>, even when the name is slightly misspelled."),
                ("code", "java", _JAVA_SEARCH),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Does it work in Spring Boot?", "Yes. You can use <code>RestClient</code> or <code>WebClient</code> instead of HttpClient. Spring Boot already ships Jackson, so you only need to define your records."),
                ("Which Java version is required?", "HttpClient needs Java 11. Records need Java 16. On older versions, use plain classes with getters instead."),
                ("Do I need an API key?", "No. CVR-API needs no key and no account."),
            ],
        },
    },
    {
        "id": "go",
        "updated": "2026-11-06",
        "family": "language",
        "slug": {"da": "cvr-api-go", "en": "cvr-api-go"},
        "related": ["python", "owners-management", "validate-cvr"],
        "da": {
            "title": "CVR API i Go – opslag med net/http og encoding/json",
            "description": "Slå danske virksomheder op i Go med net/http og encoding/json fra standardbiblioteket. Eksempler på CVR-opslag, navnesøgning, ejere og fejl.",
            "h1": "CVR-opslag i Go",
            "lead": "I Go klarer standardbiblioteket det hele: <code>net/http</code> til kaldet og <code>encoding/json</code> til at læse svaret ind i en struct. Ingen API-nøgle, ingen eksterne pakker.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("p", "Structen indeholder kun de felter, du har brug for. Felter i svaret, som ikke er med i structen, bliver ignoreret."),
                ("code", "go", _GO_LOOKUP),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Fuzzy-søgningen finder virksomheder, selv om navnet er stavet lidt forkert. Hvert hit har <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> og <code>industrytext</code>."),
                ("code", "go", _GO_SEARCH),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("p", "I eksemplet bliver 404 til <code>ErrNotFound</code>, så du kan tjekke det med <code>errors.Is(err, ErrNotFound)</code>. Andre statuskoder giver en almindelig fejl."),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Hvorfor er nogle felter null?", "Felter uden værdi i CVR er <code>null</code> i JSON. Med almindelige typer i structen får du nulværdien (fx en tom streng). Brug pointere som <code>*string</code>, hvis du skal kende forskel."),
                ("Kan jeg kalde API'et parallelt fra goroutines?", "Ja, men hold tempoet nede, fx med en semaphore på få samtidige kald. Har du brug for vedvarende høj trafik, så skriv til noah@noahbohme.com."),
            ],
        },
        "en": {
            "title": "CVR API in Go – lookups with net/http and encoding/json",
            "description": "Look up Danish companies in Go with net/http and encoding/json from the standard library. Examples for CVR lookup, name search, owners and errors.",
            "h1": "CVR lookups in Go",
            "lead": "In Go the standard library covers everything: <code>net/http</code> for the request and <code>encoding/json</code> to decode the response into a struct. No API key, no third-party packages.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("p", "The struct only holds the fields you need. Fields in the response that aren't in the struct are ignored."),
                ("code", "go", _GO_LOOKUP),
                ("h2", "Search by company name"),
                ("p", "Fuzzy search finds companies even when the name is slightly misspelled. Each hit has <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> and <code>industrytext</code>."),
                ("code", "go", _GO_SEARCH),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("p", "In the example, 404 becomes <code>ErrNotFound</code>, so you can check for it with <code>errors.Is(err, ErrNotFound)</code>. Other status codes return a plain error."),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Why are some fields null?", "Fields without a value in CVR are <code>null</code> in the JSON. With plain types in the struct you get the zero value (e.g. an empty string). Use pointers such as <code>*string</code> if you need to tell the difference."),
                ("Can I call the API concurrently from goroutines?", "Yes, but keep the pace down, for example with a semaphore allowing a few requests at a time. If you need sustained heavy traffic, email noah@noahbohme.com."),
            ],
        },
    },
    {
        "id": "ruby",
        "updated": "2026-11-06",
        "family": "language",
        "slug": {"da": "cvr-api-ruby", "en": "cvr-api-ruby"},
        "related": ["python", "owners-management", "validate-cvr"],
        "da": {
            "title": "CVR API i Ruby og Rails – opslag med Net::HTTP",
            "description": "Slå danske virksomheder op i Ruby og Rails med Net::HTTP og JSON fra standardbiblioteket. Eksempler på CVR-opslag, navnesøgning, cache og fejl.",
            "h1": "CVR-opslag i Ruby og Rails",
            "lead": "Ruby har både HTTP og JSON i standardbiblioteket, så et CVR-opslag fylder kun et par linjer. Du behøver hverken gems eller API-nøgle.",
            "blocks": [
                ("h2", "Slå en virksomhed op på CVR-nummer"),
                ("code", "ruby", _RUBY_LOOKUP),
                ("h2", "Søg på virksomhedsnavn"),
                ("p", "Fuzzy-søgningen finder virksomheder, selv om navnet er stavet lidt forkert. Hvert hit har <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> og <code>industrytext</code>."),
                ("code", "ruby", _RUBY_SEARCH),
                ("h2", "I en Rails-app"),
                ("p", "Firmadata ændrer sig sjældent. Læg opslaget i en service, og cache svaret, så samme CVR-nummer ikke slås op ved hver request:"),
                ("code", "ruby", _RUBY_RAILS),
                ("h2", "Håndter fejl"),
                _errors_table("da"),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Kan jeg bruge Faraday eller HTTParty?", "Ja. API'et er et almindeligt GET-kald, der returnerer JSON, så enhver HTTP-klient virker. Eksemplerne bruger Net::HTTP, fordi det ikke kræver nogen gems."),
                ("Skal jeg bruge en API-nøgle?", "Nej. CVR-API kræver hverken nøgle eller konto."),
            ],
        },
        "en": {
            "title": "CVR API in Ruby and Rails – lookups with Net::HTTP",
            "description": "Look up Danish companies in Ruby and Rails with Net::HTTP and JSON from the standard library. Examples for CVR lookup, name search, caching and errors.",
            "h1": "CVR lookups in Ruby and Rails",
            "lead": "Ruby ships both HTTP and JSON in the standard library, so a CVR lookup only takes a few lines. You don't need any gems or an API key.",
            "blocks": [
                ("h2", "Look up a company by CVR number"),
                ("code", "ruby", _RUBY_LOOKUP),
                ("h2", "Search by company name"),
                ("p", "Fuzzy search finds companies even when the name is slightly misspelled. Each hit has <code>name</code>, <code>cvr_number</code>, <code>industrycode</code> and <code>industrytext</code>."),
                ("code", "ruby", _RUBY_SEARCH),
                ("h2", "In a Rails app"),
                ("p", "Company data rarely changes. Put the lookup in a service and cache the response, so the same CVR number isn't looked up on every request:"),
                ("code", "ruby", _RUBY_RAILS),
                ("h2", "Handle errors"),
                _errors_table("en"),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Can I use Faraday or HTTParty?", "Yes. The API is a plain GET request that returns JSON, so any HTTP client works. The examples use Net::HTTP because it needs no gems."),
                ("Do I need an API key?", "No. CVR-API needs no key and no account."),
            ],
        },
    },
    {
        "id": "excel",
        "family": "language",
        "slug": {"da": "cvr-opslag-excel", "en": "cvr-lookup-excel"},
        "related": ["google-sheets", "zapier-make", "company-types"],
        "da": {
            "title": "CVR-opslag i Excel med Power Query – uden makroer",
            "description": "Hent virksomhedsdata fra CVR direkte ind i Excel med Power Query. Slå navn, adresse, branche og ejere op ud fra en liste af CVR-numre uden VBA.",
            "h1": "CVR-opslag i Excel med Power Query",
            "lead": "Med Power Query kan Excel hente data fra CVR-API uden makroer eller VBA. Du kan slå en enkelt virksomhed op eller berige en hel liste af CVR-numre med navn, by og branche.",
            "blocks": [
                ("h2", "Hent én virksomhed"),
                ("ol", [
                    "Gå til <strong>Data</strong> &gt; <strong>Hent data</strong> &gt; <strong>Fra andre kilder</strong> &gt; <strong>Tom forespørgsel</strong>.",
                    "Åbn <strong>Avanceret editor</strong>, og indsæt koden nedenfor.",
                    "Klik <strong>Luk og indlæs</strong>. Virksomheden lander som en tabel i dit ark.",
                ]),
                ("code", "powerquery", _PQ_LOOKUP),
                ("h2", "Berig en liste af CVR-numre"),
                ("p", "Opret en ny tom forespørgsel med funktionen herunder, og kald den <code>HentCVR</code>. Den tager et CVR-nummer som tekst og returnerer navn, by, branche og reklamebeskyttelse."),
                ("code", "powerquery", _PQ_FUNCTION),
                ("ol", [
                    "Indlæs din tabel med CVR-numre i Power Query, og sørg for, at kolonnen har typen <strong>Tekst</strong>.",
                    "Vælg <strong>Tilføj kolonne</strong> &gt; <strong>Aktivér brugerdefineret funktion</strong>, og vælg <code>HentCVR</code>.",
                    "Klik på udvid-ikonet i den nye kolonne, og vælg de felter, du vil have med.",
                ]),
                ("note", "Excel spørger måske om adgang til <code>{site}</code> første gang. Vælg <strong>Anonym</strong> adgang. API'et kræver ingen login."),
                ("h2", "Hent ejerne som en tabel"),
                ("code", "powerquery", _PQ_OWNERS),
                ("h2", "Opdatering og store lister"),
                ("p", "Klik <strong>Opdater alle</strong> for at hente friske data. Hver række er ét kald, så hold lister under et par tusinde rækker pr. opdatering."),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Virker det i Excel til Mac?", "Ja, Power Query er med i nyere versioner af Excel til Mac (Microsoft 365). Menuerne hedder det samme."),
                ("Kræver det VBA eller makroer?", "Nej. Power Query er indbygget i Excel, og filen kan gemmes som almindelig .xlsx."),
                ("Hvorfor skal CVR-kolonnen være tekst?", "Funktionen bygger URL'en ud fra teksten. Er kolonnen et tal, så konvertér den med <code>Text.From</code> eller skift typen til Tekst."),
            ],
        },
        "en": {
            "title": "CVR lookup in Excel with Power Query – no macros",
            "description": "Pull Danish company data from CVR straight into Excel with Power Query. Enrich a list of CVR numbers with name, address, industry and owners, no VBA.",
            "h1": "CVR lookups in Excel with Power Query",
            "lead": "With Power Query, Excel can fetch data from CVR-API without macros or VBA. You can look up a single company or enrich a whole list of CVR numbers with name, city and industry.",
            "blocks": [
                ("h2", "Fetch one company"),
                ("ol", [
                    "Go to <strong>Data</strong> &gt; <strong>Get Data</strong> &gt; <strong>From Other Sources</strong> &gt; <strong>Blank Query</strong>.",
                    "Open the <strong>Advanced Editor</strong> and paste the code below.",
                    "Click <strong>Close &amp; Load</strong>. The company lands as a table in your sheet.",
                ]),
                ("code", "powerquery", _PQ_LOOKUP),
                ("h2", "Enrich a list of CVR numbers"),
                ("p", "Create a new blank query with the function below and name it <code>GetCVR</code>. It takes a CVR number as text and returns name, city, industry and marketing protection."),
                ("code", "powerquery", _PQ_FUNCTION),
                ("ol", [
                    "Load your table of CVR numbers into Power Query and make sure the column type is <strong>Text</strong>.",
                    "Choose <strong>Add Column</strong> &gt; <strong>Invoke Custom Function</strong> and pick <code>GetCVR</code>.",
                    "Click the expand icon on the new column and pick the fields you want.",
                ]),
                ("note", "Excel may ask how to access <code>{site}</code> the first time. Choose <strong>Anonymous</strong>. The API needs no login."),
                ("h2", "Fetch the owners as a table"),
                ("code", "powerquery", _PQ_OWNERS),
                ("h2", "Refreshing and large lists"),
                ("p", "Click <strong>Refresh All</strong> to fetch fresh data. Each row is one request, so keep lists under a few thousand rows per refresh."),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Does it work in Excel for Mac?", "Yes, Power Query is included in recent versions of Excel for Mac (Microsoft 365). The menus have the same names."),
                ("Does it need VBA or macros?", "No. Power Query is built into Excel, and the file can be saved as a regular .xlsx."),
                ("Why does the CVR column have to be text?", "The function builds the URL from the text. If the column is a number, convert it with <code>Text.From</code> or change the type to Text."),
            ],
        },
    },
    {
        "id": "google-sheets",
        "family": "language",
        "slug": {"da": "cvr-opslag-google-sheets", "en": "cvr-lookup-google-sheets"},
        "related": ["excel", "zapier-make", "validate-cvr"],
        "da": {
            "title": "CVR-opslag i Google Sheets – egen =CVR()-formel",
            "description": "Lav din egen =CVR()-formel i Google Sheets med Apps Script. Slå navn, adresse og branche op ud fra et CVR-nummer direkte i regnearket.",
            "h1": "CVR-opslag i Google Sheets",
            "lead": "Med et lille Apps Script får du en =CVR()-formel i Google Sheets, der henter navn, by, branche og meget mere direkte fra CVR-registret.",
            "blocks": [
                ("h2", "Opret formlen"),
                ("ol", [
                    "Åbn dit regneark, og vælg <strong>Udvidelser</strong> &gt; <strong>Apps Script</strong>.",
                    "Slet indholdet i <code>Code.gs</code>, og indsæt scriptet nedenfor.",
                    "Gem projektet. Formlen er nu klar i regnearket.",
                ]),
                ("code", "javascript", _GS_SCRIPT),
                ("h2", "Brug formlen"),
                ("p", "Står CVR-nummeret i A2, kan du skrive:"),
                ("ul", [
                    "<code>=CVR(A2; \"name\")</code> giver virksomhedens navn",
                    "<code>=CVR(A2; \"city\")</code> giver byen",
                    "<code>=CVR(A2; \"industrydesc\")</code> giver branchen",
                    "<code>=CVR(A2; \"protected\")</code> viser, om virksomheden er reklamebeskyttet",
                    "<code>=CVR(A2; \"ejere\")</code> giver ejernes navne adskilt af komma",
                ]),
                ("p", "Bruger dit regneark engelske indstillinger, skal du adskille argumenterne med komma: <code>=CVR(A2, \"name\")</code>."),
                ("note", "Scriptet gemmer svar i 6 timer med <code>CacheService</code>, så flere kolonner med samme CVR-nummer kun giver ét kald."),
                ("h2", "Søg på navn"),
                ("p", "Tilføj denne funktion for at få en liste over hits med CVR-nummer, navn og branche. Resultatet fylder flere rækker og kolonner."),
                ("code", "javascript", _GS_SEARCH),
                ("note", _PROTECTED_DA),
            ],
            "faq": [
                ("Hvorfor viser cellen \"Ikke fundet\"?", "CVR-nummeret findes ikke i registret. Tjek at det har 8 cifre og ikke er formateret som et tal med tusindtalsseparator."),
                ("Er der en grænse for, hvor mange rækker jeg kan slå op?", "Google begrænser, hvor mange URL-kald et script må lave pr. dag. Cachen hjælper, men del store lister op over flere dage."),
            ],
        },
        "en": {
            "title": "CVR lookup in Google Sheets – your own =CVR() formula",
            "description": "Build a =CVR() formula in Google Sheets with Apps Script. Look up a Danish company's name, address and industry from its CVR number in your sheet.",
            "h1": "CVR lookups in Google Sheets",
            "lead": "A small Apps Script gives you a =CVR() formula in Google Sheets that pulls name, city, industry and more straight from the Danish CVR register.",
            "blocks": [
                ("h2", "Create the formula"),
                ("ol", [
                    "Open your spreadsheet and choose <strong>Extensions</strong> &gt; <strong>Apps Script</strong>.",
                    "Delete the contents of <code>Code.gs</code> and paste the script below.",
                    "Save the project. The formula is now available in the sheet.",
                ]),
                ("code", "javascript", _GS_SCRIPT),
                ("h2", "Use the formula"),
                ("p", "With the CVR number in A2, you can write:"),
                ("ul", [
                    "<code>=CVR(A2, \"name\")</code> returns the company name",
                    "<code>=CVR(A2, \"city\")</code> returns the city",
                    "<code>=CVR(A2, \"industrydesc\")</code> returns the industry (in Danish)",
                    "<code>=CVR(A2, \"protected\")</code> shows whether the company has marketing protection",
                    "<code>=CVR(A2, \"ejere\")</code> returns the owners' names, comma-separated",
                ]),
                ("p", "If your spreadsheet uses Danish locale settings, separate the arguments with a semicolon: <code>=CVR(A2; \"name\")</code>."),
                ("note", "The script caches responses for 6 hours with <code>CacheService</code>, so several columns with the same CVR number only make one request."),
                ("h2", "Search by name"),
                ("p", "Add this function to get a list of hits with CVR number, name and industry. The result spills over several rows and columns."),
                ("code", "javascript", _GS_SEARCH),
                ("note", _PROTECTED_EN),
            ],
            "faq": [
                ("Why does the cell say \"Ikke fundet\"?", "That means not found: the CVR number isn't in the register. Check that it has 8 digits and isn't formatted as a number with thousands separators."),
                ("Is there a limit on how many rows I can look up?", "Google limits how many URL fetches a script can make per day. The cache helps, but spread very large lists over several days."),
            ],
        },
    },
]
