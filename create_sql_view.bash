#!/bin/bash
docker-compose exec postgres_db bash -c "echo 'CREATE VIEW all_flats_last_price AS
    SELECT flat.flat_id, flat.address, flat.floor, flat.rooms, flat.area, flat.finishing,
    flat.settlement_date, flat.url_suffix,
        project.project_id, project.name, project.city, project.url,
        price.price, price.booking_status
    FROM flat
    INNER JOIN project ON flat.project_id = project.project_id
    INNER JOIN price ON price.flat_id = flat.flat_id
    INNER JOIN (
        SELECT flat_id, max(data_created) AS max_data
        FROM price
        GROUP BY flat_id
    ) AS last_price ON last_price.flat_id = price.flat_id
    WHERE price.data_created = last_price.max_data;' | psql -U 'postgres' "
