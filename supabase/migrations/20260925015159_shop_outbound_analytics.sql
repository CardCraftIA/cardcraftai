-- Aggregate commercial intent without visitor identifiers, prices or payments.
create table if not exists public.shop_outbound_events (
  id bigint generated always as identity primary key,
  occurred_at timestamptz not null default now(),
  item_id text not null check (char_length(item_id) between 1 and 40),
  partner text not null check (partner in ('tcgplayer', 'amazon_br')),
  campaign text not null default 'shop' check (campaign ~ '^[a-z0-9_-]{1,32}$'),
  is_affiliate boolean not null default false
);

create index if not exists shop_outbound_events_occurred_at_idx
  on public.shop_outbound_events (occurred_at desc);
create index if not exists shop_outbound_events_campaign_idx
  on public.shop_outbound_events (campaign, occurred_at desc);

alter table public.shop_outbound_events enable row level security;
revoke all on public.shop_outbound_events from anon, authenticated;
grant select, insert on public.shop_outbound_events to service_role;
grant usage, select on sequence public.shop_outbound_events_id_seq to service_role;
