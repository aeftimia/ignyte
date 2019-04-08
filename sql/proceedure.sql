create or replace function record()
returns void as $$
DECLARE
counter integer := 0;
faulty_indicator integer;
c record;
location record;
sensor record;
begin
    for c in select mod(count(*), 3 * 105) as b from sensor_readings loop
        faulty_indicator := c.b;
    end loop;
    for location in (select distinct location_id from
        (select location_id from machine_lookup_table order by random()) as temp) loop
        for sensor in
            select distinct sensor_id
            from sensor_lookup_table
            inner join machine_lookup_table
            using(machine_id)
            where machine_lookup_table.location_id = location.location_id loop
            if faulty_indicator = 0 and counter < 2 then
                insert into sensor_readings
                select sensor.sensor_id, random() * 0.4 + 0.5;
            else
                insert into sensor_readings
                select sensor.sensor_id, random() * 0.5;
            end if;
        end loop;
        counter := counter + 1 ; 
    end loop;
end;
$$ LANGUAGE plpgsql;
