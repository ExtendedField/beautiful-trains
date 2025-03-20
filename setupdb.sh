#!/bin/zsh

# this script assumes postgresql is installed on the machine and that you have superuser access.
# documentation to aid you with this can be found here: https://www.postgresql.org/docs/17/installation.html

city="$1"
dbname="${1}_transitdb"

# checks to see if a postgresql db called transitdb exists and creates it if it doesnt
# also creates a user to own the database and changes that user to the owner.
if [[ -z $(psql -lqt | cut -d \| -f 1 | grep -w "$dbname") ]]
then
createdb "$dbname"
psql -d "$dbname" <<SetupCommands
CREATE USER transitdb_user WITH PASSWORD 'conductor';
ALTER DATABASE "$dbname" OWNER TO transitdb_user;
SetupCommands
fi