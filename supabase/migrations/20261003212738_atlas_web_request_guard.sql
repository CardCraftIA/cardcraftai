-- TEST rollout only. No change to existing Streamlit allowance semantics.
create schema if not exists cardcraft_private;
revoke all on schema cardcraft_private from public, anon;
grant usage on schema cardcraft_private to authenticated;
create table cardcraft_private.atlas_web_requests (
  user_id uuid not null references auth.users(id) on delete cascade,
  request_id uuid not null,
  created_at timestamptz not null default now(),
  primary key(user_id,request_id)
);
alter table cardcraft_private.atlas_web_requests enable row level security;
revoke all on cardcraft_private.atlas_web_requests from public,anon,authenticated;
create index atlas_web_requests_user_time on cardcraft_private.atlas_web_requests(user_id,created_at);
create function cardcraft_private.claim_atlas_web_question(p_request_id uuid)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare uid uuid := auth.uid(); result jsonb;
begin
 if uid is null or p_request_id is null then raise exception 'Authentication and request ID required'; end if;
 if not exists(select 1 from auth.users where id=uid and email_confirmed_at is not null) then raise exception 'Confirmed email required'; end if;
 -- Serialize requests per user, including duplicate retries across instances.
 perform pg_advisory_xact_lock(hashtextextended(uid::text, 214));
 if exists(select 1 from cardcraft_private.atlas_web_requests where user_id=uid and request_id=p_request_id) then
  return jsonb_build_object('allowed',false,'duplicate',true);
 end if;
 if (select count(*) from cardcraft_private.atlas_web_requests where user_id=uid and created_at>now()-interval '1 minute')>=10 then
  raise exception 'Rate limit exceeded';
 end if;
 result := public.claim_atlas_question();
 if (result->>'allowed')::boolean then
  insert into cardcraft_private.atlas_web_requests(user_id,request_id) values(uid,p_request_id);
 end if;
 return result;
end;
$$;
revoke all on function cardcraft_private.claim_atlas_web_question(uuid) from public,anon;
grant execute on function cardcraft_private.claim_atlas_web_question(uuid) to authenticated;
create function public.claim_atlas_web_question(p_request_id uuid)
returns jsonb language sql security invoker set search_path = '' as $$
 select cardcraft_private.claim_atlas_web_question(p_request_id);
$$;
revoke all on function public.claim_atlas_web_question(uuid) from public,anon;
grant execute on function public.claim_atlas_web_question(uuid) to authenticated;
