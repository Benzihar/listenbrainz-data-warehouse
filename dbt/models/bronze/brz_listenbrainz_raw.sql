{{ config(
    alias='csv_listenbrainz_raw',
    materialized='incremental',
    unique_key=['file_name', 'record_number']
) }}

with source_files as (
    select
        filename,
        content
    from read_text(
        -- CI uses committed sample data; use --vars '{source_glob: "../files/incoming/*.txt"}' for full data.
        -- read_ndjson_objects has no per-file row-number option, so split text to retain line ordinality.
        '{{ var("source_glob", "../tests/sample_data/*.json") }}'
    )
),

numbered_events as (
    select
        cast(line_number as bigint) as record_number,
        cast(line as json) as raw_json,
        regexp_extract(filename, '[^/\\\\]+$') as file_name,
        cast(hash('{{ invocation_id }}') % 9223372036854775807 as bigint) as load_id,
        current_timestamp as load_timestamp
    from source_files,
        unnest(string_split(content, chr(10))) with ordinality as lines(line, line_number)
    where trim(line) <> ''
)

select
    record_number,
    raw_json,
    file_name,
    load_id,
    load_timestamp
from numbered_events
{% if is_incremental() %}
where file_name not in (select file_name from {{ this }})
{% endif %}
