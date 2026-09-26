-- Private online matches. All reads/writes go through authenticated server code.
create table if not exists public.cardcraft_game_matches (
    id uuid primary key default gen_random_uuid(),
    invite_code text not null unique check (invite_code ~ '^[0-9A-F]{10}$'),
    player_a uuid not null references auth.users(id) on delete cascade,
    player_b uuid references auth.users(id) on delete cascade,
    status text not null default 'waiting' check (status in ('waiting', 'active', 'finished')),
    state jsonb,
    version integer not null default 1 check (version > 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (player_b is null or player_a <> player_b),
    check ((status = 'waiting' and player_b is null and state is null)
           or (status in ('active', 'finished') and player_b is not null and state is not null))
);
create index if not exists cardcraft_game_matches_player_a_idx on public.cardcraft_game_matches (player_a, updated_at desc);
create index if not exists cardcraft_game_matches_player_b_idx on public.cardcraft_game_matches (player_b, updated_at desc);
alter table public.cardcraft_game_matches enable row level security;
revoke all on public.cardcraft_game_matches from anon, authenticated;
grant select, insert, update on public.cardcraft_game_matches to service_role;
