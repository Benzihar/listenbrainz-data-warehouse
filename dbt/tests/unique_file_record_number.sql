select
    file_name,
    record_number
from {{ ref('brz_listenbrainz_raw') }}
group by file_name, record_number
having count(*) > 1
