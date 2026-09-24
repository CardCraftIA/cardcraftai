-- CardCraft Community social layer.
-- Applied first to CardCraftAI-TEST. Keep production deployment gated behind staging validation.

create table if not exists public.community_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  handle text not null unique,
  display_name text not null,
  bio text not null default '',
  avatar_emoji text not null default '🃏',
  favorite_tcg text not null default 'Pokémon',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint community_profiles_handle_format check (handle ~ '^[a-z0-9_]{3,24}$'),
  constraint community_profiles_display_name_length check (char_length(display_name) between 1 and 40),
  constraint community_profiles_bio_length check (char_length(bio) <= 240),
  constraint community_profiles_avatar_length check (char_length(avatar_emoji) between 1 and 16),
  constraint community_profiles_tcg_length check (char_length(favorite_tcg) between 1 and 60)
);

create table if not exists public.community_posts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.community_profiles(user_id) on delete cascade,
  post_type text not null default 'discussion',
  title text not null,
  body text not null,
  collection_item_id uuid references public.collection_items(id) on delete set null,
  card_snapshot jsonb not null default '{}'::jsonb,
  comments_enabled boolean not null default true,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint community_posts_type_check check (post_type in ('showcase','question','discussion','collection')),
  constraint community_posts_title_length check (char_length(title) between 1 and 140),
  constraint community_posts_body_length check (char_length(body) between 1 and 2200),
  constraint community_posts_status_check check (status in ('active','removed')),
  constraint community_posts_snapshot_size check (octet_length(card_snapshot::text) <= 24000)
);

create table if not exists public.community_reactions (
  post_id uuid not null references public.community_posts(id) on delete cascade,
  user_id uuid not null references public.community_profiles(user_id) on delete cascade,
  reaction text not null default 'hype',
  created_at timestamptz not null default now(),
  primary key (post_id, user_id),
  constraint community_reactions_type_check check (reaction = 'hype')
);

create table if not exists public.community_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.community_posts(id) on delete cascade,
  user_id uuid not null references public.community_profiles(user_id) on delete cascade,
  body text not null,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint community_comments_body_length check (char_length(body) between 1 and 1000),
  constraint community_comments_status_check check (status in ('active','removed'))
);

create table if not exists public.community_follows (
  follower_id uuid not null references public.community_profiles(user_id) on delete cascade,
  following_id uuid not null references public.community_profiles(user_id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (follower_id, following_id),
  constraint community_follows_not_self check (follower_id <> following_id)
);

create table if not exists public.community_reports (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references public.community_profiles(user_id) on delete cascade,
  post_id uuid references public.community_posts(id) on delete cascade,
  comment_id uuid references public.community_comments(id) on delete cascade,
  reason text not null,
  details text not null default '',
  status text not null default 'open',
  created_at timestamptz not null default now(),
  constraint community_reports_target_check check (
    (post_id is not null and comment_id is null)
    or (post_id is null and comment_id is not null)
  ),
  constraint community_reports_reason_check check (reason in ('spam','harassment','unsafe','misleading','other')),
  constraint community_reports_details_length check (char_length(details) <= 500),
  constraint community_reports_status_check check (status in ('open','reviewed','dismissed'))
);

create unique index if not exists community_reports_unique_post_report
  on public.community_reports(reporter_id, post_id)
  where post_id is not null;
create unique index if not exists community_reports_unique_comment_report
  on public.community_reports(reporter_id, comment_id)
  where comment_id is not null;
create index if not exists community_posts_created_at_idx
  on public.community_posts(created_at desc);
create index if not exists community_posts_user_created_idx
  on public.community_posts(user_id, created_at desc);
create index if not exists community_comments_post_created_idx
  on public.community_comments(post_id, created_at asc);
create index if not exists community_reactions_post_idx
  on public.community_reactions(post_id);
create index if not exists community_follows_following_idx
  on public.community_follows(following_id);

alter table public.community_profiles enable row level security;
alter table public.community_posts enable row level security;
alter table public.community_reactions enable row level security;
alter table public.community_comments enable row level security;
alter table public.community_follows enable row level security;
alter table public.community_reports enable row level security;

revoke all on table public.community_profiles from anon;
revoke all on table public.community_posts from anon;
revoke all on table public.community_reactions from anon;
revoke all on table public.community_comments from anon;
revoke all on table public.community_follows from anon;
revoke all on table public.community_reports from anon;

grant select, insert, update on table public.community_profiles to authenticated;
grant select, insert, update, delete on table public.community_posts to authenticated;
grant select, insert, delete on table public.community_reactions to authenticated;
grant select, insert, update, delete on table public.community_comments to authenticated;
grant select, insert, delete on table public.community_follows to authenticated;
grant select, insert on table public.community_reports to authenticated;

drop policy if exists community_profiles_read on public.community_profiles;
create policy community_profiles_read on public.community_profiles
for select to authenticated using (auth.uid() is not null);

drop policy if exists community_profiles_insert_own on public.community_profiles;
create policy community_profiles_insert_own on public.community_profiles
for insert to authenticated
with check (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_profiles_update_own on public.community_profiles;
create policy community_profiles_update_own on public.community_profiles
for update to authenticated
using (auth.uid() is not null and auth.uid() = user_id)
with check (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_posts_read_active on public.community_posts;
create policy community_posts_read_active on public.community_posts
for select to authenticated using (status = 'active');

drop policy if exists community_posts_insert_own on public.community_posts;
create policy community_posts_insert_own on public.community_posts
for insert to authenticated
with check (auth.uid() is not null and auth.uid() = user_id and status = 'active');

drop policy if exists community_posts_update_own on public.community_posts;
create policy community_posts_update_own on public.community_posts
for update to authenticated
using (auth.uid() is not null and auth.uid() = user_id)
with check (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_posts_delete_own on public.community_posts;
create policy community_posts_delete_own on public.community_posts
for delete to authenticated
using (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_reactions_read on public.community_reactions;
create policy community_reactions_read on public.community_reactions
for select to authenticated using (auth.uid() is not null);

drop policy if exists community_reactions_insert_own on public.community_reactions;
create policy community_reactions_insert_own on public.community_reactions
for insert to authenticated
with check (
  auth.uid() is not null
  and auth.uid() = user_id
  and exists (
    select 1 from public.community_posts p
    where p.id = post_id and p.status = 'active'
  )
);

drop policy if exists community_reactions_delete_own on public.community_reactions;
create policy community_reactions_delete_own on public.community_reactions
for delete to authenticated
using (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_comments_read_active on public.community_comments;
create policy community_comments_read_active on public.community_comments
for select to authenticated using (status = 'active');

drop policy if exists community_comments_insert_own on public.community_comments;
create policy community_comments_insert_own on public.community_comments
for insert to authenticated
with check (
  auth.uid() is not null
  and auth.uid() = user_id
  and status = 'active'
  and exists (
    select 1 from public.community_posts p
    where p.id = post_id
      and p.status = 'active'
      and p.comments_enabled = true
  )
);

drop policy if exists community_comments_update_own on public.community_comments;
create policy community_comments_update_own on public.community_comments
for update to authenticated
using (auth.uid() is not null and auth.uid() = user_id)
with check (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_comments_delete_own on public.community_comments;
create policy community_comments_delete_own on public.community_comments
for delete to authenticated
using (auth.uid() is not null and auth.uid() = user_id);

drop policy if exists community_follows_read on public.community_follows;
create policy community_follows_read on public.community_follows
for select to authenticated using (auth.uid() is not null);

drop policy if exists community_follows_insert_own on public.community_follows;
create policy community_follows_insert_own on public.community_follows
for insert to authenticated
with check (auth.uid() is not null and auth.uid() = follower_id);

drop policy if exists community_follows_delete_own on public.community_follows;
create policy community_follows_delete_own on public.community_follows
for delete to authenticated
using (auth.uid() is not null and auth.uid() = follower_id);

drop policy if exists community_reports_insert_own on public.community_reports;
create policy community_reports_insert_own on public.community_reports
for insert to authenticated
with check (auth.uid() is not null and auth.uid() = reporter_id and status = 'open');

drop policy if exists community_reports_read_own on public.community_reports;
create policy community_reports_read_own on public.community_reports
for select to authenticated
using (auth.uid() is not null and auth.uid() = reporter_id);
