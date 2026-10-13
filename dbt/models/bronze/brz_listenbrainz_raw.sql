{{ config(alias='csv_listenbrainz_raw') }}

with source_events as (
    select
        json,
        filename
    from read_ndjson_objects(
        '{{ var("source_glob", "../files/incoming/*.txt") }}',
        filename = true
    )
),

numbered_events as (
    select
        row_number() over (partition by filename order by filename) as record_number,
        json as raw_json,
        regexp_extract(filename, '[^/\\\\]+$') as file_name,
        cast(hash('{{ invocation_id }}') % 9223372036854775807 as bigint) as load_id,
        current_timestamp as load_timestamp
    from source_events
)

select
    record_number,
    raw_json,
    file_name,
    load_id,
    load_timestamp
from numbered_events
