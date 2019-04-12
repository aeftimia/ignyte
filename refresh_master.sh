while true
do
    PGPASSWORD=$ignyte_db_password psql -U $ignyte_db_username $ignyte_db -c "select master_refresh();";
    sleep 45;
done
