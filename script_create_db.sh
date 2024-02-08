-- Create a new database
CREATE DATABASE energy_project;

-- Connect to the new database
\c energy_project;

-- Create table for energy usage
CREATE TABLE energy_usage (
    user_id SERIAL PRIMARY KEY,
    average_monthly_bill DECIMAL,
    average_natural_gas_bill DECIMAL,
    monthly_fuel_bill DECIMAL
);

-- Create table for waste sector
CREATE TABLE waste_sector (
    user_id SERIAL PRIMARY KEY,
    waste_kg DECIMAL,
    recycled_or_composted_kg DECIMAL
);

-- Create table for business travel
CREATE TABLE business_travel (
    user_id SERIAL PRIMARY KEY,
    kilometers_per_year DECIMAL,
    average_efficiency_per_100km DECIMAL
);