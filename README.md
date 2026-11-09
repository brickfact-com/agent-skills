# Brickfact LEGO Shopping

[Brickfact](https://brickfact.com) helps you find LEGO sets, compare regional retailer offers and explore recorded retailer price history. This repository provides an agent skill and a portable MCP plugin for that public shopping service.

Ask your agent:

- “Find LEGO Star Wars sets under €100 including shipping to Germany.”
- “Compare LEGO 10311 and 10281 for a gift delivered in France.”
- “Show the recorded retailer price history of LEGO 75372 in Germany over the last year, including any shorter available coverage.”
- “Help me set up a price alert for LEGO 10311 in the Brickfact app.”

## Install the skill

```sh
npx skills add brickfact-com/agent-skills --skill brickfact-shopping
```

The skill includes a Python 3 helper for agents with terminal access. It calls the public MCP endpoint using the Python standard library, so no API key, account or dependency installation is needed. Run the helper from the installed skill directory:

```sh
python3 scripts/brickfact.py tools search_sets
python3 scripts/brickfact.py call search_sets '{"market":"DE","query":"Star Wars","max_price":100,"price_basis":"delivered","limit":3}'
```

Installing the skill does not configure an MCP server in your agent. The helper works independently; agents with native MCP support can connect directly instead.

## Connect an MCP client

Endpoint: **https://mcp.brickfact.com/mcp**

Transport: **Streamable HTTP**

Authentication: **none**; public catalogue data only.

For Claude Code:

```sh
claude mcp add --transport http brickfact https://mcp.brickfact.com/mcp
```

For Codex:

```sh
codex mcp add brickfact --url https://mcp.brickfact.com/mcp
```

For Hermes, install this repository as a portable plugin and enable it:

```sh
hermes plugins install https://github.com/brickfact-com/agent-skills
hermes plugins enable brickfact
```

Use a current Hermes release supporting portable Agent Plugins v1 and remote MCP servers. Start a fresh session after installation. Interactive shopping cards depend on the host; ordinary data tools and text answers remain useful without cards.

## What it can do

| Task | MCP tools |
| --- | --- |
| Discover sets and resolve themes | `search_sets`, `list_themes` |
| Read specifications and monitored offers | `get_set_details`, `get_set_offers` |
| Compare two to four sets | `compare_sets` |
| Inspect recorded retailer prices | `get_retail_price_history`, `assess_deal` |
| Find related alternatives | `find_alternatives` |
| Show shopping cards where supported | `render_sets` |
| Prepare app instructions for alerts and watchlists | `get_app_handoff` |
| Read the separate EUR collector valuation series | `get_price_history` |

Supported delivery markets: Germany (`DE`), Austria (`AT`), Switzerland (`CH`), United Kingdom (`GB`), United States (`US`), France (`FR`), Netherlands (`NL`), Spain (`ES`) and Italy (`IT`). Select the delivery country explicitly; language alone does not identify the shopping market.

## Prices and coverage

Shopping searches can use known delivered prices, including reported shipping. Unknown shipping is excluded from delivered budgets. Offers are monitored observations, not stock confirmations or guaranteed checkout prices.

Retail history reports its actual observation dates and coverage. It excludes Amazon, estimated shipping and missing days; a recorded low is not an all-time low across every shop. Collector valuations are a separate EUR sealed-set series and are not retailer price history or a forecast.

The plugin cannot buy sets, access private collections or create account alerts. For alerts and watchlists, it returns an [app handoff](https://brickfact.com) and instructions; the user completes setup in the Brickfact app.

## Network access and privacy

Installing the plugin connects Hermes to `mcp.brickfact.com`; the Python helper contacts that same fixed HTTPS endpoint only when run. Tool calls send the selected set numbers, market, search text and shopping filters to Brickfact. Do not include personal or sensitive information in search text.

The package has no account credentials, install hooks, self-updater or background process. It does not read private account files. The helper does not persist requests or results. The hosted service briefly caches public results and keeps connection metadata in memory for rate limiting. It records aggregate hourly tool-call counts, without search text, IP addresses or conversation content in those counts. See the [MCP privacy policy](https://mcp.brickfact.com/privacy) for retention and hosting details.

Optional shopping cards load product images from `image-cdn.brickfact.com`. Following a result opens a Brickfact comparison page. These pages contain disclosed affiliate links: Brickfact may earn a commission from qualifying purchases. Returned comparison links include `utm_medium=mcp`; website analytics and the [website privacy policy](https://brickfact.com/privacy-policy) apply after a visit.

## Support and license

[Visit Brickfact](https://brickfact.com) · [Publisher information](https://brickfact.com/imprint) · [Terms](https://brickfact.com/terms) · [Contact support](mailto:info@brickfact.com)

The skill, helper and plugin manifests are MIT licensed. Brickfact's logo is a brand asset and is excluded from that license; it is included to identify this integration. The hosted service and its data are not licensed by this repository.

LEGO is a trademark of the LEGO Group. Brickfact is independent and is not sponsored, authorized or endorsed by the LEGO Group.
