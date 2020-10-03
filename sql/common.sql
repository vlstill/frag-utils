-- don't do in transaction, this is allowed to fail
create role frag_{POLL}_{COURSE} login;
begin;
grant frag_{POLL}_{COURSE} to current_user with admin option;
create schema if not exists frag_{POLL};
grant all on schema frag_{POLL} to frag_{POLL}_{COURSE};
grant usage on schema frag_{POLL} to {COURSE}_teacher;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant all on tables to current_user with grant option;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant all on sequences to current_user with grant option;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant all on functions to current_user with grant option;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant all on types to current_user with grant option;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant select on tables to {COURSE}_teacher;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant usage on sequences to {COURSE}_teacher;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant execute on functions to {COURSE}_teacher;
alter default privileges for role frag_{POLL}_{COURSE} in schema frag_{POLL} grant usage on types to {COURSE}_teacher;

set search_path to frag;

grant {COURSE}_submit to frag_{POLL}_{COURSE};
commit;
