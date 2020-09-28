create role frag_{POLL}_{COURSE} login;
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

grant usage on schema frag to frag_{POLL}_{COURSE};
grant insert, select on submission to frag_{POLL}_{COURSE};
grant insert, select on submission_in to frag_{POLL}_{COURSE};
grant insert, select on content to frag_{POLL}_{COURSE};
grant select on assignment to frag_{POLL}_{COURSE};
grant select on assignment_in to frag_{POLL}_{COURSE};
grant select on teacher_list to frag_{POLL}_{COURSE};
grant select on enrollment to frag_{POLL}_{COURSE};
grant select on person to frag_{POLL}_{COURSE};
grant usage on submission_pkey_seq to frag_{POLL}_{COURSE};
grant select on current_suite to frag_{POLL}_{COURSE};
grant select, insert on eval_req to frag_{POLL}_{COURSE};
