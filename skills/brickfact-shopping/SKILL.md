---
name: brickfact-shopping
description: Find and compare LEGO sets with Brickfact, choose gifts, assess recorded retail prices, and prepare app handoffs for price alerts or watchlists.
---

# Brickfact LEGO Shopping

Use [Brickfact](https://brickfact.com) to find LEGO sets, compare regional retailer offers and inspect recorded retail prices in DE, AT, CH, GB, US, FR, NL, ES and IT. Reply in the user's language where supported.

## Access the live catalogue

Prefer Brickfact MCP tools already connected to the host. The public endpoint is `https://mcp.brickfact.com/mcp`, using Streamable HTTP without authentication. Installing this skill alone does not configure a host's MCP connection.

If MCP tools are not connected and terminal/network access is available, use the included Python 3 helper. Resolve `scripts/brickfact.py` relative to this skill's installed directory, not the user's project. It uses only the standard library and sends shopping inputs to the fixed Brickfact endpoint; no API key or account is needed.

```sh
python3 scripts/brickfact.py tools search_sets
python3 scripts/brickfact.py call search_sets '{"market":"DE","query":"Star Wars","max_price":100,"price_basis":"delivered","limit":3}'
```

`tools NAME` returns that tool's current input schema. Discover the schema before using unfamiliar arguments. `call NAME JSON` returns live structured data. For retailer history, for example, use `call get_retail_price_history '{"market":"DE","set_id":75372,"days":365}'`.

If neither connection is available, explain the limitation and link to Brickfact; do not invent live prices. Do not request or look for credentials, use the keyed JSON API, or include personal information in search text. The [MCP privacy policy](https://mcp.brickfact.com/privacy) explains the hosted service's processing and aggregate operational counts.

## Shopping context

Reuse the delivery market already supplied in the conversation. If it is missing, ask which country the user is shopping in; language and currency alone do not establish delivery country. Keep that market when the user changes budget, theme or result language.

Use `price_basis: delivered` for shopping detail, offer and comparison calls as well. For a shopping budget including shipping, call `search_sets` with `price_basis: delivered`. These searches filter and sort known delivered totals before pagination. Use `item` only when the user wants item prices excluding shipping. A missing shipping fee is unknown, never free. A feed timestamp is not proof of stock or delivery by a deadline.

Resolve named themes with `list_themes`; do not guess their IDs. Preserve explicit price, piece-count and retirement constraints. If there are no results, explain which constraint could be relaxed and ask before exceeding the budget or changing market. Do not silently retry an unavailable delivered-price search as item-price search.

## Gifts and discovery

Use the age, interests, budget and market the user has already provided. Ask only for missing information that materially affects the selection; offer a small range when preferences are broad. Translate interests into supported theme searches and explain matches using returned attributes. Manufacturer age labels are building recommendations, not safety certification, and an 18+ label alone does not establish difficulty. Never invent build quality, play features, recipient suitability or a guaranteed arrival date.

Use `find_alternatives` for a known set, optionally with `preference: cheaper`, a delivered `max_price`, or `fewer_pieces`. These are bounded related candidates, not an exhaustive best-of ranking. Fewer pieces does not mean a smaller finished model.

## Presentation and evidence

After choosing final IDs from search or alternatives, use `render_sets` when the connected host supports shopping cards: up to six cards, or `view: comparison` for two to four sets. With the Python helper or a host without UI, give a useful text comparison using the returned data instead. Refer to the main differences; avoid repeating every field shown in cards.

Link recommended sets using their returned `comparison_url`, preserving the selected delivery market. These Brickfact pages contain disclosed affiliate links; mention that if relevant to a question about monetization. Rank by the user's constraints and returned evidence, without adding forced recommendations or unrelated promotional links.

For any price-history, price-development or Preisentwicklung question, call `get_retail_price_history` first. Use `days: 365` for the last 12 months. Show the returned merchant history even if recording began later: report the actual first/last recorded dates, observation days, currency and freshness. For example, 20 recorded days in a requested 365-day window is available history with partial coverage, not "no merchant history". Do not interpolate missing days or claim the returned period covers a full year.

Use `assess_deal` for a current-offer comparison. History excludes Amazon, so do not describe the recorded low as the lowest price ever across all shops. A failed call means temporarily unavailable data, not an empty history. If no eligible observations are returned, state the selected market, window and known-shipping restriction, then link to the set page. Never substitute market valuations for partial, missing or failed merchant history.

Use `get_price_history` only when the user explicitly asks for collector value, resale valuation or Marktwert, or asks to see that series separately as well. It is a separate EUR sealed-set valuation series, not historical retailer pricing or a forecast.

## Shortlists, watchlists and alerts

The shopping card's shortlist belongs to that card and is not synced to a Brickfact account. Do not imply it is a persistent account wishlist.

For a price alert or account watchlist, call `get_app_handoff` with the chosen set, market, action and optional target price. Give the returned app link and remaining steps. `created: false` means nothing has been created: the user must sign in and finish in the app. Do not ask for passwords, payment details, email addresses or notification tokens. Do not promise notification delivery or ongoing monitoring by this conversation.
