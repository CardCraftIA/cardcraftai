-- Disposable fixtures: entire script MUST run as one transaction and ends in ROLLBACK.
begin;
select set_config('test.atlas_uid',gen_random_uuid()::text,true);
select set_config('test.atlas_other',gen_random_uuid()::text,true);
insert into auth.users(id,email,email_confirmed_at,raw_user_meta_data,raw_app_meta_data)
values(current_setting('test.atlas_uid')::uuid,'atlas-qa-'||current_setting('test.atlas_uid')||'@example.invalid',now(),'{}','{}'),
(current_setting('test.atlas_other')::uuid,'atlas-qa-'||current_setting('test.atlas_other')||'@example.invalid',now(),'{}','{}');
select set_config('request.jwt.claim.sub',current_setting('test.atlas_uid'),true);
select set_config('test.atlas_request',gen_random_uuid()::text,true);
select set_config('test.atlas_token',gen_random_uuid()::text,true);
set local role authenticated;
do $$
declare r uuid:=current_setting('test.atlas_request')::uuid; t uuid:=current_setting('test.atlas_token')::uuid; v jsonb; blocked boolean:=false;
begin
 v:=public.reserve_atlas_web_question(r,t); if v->>'remaining'<>'4' then raise exception 'reserve failed %',v; end if;
 v:=public.reserve_atlas_web_question(r,t); if v->>'duplicate'<>'true' then raise exception 'duplicate not blocked'; end if;
 begin perform public.settle_atlas_web_question(r,gen_random_uuid(),false); exception when others then blocked:=true; end;
 if not blocked then raise exception 'wrong capability accepted'; end if;
 perform set_config('request.jwt.claim.sub',current_setting('test.atlas_other'),true);blocked:=false;
 begin perform public.settle_atlas_web_question(r,t,false); exception when others then blocked:=true; end;
 if not blocked then raise exception 'cross-account refund accepted'; end if;
 perform set_config('request.jwt.claim.sub',current_setting('test.atlas_uid'),true);
 v:=public.settle_atlas_web_question(r,t,false); if v->>'remaining'<>'5' or v->>'status'<>'refunded' then raise exception 'refund failed'; end if;
 v:=public.settle_atlas_web_question(r,t,false); if v->>'remaining'<>'5' then raise exception 'duplicate refund changed balance'; end if;
 v:=public.settle_atlas_web_question(r,t,true); if v->>'status'<>'refunded' then raise exception 'refunded request completed'; end if;
 r:=gen_random_uuid();v:=public.reserve_atlas_web_question(r,t);v:=public.settle_atlas_web_question(r,t,true);
 v:=public.settle_atlas_web_question(r,t,false);if v->>'status'<>'completed' or v->>'remaining'<>'4' then raise exception 'completed request refunded'; end if;
 -- Leave a reservation pending to simulate worker termination.
 r:=gen_random_uuid();perform set_config('test.atlas_pending',r::text,true);v:=public.reserve_atlas_web_question(r,t);
 if v->>'remaining'<>'3' then raise exception 'pending reserve failed'; end if;
end;
$$;
reset role;
update cardcraft_private.atlas_web_requests set expires_at=now()-interval '1 second'
where user_id=current_setting('test.atlas_uid')::uuid and request_id=current_setting('test.atlas_pending')::uuid;
set local role authenticated;
do $$
declare v jsonb; r uuid:=gen_random_uuid(); t uuid:=gen_random_uuid();
begin
 v:=public.reserve_atlas_web_question(r,t);if v->>'remaining'<>'3' then raise exception 'abandoned reservation not reconciled %',v; end if;
 v:=public.settle_atlas_web_question(current_setting('test.atlas_pending')::uuid,current_setting('test.atlas_token')::uuid,true);
 if v->>'status'<>'refunded' then raise exception 'expired request completed'; end if;
 v:=public.settle_atlas_web_question(r,t,false);if v->>'remaining'<>'4' then raise exception 'balance after reconciliation incorrect'; end if;
end;
$$;
reset role;
-- Paid requests must never refund a previously consumed free question.
update public.atlas_allowances set paid_until=now()+interval '1 day' where user_id=current_setting('test.atlas_uid')::uuid;
set local role authenticated;
select public.reserve_atlas_web_question('00000000-0000-4000-8000-000000000001',current_setting('test.atlas_token')::uuid);
select public.settle_atlas_web_question('00000000-0000-4000-8000-000000000001',current_setting('test.atlas_token')::uuid,false);
reset role;
do $$ begin
 if (select used from public.atlas_allowances where user_id=current_setting('test.atlas_uid')::uuid)<>1 then raise exception 'paid refund altered free quota'; end if;
 if has_function_privilege('anon','public.settle_atlas_web_question(uuid,uuid,boolean)','EXECUTE') then raise exception 'anon grant'; end if;
 if has_table_privilege('authenticated','cardcraft_private.atlas_web_requests','SELECT') then raise exception 'capabilities exposed'; end if;
end $$;
select 'PASS: refunds, duplicate, capability, ownership, expiry, paid balance and grants' as result;
rollback;
