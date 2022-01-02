create table action(id number generated always as identity
                   , type varchar2(50)
                   , ticker varchar2(5)
                   , lots   number
                   , go_in number
                   , created date default sysdate
                   , expire_time timestamp default trunc(systimestamp + 1/6, 'HH24')
                   , do_time timestamp)
/
alter table action
  add constraint action_pk
  primary key (id)
/

comment on column action.type is 'operation type';
comment on column action.go_in is 'price from which to do it';
comment on column action.do_time is 'when to do it';
comment on column action.expire_time is 'time of deal expiration';