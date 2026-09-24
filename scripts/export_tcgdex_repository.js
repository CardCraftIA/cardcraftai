#!/usr/bin/env node
/*
Build a CardCraft Catalog source snapshot from the MIT-licensed TCGdex repository.

Usage:
  node scripts/export_tcgdex_repository.js --repo ../cards-database --output ./tcgdex_cards.jsonl

The exporter never calls the TCGdex API. It evaluates the checked-out TypeScript
source files locally through ts-node, preserving rich variants and translations.
Images are represented as deterministic TCGdex asset references only; no image
binaries are copied into CardCraftAI.
*/
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

function arg(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const repoRoot = path.resolve(arg("--repo", "."));
const outputPath = path.resolve(arg("--output", "tcgdex_cards.jsonl"));
const tsNodeRegister = path.join(repoRoot, "node_modules", "ts-node", "register", "transpile-only");
require(tsNodeRegister);
const { globSync } = require(path.join(repoRoot, "node_modules", "glob"));

function localeValue(value, language) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return "";
  return typeof value[language] === "string" ? value[language] : "";
}

function stableVariantKey(variant, index) {
  const payload = JSON.stringify(variant || {}, Object.keys(variant || {}).sort());
  const digest = crypto.createHash("sha256").update(payload).digest("hex").slice(0, 12);
  const type = String((variant || {}).type || "normal");
  const subtype = String((variant || {}).subtype || "");
  const size = String((variant || {}).size || "standard");
  return [type, subtype, size, digest || String(index)].filter(Boolean).join(":");
}

function imageBase(language, serieId, setId, localId) {
  if (!language || !serieId || !setId || !localId) return "";
  const pieces = [language, serieId, setId, localId].map(encodeURIComponent);
  return "https://assets.tcgdex.net/" + pieces.join("/");
}

const cardFiles = globSync("data/*/*/*.ts", {
  cwd: repoRoot,
  nodir: true,
}).sort();

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
const out = fs.createWriteStream(outputPath, { encoding: "utf8" });
let emitted = 0;
let variantCount = 0;
let localizationCount = 0;
const games = new Map();
const sets = new Map();
const languageCounts = new Map();

for (const relativePath of cardFiles) {
  const absolutePath = path.join(repoRoot, relativePath);
  const cardModule = require(absolutePath);
  const card = cardModule && (cardModule.default || cardModule);
  if (!card || typeof card !== "object" || !card.set || !card.set.id) continue;

  const parts = relativePath.split(path.sep);
  const topSeriesDirectory = parts[1] || "";
  const localId = path.basename(relativePath, ".ts");
  const set = card.set || {};
  const serie = set.serie || {};
  const gameSlug = topSeriesDirectory === "Pokémon TCG Pocket" ? "pokemon-pocket" : "pokemon";
  const sourceKey = String(set.id) + "-" + String(localId);
  const names = card.name && typeof card.name === "object" ? card.name : {};
  const setNames = set.name && typeof set.name === "object" ? set.name : {};
  const seriesNames = serie.name && typeof serie.name === "object" ? serie.name : {};

  const localizations = [];
  const languages = new Set([
    ...Object.keys(names),
    ...Object.keys(setNames),
  ]);
  for (const language of Array.from(languages).sort()) {
    const cardName = localeValue(names, language);
    if (!cardName) continue;
    const base = imageBase(language, String(serie.id || ""), String(set.id || ""), String(localId));
    localizations.push({
      language,
      name: cardName,
      set_name: localeValue(setNames, language),
      series_name: localeValue(seriesNames, language),
      description: localeValue(card.description, language),
      image_base_url: base,
      image_small_url: base ? base + "/low.webp" : "",
      image_url: base ? base + "/high.webp" : "",
    });
    localizationCount += 1;
    languageCounts.set(language, (languageCounts.get(language) || 0) + 1);
  }

  const rawVariants = Array.isArray(card.variants) && card.variants.length
    ? card.variants
    : [{ type: "normal", subtype: "", size: "standard" }];
  const variants = rawVariants.map((variant, index) => ({
    variant_key: stableVariantKey(variant, index),
    variant_type: String((variant || {}).type || "normal"),
    subtype: String((variant || {}).subtype || ""),
    size: String((variant || {}).size || "standard"),
    stamps: Array.isArray((variant || {}).stamp) ? variant.stamp.map(String) : [],
    external_ids: (variant || {}).thirdParty || {},
    attributes: Object.fromEntries(
      Object.entries(variant || {}).filter(([key]) => !["type", "subtype", "size", "stamp", "thirdParty"].includes(key))
    ),
  }));
  variantCount += variants.length;

  const cardWithoutSet = Object.fromEntries(
    Object.entries(card).filter(([key]) => !["set", "name", "description", "variants"].includes(key))
  );

  const record = {
    schema_version: 1,
    provider: "tcgdex",
    source_key: sourceKey,
    game_slug: gameSlug,
    local_id: String(localId),
    set: {
      source_id: String(set.id || ""),
      code: String((set.abbreviations || {}).official || set.tcgOnline || set.id || ""),
      names: setNames,
      series_source_id: String(serie.id || ""),
      series_names: seriesNames,
      release_date: String(set.releaseDate || ""),
      card_count: set.cardCount || {},
      third_party: set.thirdParty || {},
      attributes: Object.fromEntries(
        Object.entries(set).filter(([key]) => !["id", "name", "serie", "releaseDate", "cardCount", "thirdParty", "abbreviations", "tcgOnline"].includes(key))
      ),
    },
    card: {
      category: String(card.category || ""),
      rarity: String(card.rarity || ""),
      illustrator: String(card.illustrator || ""),
      hp: Number.isFinite(card.hp) ? card.hp : null,
      dex_ids: Array.isArray(card.dexId) ? card.dexId.filter(Number.isFinite) : [],
      attributes: cardWithoutSet,
    },
    localizations,
    variants,
  };

  out.write(JSON.stringify(record) + "\n");
  emitted += 1;

  delete require.cache[require.resolve(absolutePath)];
}

out.end();
out.on("finish", () => {
  const stats = {
    schema_version: 1,
    provider: "tcgdex",
    generated_at: new Date().toISOString(),
    source_repository: "https://github.com/tcgdex/cards-database",
    card_records: emitted,
    variants: variantCount,
    localizations: localizationCount,
    languages: Object.fromEntries(Array.from(languageCounts.entries()).sort()),
  };
  fs.writeFileSync(outputPath + ".stats.json", JSON.stringify(stats, null, 2) + "\n", "utf8");
  process.stdout.write(JSON.stringify(stats, null, 2) + "\n");
});
