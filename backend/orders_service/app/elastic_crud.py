from orders_service.Core.elastick_client import es_client
from elasticsearch import ElasticsearchWarning, NotFoundError
from common.logger import logger


async def index_item(doc: dict, index: str):
    try:
        await es_client.index(index=index, id=doc.get("id"), document=doc)
    except ElasticsearchWarning as e:
        _id = doc.get("id")
        logger.error(f"Ошибка при индексации заказа {_id}: {e}")
        raise
    except NotFoundError as e:
        return


async def search_by_term(index: str, **terms) -> list[dict]:
    query = {
        "bool": {"filter": [{"term": {key: value}} for key, value in terms.items()]}
    }
    try:
        response = await es_client.search(index=index, query=query)
        return response["hits"]["hits"]
    except ElasticsearchWarning as e:
        logger.error(f"Elasticsearch search error: {e}")
        raise
    except NotFoundError as e:
        return list()


async def search_by_match_all(index: str, size: int = 1000) -> list[dict]:
    try:
        query = {"query": {"match_all": {}}}
        resp = await es_client.search(index=index, body=query, size=size)
        return resp["hits"]["hits"]
    except ElasticsearchWarning as e:
        logger.error(f"Elasticsearch search error: {e}")
        raise
    except NotFoundError as e:
        return list()


async def delete_item(index: str, item_id: int):
    try:
        await es_client.delete(index=index, id=item_id, ignore=[404])
    except ElasticsearchWarning as e:
        logger.error(f"Ошибка при удалении заказа {item_id}: {e}")
        raise
    except NotFoundError as e:
        return
