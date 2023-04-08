-- Создание таблиц через данный файл
-- с целью создать представление CREATE VIEW all_flats_last_price
-- на основе данных таблиц.
-- (python manage.py sqlmigrate flats 0001_initial)
--
BEGIN;
--
-- Create model Flat
--
CREATE TABLE "flat" (
    "flat_id" integer NOT NULL PRIMARY KEY,
    "address" varchar(255) NULL,
    "floor" integer NULL,
    "rooms" integer NULL,
    "area" double precision NULL,
    "finishing" boolean NULL,
    "bulk" varchar(127) NULL,
    "settlement_date" date NULL,
    "url_suffix" varchar(127) NOT NULL,
    "data_created" date NOT NULL,
    "data_closed" date NULL
    );
--
-- Create model Project
--
CREATE TABLE "project" (
    "project_id" integer NOT NULL PRIMARY KEY,
    "city" varchar(127) NOT NULL,
    "name" varchar(127) NOT NULL,
    "url" varchar(255) NULL,
    "metro" varchar(127) NULL,
    "time_to_metro" integer NULL,
    "latitude" double precision NULL,
    "longitude" double precision NULL,
    "address" varchar(255) NULL,
    "data_created" date NOT NULL,
    "data_closed" date NULL
    );
--
-- Create model Price
--
CREATE TABLE "price" (
    "price_id" integer NOT NULL PRIMARY KEY,
    "benefit_name" varchar(127) NULL,
    "benefit_description" varchar(255) NULL,
    "price" integer NOT NULL,
    "meter_price" integer NULL,
    "booking_status" varchar(15) NULL,
    "data_created" date NOT NULL,
    "flat_id" integer NOT NULL
    );
--
-- Add field project to flat
--
ALTER TABLE "flat" ADD COLUMN "project_id" integer NOT NULL CONSTRAINT "flat_project_id_8419c3a9_fk_project_project_id" REFERENCES "project"("project_id") DEFERRABLE INITIALLY DEFERRED;
    SET CONSTRAINTS "flat_project_id_8419c3a9_fk_project_project_id" IMMEDIATE;
ALTER TABLE "price" ADD CONSTRAINT "price_flat_id_92b47ccc_fk_flat_flat_id" FOREIGN KEY ("flat_id") REFERENCES "flat" ("flat_id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "price_flat_id_92b47ccc" ON "price" ("flat_id");
CREATE INDEX "flat_project_id_8419c3a9" ON "flat" ("project_id");
COMMIT;
--
-- Create VIEW all_flats_last_price
--
CREATE VIEW all_flats_last_price AS
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
    WHERE price.data_created = last_price.max_data;