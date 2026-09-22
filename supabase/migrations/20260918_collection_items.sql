-- Apply before enabling COLLECTIONS_ENABLED in Streamlit secrets.
create table public.collection_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  catalog_id text not null check (length(catalog_id) between 1 and 200),
  card_name text not null check (length(card_name) between 1 and 200),
  set_name text not null default '',
  card_number text not null default '',
  image_url text not null default '',
  quantity integer not null default 1 check (quantity between 0 and 9999),
  condition text not null default 'Not assessed' check (condition in ('Not assessed','Near Mint','Lightly Played','Moderately Played','Heavily Played','Damaged')),
  language text not null default '' check (length(language) <= 80),
  variant text not null default '' check (length(variant) <= 120),
  notes text not null default '' check (length(notes) <= 2000),
  wishlist boolean not null default false,
  created_at timestamptz not null default now()
);
create index collection_items_owner on public.collection_items(user_id);
alter table public.collection_items enable row level security;
revoke all on public.collection_items
from anon, authenticated, service_role;

grant select, insert, update, delete
on public.collection_items
to authenticated;

grant select, insert, update, delete
on public.collection_items
to service_role;
create policy collection_owner_select on public.collection_items for select to authenticated using (user_id = auth.uid());
create policy collection_owner_insert on public.collection_items for insert to authenticated with check (user_id = auth.uid());
create policy collection_owner_update on public.collection_items for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy collection_owner_delete on public.collection_items for delete to authenticated using (user_id = auth.uid());
-- Deliberately no public read policy. Public profiles need a separate public projection.
