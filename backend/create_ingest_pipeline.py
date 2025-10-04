"""
Create Elasticsearch ingest pipeline for Content Discovery enrichment
"""
from elasticsearch import Elasticsearch
import ssl

es = Elasticsearch(
    'https://95.217.117.251:9200/',
    basic_auth=('elastic', 'd41=*sDuOnhQqXonYz2U'),
    verify_certs=False,
    ssl_show_warn=False
)

# Create ingest pipeline with proper escaping
pipeline = {
    "description": "Enrich planning applications for Content Discovery feature",
    "processors": [
        {
            "script": {
                "description": "Generate authority_slug from area_name",
                "lang": "painless",
                "source": """
if (ctx.area_name != null) {
    ctx.authority_slug = ctx.area_name.toLowerCase().replace(' ', '-').replace('_', '-');
}
"""
            }
        },
        {
            "script": {
                "description": "Generate location_slug from postcode or area_name",
                "lang": "painless",
                "source": """
if (ctx.postcode != null) {
    ctx.location_slug = ctx.postcode.toLowerCase().replace(' ', '-');
} else if (ctx.area_name != null) {
    ctx.location_slug = ctx.area_name.toLowerCase().replace(' ', '-');
}
"""
            }
        },
        {
            "script": {
                "description": "Calculate decision_days from dates",
                "lang": "painless",
                "source": """
if (ctx.decided_date != null && ctx.start_date != null) {
    ZonedDateTime decided = ZonedDateTime.parse(ctx.decided_date);
    ZonedDateTime started = ZonedDateTime.parse(ctx.start_date);
    ctx.decision_days = ChronoUnit.DAYS.between(started, decided);
}
"""
            }
        },
        {
            "script": {
                "description": "Set is_approved from app_state",
                "lang": "painless",
                "source": """
if (ctx.app_state != null) {
    if (ctx.app_state == 'Permitted' || ctx.app_state == 'Conditions') {
        ctx.is_approved = true;
    } else if (ctx.app_state == 'Rejected' || ctx.app_state == 'Withdrawn') {
        ctx.is_approved = false;
    }
}
"""
            }
        }
    ]
}

try:
    result = es.ingest.put_pipeline(id='content_discovery_enrichment', body=pipeline)
    print('✅ Ingest pipeline created successfully')
    print('Acknowledged:', result.get('acknowledged', False))
except Exception as e:
    print(f'❌ Failed to create pipeline: {e}')
