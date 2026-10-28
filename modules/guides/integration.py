"""Integration guides: autofill and enrich company data in common platforms."""

# --- WooCommerce -------------------------------------------------------------

_WOO_FIELD_PHP = {
    "da": """\
<?php
// functions.php i dit (child-)tema eller et lille plugin
add_filter( 'woocommerce_checkout_fields', function ( $fields ) {
    $fields['billing']['billing_cvr'] = array(
        'type'      => 'text',
        'label'     => 'CVR-nummer',
        'required'  => false,
        'class'     => array( 'form-row-wide' ),
        'priority'  => 25, // lige efter firmanavn
        'maxlength' => 8,
    );
    return $fields;
} );

add_action( 'wp_enqueue_scripts', function () {
    if ( ! is_checkout() ) {
        return;
    }
    wp_enqueue_script(
        'cvr-autofill',
        get_stylesheet_directory_uri() . '/cvr-autofill.js',
        array(),
        '1.0',
        true
    );
} );
""",
    "en": """\
<?php
// functions.php in your (child) theme, or a small plugin
add_filter( 'woocommerce_checkout_fields', function ( $fields ) {
    $fields['billing']['billing_cvr'] = array(
        'type'      => 'text',
        'label'     => 'CVR number',
        'required'  => false,
        'class'     => array( 'form-row-wide' ),
        'priority'  => 25, // right after company name
        'maxlength' => 8,
    );
    return $fields;
} );

add_action( 'wp_enqueue_scripts', function () {
    if ( ! is_checkout() ) {
        return;
    }
    wp_enqueue_script(
        'cvr-autofill',
        get_stylesheet_directory_uri() . '/cvr-autofill.js',
        array(),
        '1.0',
        true
    );
} );
""",
}

_WOO_JS = """\
// cvr-autofill.js
document.addEventListener('DOMContentLoaded', () => {
  const cvrInput = document.getElementById('billing_cvr');
  if (!cvrInput) return;

  const setField = (id, value) => {
    const el = document.getElementById(id);
    if (!el || value === null || value === undefined) return;
    el.value = value;
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  cvrInput.addEventListener('input', async () => {
    const cvr = cvrInput.value.replace(/\\D/g, '');
    if (cvr.length !== 8) return;

    try {
      const res = await fetch(`{site}/api/v1/${cvr}`);
      if (!res.ok) return; // 404 = unknown CVR number
      const company = await res.json();

      setField('billing_company', company.name);
      setField('billing_address_1', company.address);
      setField('billing_postcode', company.zipcode);
      setField('billing_city', company.city);
    } catch (err) {
      // Network error: let the customer fill in the fields by hand.
    }
  });
});
"""

_WOO_VALIDATE_PHP = {
    "da": """\
<?php
add_action( 'woocommerce_checkout_process', function () {
    $cvr = isset( $_POST['billing_cvr'] )
        ? preg_replace( '/\\D/', '', wp_unslash( $_POST['billing_cvr'] ) )
        : '';
    if ( '' === $cvr ) {
        return; // feltet er valgfrit
    }
    if ( 8 !== strlen( $cvr ) ) {
        wc_add_notice( 'CVR-nummeret skal bestå af 8 cifre.', 'error' );
        return;
    }

    $response = wp_remote_get( '{site}/api/v1/' . $cvr, array( 'timeout' => 10 ) );
    if ( is_wp_error( $response ) ) {
        return; // bloker ikke checkout, hvis API'et ikke svarer
    }
    if ( 404 === wp_remote_retrieve_response_code( $response ) ) {
        wc_add_notice( 'Vi kunne ikke finde CVR-nummeret i CVR-registret.', 'error' );
    }
} );
""",
    "en": """\
<?php
add_action( 'woocommerce_checkout_process', function () {
    $cvr = isset( $_POST['billing_cvr'] )
        ? preg_replace( '/\\D/', '', wp_unslash( $_POST['billing_cvr'] ) )
        : '';
    if ( '' === $cvr ) {
        return; // the field is optional
    }
    if ( 8 !== strlen( $cvr ) ) {
        wc_add_notice( 'The CVR number must be 8 digits.', 'error' );
        return;
    }

    $response = wp_remote_get( '{site}/api/v1/' . $cvr, array( 'timeout' => 10 ) );
    if ( is_wp_error( $response ) ) {
        return; // don't block checkout if the API is unreachable
    }
    if ( 404 === wp_remote_retrieve_response_code( $response ) ) {
        wc_add_notice( 'We could not find that CVR number in the CVR register.', 'error' );
    }
} );
""",
}

# --- Shopify -----------------------------------------------------------------

_SHOPIFY_LIQUID = {
    "da": """\
{%- comment -%} I cart-sektionen, fx sections/main-cart-footer.liquid {%- endcomment -%}
<div class="cart-attribute">
  <label for="cvr-number">CVR-nummer</label>
  <input id="cvr-number" type="text" inputmode="numeric" maxlength="8"
         name="attributes[CVR]" form="cart"
         value="{{ cart.attributes.CVR }}">
</div>
<div class="cart-attribute">
  <label for="cvr-company">Firmanavn</label>
  <input id="cvr-company" type="text"
         name="attributes[Firmanavn]" form="cart"
         value="{{ cart.attributes.Firmanavn }}">
</div>
<p id="cvr-status" aria-live="polite"></p>
""",
    "en": """\
{%- comment -%} In the cart section, e.g. sections/main-cart-footer.liquid {%- endcomment -%}
<div class="cart-attribute">
  <label for="cvr-number">CVR number</label>
  <input id="cvr-number" type="text" inputmode="numeric" maxlength="8"
         name="attributes[CVR]" form="cart"
         value="{{ cart.attributes.CVR }}">
</div>
<div class="cart-attribute">
  <label for="cvr-company">Company name</label>
  <input id="cvr-company" type="text"
         name="attributes[Company]" form="cart"
         value="{{ cart.attributes.Company }}">
</div>
<p id="cvr-status" aria-live="polite"></p>
""",
}

_SHOPIFY_JS = """\
// assets/cvr-lookup.js, loaded on the cart page
const cvrInput = document.getElementById('cvr-number');
const companyInput = document.getElementById('cvr-company');
const status = document.getElementById('cvr-status');

cvrInput?.addEventListener('input', async () => {
  const cvr = cvrInput.value.replace(/\\D/g, '');
  status.textContent = '';
  if (cvr.length !== 8) return;

  try {
    const res = await fetch(`{site}/api/v1/${cvr}`);
    if (!res.ok) {
      status.textContent = 'CVR not found';
      return;
    }
    const company = await res.json();
    companyInput.value = company.name;
    status.textContent = `${company.name}, ${company.address}, ${company.zipcode} ${company.city}`;
  } catch (err) {
    // Leave the fields for the customer to fill in.
  }
});
"""

_SHOPIFY_REGISTER = {
    "da": """\
{%- comment -%} I kunderegistreringsformularen (customers/register) {%- endcomment -%}
<label for="RegisterForm-CVR">CVR-nummer</label>
<input id="RegisterForm-CVR" type="text" inputmode="numeric" maxlength="8"
       name="customer[note][CVR]">
""",
    "en": """\
{%- comment -%} Inside the customer registration form (customers/register) {%- endcomment -%}
<label for="RegisterForm-CVR">CVR number</label>
<input id="RegisterForm-CVR" type="text" inputmode="numeric" maxlength="8"
       name="customer[note][CVR]">
""",
}

# --- React -------------------------------------------------------------------

_REACT_AUTOCOMPLETE = """\
import { useEffect, useState } from "react";

const API = "{site}/api/v1";

export function CompanyAutocomplete({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API}/search/fuzzy/${encodeURIComponent(q)}`, {
          signal: controller.signal,
        });
        if (res.ok) setResults((await res.json()).slice(0, 8));
      } catch (err) {
        if (err.name !== "AbortError") setResults([]);
      }
    }, 300); // debounce: wait until the user pauses typing

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  return (
    <div className="company-autocomplete">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Company name"
        autoComplete="off"
      />
      {results.length > 0 && (
        <ul role="listbox">
          {results.map((c) => (
            <li key={c.cvr_number} role="option" aria-selected="false">
              <button type="button" onClick={() => { onSelect(c.cvr_number); setResults([]); }}>
                {c.name} <small>CVR {c.cvr_number} · {c.industrytext}</small>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
"""

_REACT_FORM = """\
import { useState } from "react";
import { CompanyAutocomplete } from "./CompanyAutocomplete";

const API = "{site}/api/v1";
const EMPTY = { cvr: "", name: "", address: "", zipcode: "", city: "" };

export function CompanyForm() {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);

  async function fillFromCvr(cvr) {
    setError(null);
    const res = await fetch(`${API}/${cvr}`);
    if (!res.ok) {
      setError(res.status === 404 ? "Unknown CVR number" : "Lookup failed");
      return;
    }
    const c = await res.json();
    setForm({
      cvr: String(c.vat),
      name: c.name ?? "",
      address: c.address ?? "",
      zipcode: c.zipcode ? String(c.zipcode) : "",
      city: c.city ?? "",
    });
  }

  const field = (key) => ({
    value: form[key],
    onChange: (e) => {
      const value = e.target.value;
      setForm((f) => ({ ...f, [key]: value }));
      if (key === "cvr" && /^\\d{8}$/.test(value)) fillFromCvr(value);
    },
  });

  return (
    <form>
      <CompanyAutocomplete onSelect={fillFromCvr} />
      <input {...field("cvr")} placeholder="CVR" inputMode="numeric" maxLength={8} />
      <input {...field("name")} placeholder="Name" />
      <input {...field("address")} placeholder="Address" />
      <input {...field("zipcode")} placeholder="Postcode" />
      <input {...field("city")} placeholder="City" />
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
"""

# --- Zapier / Make / n8n -----------------------------------------------------

_ZAPIER_CONFIG = """\
Action:  Webhooks by Zapier → GET
URL:     {site}/api/v1/[CVR field from your trigger]
Query String Params:  (empty)
Headers:              (empty, no API key needed)
"""

_MAKE_CONFIG = """\
Module:           HTTP → Make a request
URL:              {site}/api/v1/{{1.cvr}}
Method:           GET
Parse response:   Yes
"""

_N8N_CONFIG = """\
Node:            HTTP Request
Method:          GET
URL:             {site}/api/v1/{{ $json.cvr }}
Authentication:  None
Response Format: JSON
"""

_FUZZY_CONFIG = """\
GET {site}/api/v1/search/fuzzy/[company name]

→ [{ "name": "...", "cvr_number": 12345678, "industrycode": ..., "industrytext": "..." }, ...]
"""


PAGES = [
    {
        "id": "woocommerce",
        "family": "integration",
        "slug": {"da": "woocommerce-cvr-opslag", "en": "woocommerce-cvr-lookup"},
        "related": ["validate-cvr", "php", "javascript"],
        "da": {
            "title": "WooCommerce CVR-opslag: Autoudfyld firmadata i checkout",
            "description": (
                "Tilføj et CVR-felt til WooCommerce-checkout, og udfyld firmanavn og adresse automatisk "
                "med et gratis CVR API. Komplet PHP- og JavaScript-kode."
            ),
            "h1": "CVR-opslag i WooCommerce-checkout",
            "lead": (
                "B2B-kunder skal ikke taste firmanavn og adresse selv. Med et CVR-felt og ca. 30 linjer kode "
                "henter din WooCommerce-butik oplysningerne direkte fra CVR-registret, så snart kunden har "
                "skrevet 8 cifre."
            ),
            "blocks": [
                ("h2", "Sådan virker det"),
                ("ol", [
                    "Et nyt felt, <code>billing_cvr</code>, lægges ind i checkout under firmanavn.",
                    "Når kunden har tastet 8 cifre, kalder et lille script <code>{site}/api/v1/{cvr}</code>.",
                    "Firmanavn, adresse, postnummer og by udfyldes automatisk.",
                    "Valgfrit: CVR-nummeret valideres på serveren, før ordren oprettes.",
                ]),
                ("h2", "1. Tilføj CVR-feltet og scriptet"),
                ("p", "Læg koden i <code>functions.php</code> i dit child-tema eller i et lille plugin. "
                      "WooCommerce gemmer automatisk feltet på ordren som metafeltet <code>_billing_cvr</code>."),
                ("code", "php", _WOO_FIELD_PHP["da"]),
                ("h2", "2. Autoudfyld med JavaScript"),
                ("p", "Gem filen som <code>cvr-autofill.js</code> i dit child-tema. API'et sender "
                      "<code>Access-Control-Allow-Origin: *</code>, så kaldet kan laves direkte fra browseren "
                      "uden proxy og uden API-nøgle."),
                ("code", "javascript", _WOO_JS),
                ("h2", "3. Valider CVR-nummeret på serveren (valgfrit)"),
                ("p", "Browseren kan snydes, så validér også på serveren. Svarer API'et <code>404</code>, "
                      "findes CVR-nummeret ikke. Er API'et utilgængeligt, lader vi ordren gå igennem, så du "
                      "ikke mister salg."),
                ("code", "php", _WOO_VALIDATE_PHP["da"]),
                ("note", "Koden bruger den klassiske checkout (<code>[woocommerce_checkout]</code>). Bruger din "
                         "butik den nye blokbaserede checkout, virker filteret "
                         "<code>woocommerce_checkout_fields</code> ikke. Der skal du tilføje feltet via "
                         "WooCommerces Additional Checkout Fields API i stedet."),
                ("h2", "Husk reklamebeskyttelse"),
                ("p", "Gemmer du kundens firmadata til nyhedsbreve eller anden markedsføring, så tjek feltet "
                      "<code>protected</code>. Er det <code>true</code>, har virksomheden frabedt sig "
                      "reklamehenvendelser. Læs mere om <a href=\"/guides/reklamebeskyttelse\">reklamebeskyttelse</a>."),
            ],
            "faq": [
                ("Kræver det et plugin?",
                 "Nej. Koden ovenfor kan ligge i dit child-temas <code>functions.php</code>. Vil du kunne flytte "
                 "den mellem temaer, så pak den ind i et lille plugin."),
                ("Hvor bliver CVR-nummeret gemt?",
                 "WooCommerce gemmer felter fra <code>woocommerce_checkout_fields</code> som ordremeta. Du finder "
                 "det under metanøglen <code>_billing_cvr</code> på ordren."),
                ("Koster CVR-opslagene noget?",
                 "Nej. CVR-API er gratis og kræver ingen API-nøgle. Der gælder rimelige rate limits."),
            ],
        },
        "en": {
            "title": "WooCommerce CVR Lookup: Autofill Company Data at Checkout",
            "description": (
                "Add a CVR field to WooCommerce checkout and autofill company name and address with a free "
                "CVR API. Complete PHP and JavaScript code included."
            ),
            "h1": "CVR lookup in WooCommerce checkout",
            "lead": (
                "B2B customers shouldn't have to type their company name and address. With a CVR field and "
                "about 30 lines of code, your WooCommerce store fetches the details from the Danish CVR "
                "register as soon as the customer has typed 8 digits."
            ),
            "blocks": [
                ("h2", "How it works"),
                ("ol", [
                    "A new field, <code>billing_cvr</code>, is added to checkout below the company name.",
                    "Once the customer has typed 8 digits, a small script calls <code>{site}/api/v1/{cvr}</code>.",
                    "Company name, address, postcode and city are filled in automatically.",
                    "Optional: the CVR number is validated on the server before the order is created.",
                ]),
                ("h2", "1. Add the CVR field and the script"),
                ("p", "Put this in your child theme's <code>functions.php</code> or in a small plugin. "
                      "WooCommerce automatically saves the field on the order as the meta key "
                      "<code>_billing_cvr</code>."),
                ("code", "php", _WOO_FIELD_PHP["en"]),
                ("h2", "2. Autofill with JavaScript"),
                ("p", "Save this as <code>cvr-autofill.js</code> in your child theme. The API sends "
                      "<code>Access-Control-Allow-Origin: *</code>, so the request can run straight from the "
                      "browser with no proxy and no API key."),
                ("code", "javascript", _WOO_JS),
                ("h2", "3. Validate the CVR number on the server (optional)"),
                ("p", "The browser can be bypassed, so validate on the server too. A <code>404</code> from "
                      "the API means the CVR number doesn't exist. If the API is unreachable, the order goes "
                      "through anyway so you don't lose the sale."),
                ("code", "php", _WOO_VALIDATE_PHP["en"]),
                ("note", "This code targets the classic checkout (<code>[woocommerce_checkout]</code>). If your "
                         "store uses the new block-based checkout, the <code>woocommerce_checkout_fields</code> "
                         "filter has no effect; add the field with WooCommerce's Additional Checkout Fields API "
                         "instead."),
                ("h2", "Respect marketing protection"),
                ("p", "If you store customers' company data for newsletters or other marketing, check the "
                      "<code>protected</code> field. When it's <code>true</code>, the company has opted out of "
                      "marketing. Read more about <a href=\"/en/guides/marketing-protection-reklamebeskyttelse\">marketing "
                      "protection</a>."),
            ],
            "faq": [
                ("Do I need a plugin?",
                 "No. The code above can live in your child theme's <code>functions.php</code>. If you want it "
                 "to survive theme changes, wrap it in a small plugin."),
                ("Where is the CVR number stored?",
                 "WooCommerce saves fields added through <code>woocommerce_checkout_fields</code> as order meta, "
                 "under the key <code>_billing_cvr</code>."),
                ("Do the CVR lookups cost anything?",
                 "No. CVR-API is free and needs no API key. Fair-use rate limits apply."),
            ],
        },
    },
    {
        "id": "shopify",
        "family": "integration",
        "slug": {"da": "shopify-cvr-opslag", "en": "shopify-cvr-lookup"},
        "related": ["woocommerce", "javascript", "validate-cvr"],
        "da": {
            "title": "Shopify CVR-opslag: Firmadata i kurv og kundeoprettelse",
            "description": (
                "Sådan henter du firmanavn og adresse fra CVR-registret i din Shopify-butik. Ærlig guide til, "
                "hvad der kan lade sig gøre i kurv, kundeoprettelse og checkout."
            ),
            "h1": "CVR-opslag i Shopify",
            "lead": (
                "Shopify lader dig ikke frit tilføje felter til checkout, så CVR-opslaget skal ligge et andet "
                "sted. Den nemmeste løsning er et CVR-felt i kurven, som slår virksomheden op og sender data "
                "med ordren som kurv-attributter."
            ),
            "blocks": [
                ("h2", "Hvad kan lade sig gøre?"),
                ("table", ["Sted", "Muligt?", "Hvordan"], [
                    ["Kurv", "Ja, alle planer", "Kurv-attributter + lidt JavaScript i temaet"],
                    ["Kundeoprettelse", "Ja, alle planer", "Ekstra felt i registreringsformularen"],
                    ["Checkout", "Begrænset", "Checkout UI extensions, primært på Shopify Plus"],
                ]),
                ("h2", "1. CVR-felt i kurven"),
                ("p", "Læg felterne ind i din kurv-sektion. Attributten <code>form=\"cart\"</code> knytter dem "
                      "til kurvformularen (i Dawn-temaet har den id'et <code>cart</code>). Alt med navnet "
                      "<code>attributes[...]</code> følger med ordren og vises i admin under "
                      "<em>Yderligere oplysninger</em>."),
                ("code", "liquid", _SHOPIFY_LIQUID["da"]),
                ("h2", "2. Slå virksomheden op med JavaScript"),
                ("p", "API'et tillader kald fra alle domæner (CORS), så scriptet kan kalde det direkte fra "
                      "butikken uden en app eller proxy."),
                ("code", "javascript", _SHOPIFY_JS),
                ("h2", "3. CVR ved kundeoprettelse"),
                ("p", "Har du B2B-kunder med konto, kan du også spørge efter CVR-nummeret ved oprettelse. "
                      "Felter med navnet <code>customer[note][...]</code> gemmes i kundens note."),
                ("code", "liquid", _SHOPIFY_REGISTER["da"]),
                ("note", "Selve checkout kan kun udvides med Checkout UI extensions, og for informations-, "
                         "leverings- og betalingstrinnet kræver det som udgangspunkt Shopify Plus. Extensions skal "
                         "have netværksadgang slået til for at kunne kalde et eksternt API."),
                ("h2", "Husk reklamebeskyttelse"),
                ("p", "Bruger du firmadata fra kunderne til markedsføring, så tjek feltet <code>protected</code> "
                      "i API-svaret. Se <a href=\"/guides/reklamebeskyttelse\">reklamebeskyttelse</a>."),
            ],
            "faq": [
                ("Skal jeg installere en app?",
                 "Nej. Kurv-felterne og scriptet ligger direkte i dit tema, og API'et kræver ingen nøgle."),
                ("Hvor finder jeg CVR-nummeret på ordren?",
                 "Kurv-attributter vises på ordren i Shopify admin under Yderligere oplysninger og følger med i "
                 "ordre-webhooks og API'et som <code>note_attributes</code>."),
                ("Kan jeg tilføje CVR-feltet i selve checkout?",
                 "Kun med Checkout UI extensions, som til informations- og betalingstrinnet som udgangspunkt "
                 "kræver Shopify Plus."),
            ],
        },
        "en": {
            "title": "Shopify CVR Lookup: Company Data in Cart and Sign-up",
            "description": (
                "How to fetch company name and address from the Danish CVR register in your Shopify store. "
                "An honest guide to what's possible in cart, sign-up and checkout."
            ),
            "h1": "CVR lookup in Shopify",
            "lead": (
                "Shopify doesn't let you freely add fields to checkout, so the CVR lookup has to live "
                "somewhere else. The simplest option is a CVR field in the cart that looks up the company "
                "and sends the data along with the order as cart attributes."
            ),
            "blocks": [
                ("h2", "What's possible?"),
                ("table", ["Where", "Possible?", "How"], [
                    ["Cart", "Yes, all plans", "Cart attributes + a little theme JavaScript"],
                    ["Customer sign-up", "Yes, all plans", "Extra field in the registration form"],
                    ["Checkout", "Limited", "Checkout UI extensions, mainly on Shopify Plus"],
                ]),
                ("h2", "1. CVR field in the cart"),
                ("p", "Add the fields to your cart section. The <code>form=\"cart\"</code> attribute ties them to "
                      "the cart form (in the Dawn theme its id is <code>cart</code>). Anything named "
                      "<code>attributes[...]</code> is saved with the order and shown in admin under "
                      "<em>Additional details</em>."),
                ("code", "liquid", _SHOPIFY_LIQUID["en"]),
                ("h2", "2. Look up the company with JavaScript"),
                ("p", "The API allows requests from any origin (CORS), so the script can call it straight from "
                      "your storefront without an app or a proxy."),
                ("code", "javascript", _SHOPIFY_JS),
                ("h2", "3. CVR at customer sign-up"),
                ("p", "If your B2B customers create accounts, you can ask for the CVR number at sign-up too. "
                      "Fields named <code>customer[note][...]</code> are saved to the customer's note."),
                ("code", "liquid", _SHOPIFY_REGISTER["en"]),
                ("note", "Checkout itself can only be extended with Checkout UI extensions, and for the "
                         "information, shipping and payment steps that generally requires Shopify Plus. "
                         "Extensions also need network access enabled to call an external API."),
                ("h2", "Respect marketing protection"),
                ("p", "If you use customers' company data for marketing, check the <code>protected</code> field "
                      "in the API response. See <a href=\"/en/guides/marketing-protection-reklamebeskyttelse\">marketing "
                      "protection</a>."),
            ],
            "faq": [
                ("Do I need to install an app?",
                 "No. The cart fields and the script live in your theme, and the API needs no key."),
                ("Where do I find the CVR number on the order?",
                 "Cart attributes appear on the order in Shopify admin under Additional details, and in order "
                 "webhooks and the API as <code>note_attributes</code>."),
                ("Can I add the CVR field to checkout itself?",
                 "Only with Checkout UI extensions, which for the information and payment steps generally "
                 "require Shopify Plus."),
            ],
        },
    },
    {
        "id": "react-form",
        "family": "integration",
        "slug": {"da": "react-cvr-autocomplete", "en": "react-cvr-autocomplete"},
        "related": ["javascript", "validate-cvr", "woocommerce"],
        "da": {
            "title": "React CVR-autocomplete: Søg og udfyld firmadata",
            "description": (
                "Byg en React-formular med autocomplete på firmanavn og automatisk udfyldning fra "
                "CVR-nummer. Gratis CVR API, ingen API-nøgle, komplet kode."
            ),
            "h1": "CVR-autocomplete i React",
            "lead": (
                "Lad brugeren skrive et par bogstaver af firmanavnet, vælge virksomheden på en liste og få "
                "CVR-nummer, adresse og by udfyldt automatisk. To små komponenter og ingen ekstra "
                "afhængigheder."
            ),
            "blocks": [
                ("h2", "De to endpoints"),
                ("ul", [
                    "<code>{site}/api/v1/search/fuzzy/{navn}</code> finder virksomheder, selv med stavefejl. "
                    "Perfekt til autocomplete.",
                    "<code>{site}/api/v1/{cvr}</code> henter den fulde profil, når brugeren har valgt en "
                    "virksomhed eller tastet et CVR-nummer.",
                ]),
                ("code", "text", _FUZZY_CONFIG),
                ("h2", "1. Autocomplete-komponenten"),
                ("p", "Komponenten venter 300 ms efter sidste tastetryk (debounce) og afbryder gamle kald med "
                      "<code>AbortController</code>, så svarene aldrig kommer i forkert rækkefølge."),
                ("code", "jsx", _REACT_AUTOCOMPLETE),
                ("h2", "2. Formularen der udfyldes"),
                ("p", "Formularen slår virksomheden op, når brugeren vælger i listen, eller når CVR-feltet "
                      "indeholder 8 cifre."),
                ("code", "jsx", _REACT_FORM),
                ("note", "API'et sender <code>Access-Control-Allow-Origin: *</code>, så du kan kalde det direkte "
                         "fra browseren i Vite, Next.js, Create React App og lignende, uden proxy og uden nøgle."),
                ("h2", "Gemmer du data til markedsføring?"),
                ("p", "Så tjek feltet <code>protected</code> i det fulde opslag. Se "
                      "<a href=\"/guides/reklamebeskyttelse\">reklamebeskyttelse</a>."),
            ],
            "faq": [
                ("Virker det med Next.js?",
                 "Ja. Komponenterne er almindelige klientkomponenter. I Next.js App Router skal filen starte "
                 "med <code>\"use client\"</code>."),
                ("Hvor mange kald må jeg lave?",
                 "Der gælder rimelige rate limits. Med debounce på 300 ms laver autocomplete kun ét kald, når "
                 "brugeren holder pause."),
            ],
        },
        "en": {
            "title": "React CVR Autocomplete: Search and Autofill Company Data",
            "description": (
                "Build a React form with company-name autocomplete and autofill from the CVR number. Free "
                "CVR API, no API key, complete code."
            ),
            "h1": "CVR autocomplete in React",
            "lead": (
                "Let users type a few letters of a company name, pick the company from a list, and get the "
                "CVR number, address and city filled in automatically. Two small components and no extra "
                "dependencies."
            ),
            "blocks": [
                ("h2", "The two endpoints"),
                ("ul", [
                    "<code>{site}/api/v1/search/fuzzy/{name}</code> finds companies even with typos. Perfect "
                    "for autocomplete.",
                    "<code>{site}/api/v1/{cvr}</code> fetches the full profile once the user has picked a "
                    "company or typed a CVR number.",
                ]),
                ("code", "text", _FUZZY_CONFIG),
                ("h2", "1. The autocomplete component"),
                ("p", "The component waits 300 ms after the last keystroke (debounce) and cancels stale requests "
                      "with <code>AbortController</code>, so responses never arrive out of order."),
                ("code", "jsx", _REACT_AUTOCOMPLETE),
                ("h2", "2. The form that gets filled in"),
                ("p", "The form looks up the company when the user picks from the list, or when the CVR field "
                      "contains 8 digits."),
                ("code", "jsx", _REACT_FORM),
                ("note", "The API sends <code>Access-Control-Allow-Origin: *</code>, so you can call it straight "
                         "from the browser in Vite, Next.js, Create React App and similar, with no proxy and no key."),
                ("h2", "Storing data for marketing?"),
                ("p", "Then check the <code>protected</code> field in the full lookup. See "
                      "<a href=\"/en/guides/marketing-protection-reklamebeskyttelse\">marketing protection</a>."),
            ],
            "faq": [
                ("Does it work with Next.js?",
                 "Yes. The components are ordinary client components. In the Next.js App Router, start the file "
                 "with <code>\"use client\"</code>."),
                ("How many requests can I make?",
                 "Fair-use rate limits apply. With a 300 ms debounce, the autocomplete only sends one request "
                 "when the user pauses typing."),
            ],
        },
    },
    {
        "id": "zapier-make",
        "family": "integration",
        "slug": {"da": "zapier-make-cvr-opslag", "en": "zapier-make-cvr-lookup"},
        "related": ["google-sheets", "excel", "validate-cvr"],
        "da": {
            "title": "CVR-opslag i Zapier, Make og n8n uden kode",
            "description": (
                "Berig leads og kunder med firmadata fra CVR-registret i Zapier, Make eller n8n. Ét HTTP-trin, "
                "ingen API-nøgle og ingen kode."
            ),
            "h1": "CVR-opslag i Zapier, Make og n8n",
            "lead": (
                "Har du et CVR-nummer i en formular, et CRM eller et regneark, kan du hente firmanavn, adresse "
                "og branche med ét HTTP-trin i dit automationsværktøj. Det kræver hverken kode eller API-nøgle."
            ),
            "blocks": [
                ("h2", "Zapier: Webhooks by Zapier"),
                ("ol", [
                    "Tilføj et action-trin og vælg <strong>Webhooks by Zapier</strong> → <strong>GET</strong>.",
                    "Skriv <code>{site}/api/v1/</code> i URL-feltet, og indsæt CVR-feltet fra dit trigger-trin "
                    "lige efter.",
                    "Lad Query String Params og Headers være tomme.",
                    "Test trinnet. Felter som <code>name</code>, <code>address</code>, <code>city</code> og "
                    "<code>industrydesc</code> kan nu bruges i de næste trin.",
                ]),
                ("code", "text", _ZAPIER_CONFIG),
                ("note", "<em>Webhooks by Zapier</em> kræver et betalt Zapier-abonnement."),
                ("h2", "Make: HTTP → Make a request"),
                ("p", "Tilføj modulet <strong>HTTP → Make a request</strong>, og map CVR-nummeret fra det "
                      "foregående modul ind i URL'en. Slå <em>Parse response</em> til, så Make deler JSON-svaret "
                      "op i felter, du kan mappe videre."),
                ("code", "text", _MAKE_CONFIG),
                ("h2", "n8n: HTTP Request"),
                ("p", "I n8n bruger du noden <strong>HTTP Request</strong> med et udtryk i URL'en:"),
                ("code", "text", _N8N_CONFIG),
                ("h2", "Felter du typisk mapper"),
                ("table", ["Felt", "Indhold"], [
                    ["<code>name</code>", "Firmanavn"],
                    ["<code>address</code>, <code>zipcode</code>, <code>city</code>", "Adresse"],
                    ["<code>industrydesc</code>", "Branche"],
                    ["<code>companydesc</code>", "Virksomhedsform, fx Anpartsselskab"],
                    ["<code>status</code>", "Status, fx NORMAL"],
                    ["<code>protected</code>", "<code>true</code> hvis virksomheden er reklamebeskyttet"],
                ]),
                ("h2", "Husk reklamebeskyttelse"),
                ("p", "Sender du berigede leads videre til e-mail-marketing eller telefonsalg, så filtrér "
                      "virksomheder med <code>protected = true</code> fra. Se "
                      "<a href=\"/guides/reklamebeskyttelse\">reklamebeskyttelse</a>."),
            ],
            "faq": [
                ("Skal jeg bruge en API-nøgle?",
                 "Nej. Lad headers og autentificering være tomme."),
                ("Kan jeg berige tusindvis af rækker på én gang?",
                 "API'et har rimelige rate limits, så kør store mængder i roligt tempo. Har du brug for "
                 "vedvarende høj trafik, så skriv til noah@noahbohme.com."),
                ("Hvad hvis CVR-nummeret ikke findes?",
                 "API'et svarer med HTTP 404. I Zapier og Make kan du fange fejlen med et filter eller en "
                 "error handler, så resten af flowet fortsætter."),
            ],
        },
        "en": {
            "title": "CVR Lookup in Zapier, Make and n8n, No Code",
            "description": (
                "Enrich leads and customers with company data from the Danish CVR register in Zapier, Make or "
                "n8n. One HTTP step, no API key, no code."
            ),
            "h1": "CVR lookup in Zapier, Make and n8n",
            "lead": (
                "If you have a CVR number in a form, a CRM or a spreadsheet, you can fetch company name, "
                "address and industry with a single HTTP step in your automation tool. No code and no API key "
                "needed."
            ),
            "blocks": [
                ("h2", "Zapier: Webhooks by Zapier"),
                ("ol", [
                    "Add an action step and choose <strong>Webhooks by Zapier</strong> → <strong>GET</strong>.",
                    "Type <code>{site}/api/v1/</code> in the URL field and insert the CVR field from your "
                    "trigger right after it.",
                    "Leave Query String Params and Headers empty.",
                    "Test the step. Fields like <code>name</code>, <code>address</code>, <code>city</code> and "
                    "<code>industrydesc</code> are now available in later steps.",
                ]),
                ("code", "text", _ZAPIER_CONFIG),
                ("note", "<em>Webhooks by Zapier</em> requires a paid Zapier plan."),
                ("h2", "Make: HTTP → Make a request"),
                ("p", "Add the <strong>HTTP → Make a request</strong> module and map the CVR number from the "
                      "previous module into the URL. Turn on <em>Parse response</em> so Make splits the JSON "
                      "response into fields you can map onward."),
                ("code", "text", _MAKE_CONFIG),
                ("h2", "n8n: HTTP Request"),
                ("p", "In n8n, use the <strong>HTTP Request</strong> node with an expression in the URL:"),
                ("code", "text", _N8N_CONFIG),
                ("h2", "Fields you'll typically map"),
                ("table", ["Field", "Contents"], [
                    ["<code>name</code>", "Company name"],
                    ["<code>address</code>, <code>zipcode</code>, <code>city</code>", "Address"],
                    ["<code>industrydesc</code>", "Industry (in Danish)"],
                    ["<code>companydesc</code>", "Company type, e.g. Anpartsselskab"],
                    ["<code>status</code>", "Status, e.g. NORMAL"],
                    ["<code>protected</code>", "<code>true</code> if the company has marketing protection"],
                ]),
                ("h2", "Respect marketing protection"),
                ("p", "If you pass enriched leads on to email marketing or cold calling, filter out companies "
                      "with <code>protected = true</code>. See <a href=\"/en/guides/marketing-protection-reklamebeskyttelse\">"
                      "marketing protection</a>."),
            ],
            "faq": [
                ("Do I need an API key?",
                 "No. Leave headers and authentication empty."),
                ("Can I enrich thousands of rows at once?",
                 "The API has fair-use rate limits, so run large batches at a steady pace. If you need sustained "
                 "heavy traffic, email noah@noahbohme.com."),
                ("What if the CVR number doesn't exist?",
                 "The API responds with HTTP 404. In Zapier and Make you can catch that with a filter or an error "
                 "handler so the rest of the flow continues."),
            ],
        },
    },
]
