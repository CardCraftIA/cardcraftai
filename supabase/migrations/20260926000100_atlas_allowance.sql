-- Five free Atlas submissions per authenticated account, across sessions.
-- Paid access is reserved for verified subscription fulfillment, not profile metadata.
create table if not exists public.atlas_allowances (
  user_id uuid primary key references auth.users(id) on delete cascade,
  used integer not null default 0 check (used >= 0),
  paid_until timestamptz,
  updated_at timestamptz not null default now()
);
alter table public.atlas_allowances enable row level security;
revoke all on public.atlas_allowances from anon, authenticated;

create or replace function public.claim_atlas_question()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  uid uuid := (select auth.uid());
  allowance public.atlas_allowances%rowtype;
begin
  if uid is null then
    raise exception 'Authentication required';
  end if;
  insert into public.atlas_allowances (user_id) values (uid)
  on conflict (user_id) do nothing;
  select * into allowance from public.atlas_allowances where user_id = uid for update;
  if allowance.paid_until > now() then
    return jsonb_build_object('allowed', true, 'used', allowance.used, 'remaining', null, 'paid', true);
  end if;
  if allowance.used >= 5 then
    return jsonb_build_object('allowed', false, 'used', allowance.used, 'remaining', 0, 'paid', false);
  end if;
  update public.atlas_allowances set used = used + 1, updated_at = now() where user_id = uid;
  return jsonb_build_object('allowed', true, 'used', allowance.used + 1, 'remaining', 4 - allowance.used, 'paid', false);
end;
$$;
revoke all on function public.claim_atlas_question() from public, anon;
grant execute on function public.claim_atlas_question() to authenticated;
