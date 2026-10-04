-- TEST only. Historical requests remain completed and cannot be refunded.
alter table cardcraft_private.atlas_web_requests
 add column reservation_token uuid,
 add column status text not null default 'completed' check(status in ('reserved','completed','refunded')),
 add column charged boolean not null default false,
 add column expires_at timestamptz;

create function cardcraft_private.reserve_atlas_web_question(p_request_id uuid,p_token uuid)
returns jsonb language plpgsql security definer set search_path='' as $$
declare uid uuid:=auth.uid(); result jsonb; refunds integer;
begin
 if uid is null or p_request_id is null or p_token is null then raise exception 'Authentication and capability required'; end if;
 if not exists(select 1 from auth.users where id=uid and email_confirmed_at is not null) then raise exception 'Confirmed email required'; end if;
 perform pg_advisory_xact_lock(hashtextextended(uid::text,214));
 -- Release abandoned requests on the next valid request, even if the limit was reached.
 with expired as (
  update cardcraft_private.atlas_web_requests set status='refunded'
  where user_id=uid and status='reserved' and expires_at<=clock_timestamp()
  returning charged
 ) select count(*) filter(where charged) into refunds from expired;
 if refunds>0 then
  update public.atlas_allowances set used=greatest(0,used-refunds),updated_at=now() where user_id=uid;
 end if;
 if exists(select 1 from cardcraft_private.atlas_web_requests where user_id=uid and request_id=p_request_id) then
  return jsonb_build_object('allowed',false,'duplicate',true);
 end if;
 if (select count(*) from cardcraft_private.atlas_web_requests where user_id=uid and created_at>now()-interval '1 minute')>=10 then
  return jsonb_build_object('rate_limited',true);
 end if;
 result:=public.claim_atlas_question();
 if (result->>'allowed')::boolean then
  insert into cardcraft_private.atlas_web_requests(user_id,request_id,reservation_token,status,charged,expires_at)
  values(uid,p_request_id,p_token,'reserved',not (result->>'paid')::boolean,clock_timestamp()+interval '2 minutes');
 end if;
 return result;
end;
$$;
revoke all on function cardcraft_private.reserve_atlas_web_question(uuid,uuid) from public,anon;
grant execute on function cardcraft_private.reserve_atlas_web_question(uuid,uuid) to authenticated;
create function public.reserve_atlas_web_question(p_request_id uuid,p_token uuid)
returns jsonb language sql security invoker set search_path='' as $$
 select cardcraft_private.reserve_atlas_web_question(p_request_id,p_token);
$$;
revoke all on function public.reserve_atlas_web_question(uuid,uuid) from public,anon;
grant execute on function public.reserve_atlas_web_question(uuid,uuid) to authenticated;

create function cardcraft_private.settle_atlas_web_question(p_request_id uuid,p_token uuid,p_success boolean)
returns jsonb language plpgsql security definer set search_path='' as $$
declare uid uuid:=auth.uid(); entry cardcraft_private.atlas_web_requests%rowtype; remaining integer;
begin
 if uid is null or p_token is null or p_success is null then raise exception 'Authentication and capability required'; end if;
 perform pg_advisory_xact_lock(hashtextextended(uid::text,214));
 select * into entry from cardcraft_private.atlas_web_requests
 where user_id=uid and request_id=p_request_id and reservation_token=p_token for update;
 if not found then raise exception 'Invalid reservation capability'; end if;
 if entry.status='reserved' then
  if p_success and entry.expires_at>clock_timestamp() then
   entry.status:='completed';
  else
   entry.status:='refunded';
   if entry.charged then
    update public.atlas_allowances set used=greatest(0,used-1),updated_at=now() where user_id=uid;
   end if;
  end if;
  update cardcraft_private.atlas_web_requests set status=entry.status where user_id=uid and request_id=p_request_id;
 end if;
 select case when paid_until>now() then null else greatest(0,5-used) end into remaining
 from public.atlas_allowances where user_id=uid;
 return jsonb_build_object('status',entry.status,'remaining',remaining);
end;
$$;
revoke all on function cardcraft_private.settle_atlas_web_question(uuid,uuid,boolean) from public,anon;
grant execute on function cardcraft_private.settle_atlas_web_question(uuid,uuid,boolean) to authenticated;
create function public.settle_atlas_web_question(p_request_id uuid,p_token uuid,p_success boolean)
returns jsonb language sql security invoker set search_path='' as $$
 select cardcraft_private.settle_atlas_web_question(p_request_id,p_token,p_success);
$$;
revoke all on function public.settle_atlas_web_question(uuid,uuid,boolean) from public,anon;
grant execute on function public.settle_atlas_web_question(uuid,uuid,boolean) to authenticated;
