#!/usr/bin/env bash

set -e
set -x

source ./database.env

useropt="-u${root_username}"
passopt="-p${root_password}"

if [ -z ${root_password} ]
then
  passopt=""
fi

mysql ${useropt} ${passopt} << _EOSQL_
# database
drop database if exists ${dbname};
create database ${dbname} default character set utf8;

# user
grant all privileges on ${dbname}.* to ${username}@localhost identified by "${password}";
select host, user, password from mysql.user;

# scheme contents
use ${dbname};
source ./create.sql

_EOSQL_
