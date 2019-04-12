while true
do
    psql ignyte -c "select master_refresh();";
    sleep 45;
done
