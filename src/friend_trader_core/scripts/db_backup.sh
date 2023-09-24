#!/bin/bash

RDS_ENDPOINT=rdsendpoint
RDS_PORT=5432
RDS_DB_NAME=DB_NAME
RDS_USERNAME=DB_USER
RDS_PASSWORD="PASWORD"

LOCAL_DB_NAME=DB_NAME
LOCAL_USERNAME=DB_USER
LOCAL_PASSWORD="Testing321."

TODAY=$(date +"%Y%m%d")
DUMP_FILE="/var/lib/postgresql/backups/DB_NAME_$TODAY.dump"

export PGPASSWORD=$RDS_PASSWORD
pg_dump -h $RDS_ENDPOINT -p $RDS_PORT -U $RDS_USERNAME -F c -b -v -f $DUMP_FILE $RDS_DB_NAME
export PGPASSWORD=$LOCAL_PASSWORD
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U DB_USER -d DB_NAME $DUMP_FILE
# Cleanup
rm $DUMP_FILE