{{ config(materialized='view') }}

-- Staging model: direct exposure of the de-identified lake file into DuckDB
-- We keep all columns as-is from the lake for now.

select
    *
from read_csv_auto('../data/lake/cardio_deid_data.csv')
