while true
do
    PGPASSWORD=$ignyte_db_password psql -U $ignyte_db_username $ignyte_db -c "select record();"
    sleep 30;
done
