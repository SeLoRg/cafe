from elasticsearch import AsyncElasticsearch
from .config import settings

es_client = AsyncElasticsearch(
    hosts=[settings.elastic_url],
    basic_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
)
