-- Catalog Core FK indexes for scale.

create index if not exists catalog_aliases_source_idx
  on public.catalog_aliases(source_id);
create index if not exists catalog_cards_set_idx
  on public.catalog_cards(set_id);
create index if not exists catalog_conflicts_card_idx
  on public.catalog_conflicts(card_id);
create index if not exists catalog_conflicts_current_source_idx
  on public.catalog_conflicts(current_source_id);
create index if not exists catalog_conflicts_candidate_source_idx
  on public.catalog_conflicts(candidate_source_id);
create index if not exists catalog_discovery_game_idx
  on public.catalog_discovery_submissions(game_slug);
create index if not exists catalog_discovery_matched_card_idx
  on public.catalog_discovery_submissions(matched_card_id)
  where matched_card_id is not null;
create index if not exists catalog_source_links_variant_idx
  on public.catalog_source_links(variant_id)
  where variant_id is not null;
create index if not exists catalog_sync_runs_source_idx
  on public.catalog_sync_runs(source_id);
