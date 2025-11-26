{{ config(materialized='table') }}

-- MART: Cardiovascular Risk Analytics Layer
-- This model builds a clean, analytics-ready fact table for ML + Power BI.

with base as (

    select *
    from {{ ref('stg_cardioinsight') }}

),

derived as (

    select
        patient_id,
        
        -- Demographics
        age_years,
        age_days,
        age_band,

        -- Anthropometrics
        height,
        weight,
        bmi,
        bmi_band,

        -- Blood pressure readings
        ap_hi,
        ap_lo,
        (ap_hi - ap_lo) as pulse_pressure,

        -- Clinical categories (mapped from numeric codes)
        cholesterol_level,
        case 
            when cholesterol_level = 1 then 'normal'
            when cholesterol_level = 2 then 'above_normal'
            when cholesterol_level = 3 then 'well_above_normal'
        end as cholesterol_category,

        glucose_level,
        case 
            when glucose_level = 1 then 'normal'
            when glucose_level = 2 then 'above_normal'
            when glucose_level = 3 then 'well_above_normal'
        end as glucose_category,

        -- Behavioral risk factors
        smoke      as smoking,   -- <- map from source column name
        alcohol,                  -- if this errors later, we'll map alco → alcohol
        active,

        -- Date columns
        measure_date,
        measure_month,

        -- Target
        target_cvd as cardiovascular_event

    from base
)

select * from derived
