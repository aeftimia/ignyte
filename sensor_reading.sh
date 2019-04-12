while true
do
    psql ignyte -c "select record();"
    sleep 30;
done
