from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import (
    Distance,
    Filter,
    PointIdsList,
    PointStruct,
    VectorParams,
)
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.services.product_service import ProductService


class AiService:
    def __init__(
        self,
        session: AsyncSession,
        qdrant_client: AsyncQdrantClient,
        embeddings: Embeddings,
        llm: ChatOpenAI,
        collection_name: str,
        product_service: ProductService,
    ) -> None:
        self.session = session
        self.qdrant_client = qdrant_client
        self.embeddings = embeddings
        self.llm = llm
        self.product_service = product_service
        self.collection_name = collection_name

    async def initialize(self) -> None:
        self.vector_size = await self._get_vector_len()
        await self._create_collection(self.collection_name)

    async def _get_vector_len(self) -> int:
        # узнаем длину вектора, конкретной embedding модели
        vector = await self.embeddings.aembed_query("Check_len")
        return len(vector)

    # Создаем коллекцию, model - для описания данных и настроек( я думаю ее можно вынести куда то отдельно)
    async def _create_collection(self, collection_name: str):
        if not await self.qdrant_client.collection_exists(collection_name):
            await self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,  # Количество чисел в векторе(после создания сможет работать только с таким же числом, то есть с такой же моделью)
                    distance=models.Distance.COSINE,  # Способ сравнения векторов
                ),
            )

        return collection_name

    async def search_in_qdrant(
        self,
        query: str,
        limit: int = 3,
    ) -> list:
        query_vector = await self.embeddings.aembed_query(query)

        res = await self.qdrant_client.query_points(
            self.collection_name, query_vector, limit=limit
        )
        result = []

        for point in res.points:
            if point.payload is not None:
                result.append(point.payload)

        return result

    async def invoke_llm(
        self,
        query: str,
        system: str,
        context: str = "",
    ):
        answer = await self.llm.ainvoke(
            [
                (
                    "system",
                    f"{system}",
                ),
                ("human", f" контекст:{context}, Вопрос: {query}"),
            ]
        )
        return answer.text

    ###########
    async def syncronize_bd_products_in_qdrant(self):
        all_products = await self.product_service.get_all_products()
        await self.session.commit()

        if not await self.qdrant_client.collection_exists(self.collection_name):
            await self.initialize()

        all_qdrant_products = []
        offset = None

        while True:
            point_list, offset = await self.qdrant_client.scroll(
                self.collection_name,
                scroll_filter=Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.source_type",
                            match=models.MatchValue(value="product"),
                        )
                    ]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            all_qdrant_products.extend(point_list)
            if offset is None:
                break

        # Позволяет найти точку Qdrant по ID продукта из PostgreSQL.
        qdrant_by_product_id = {
            point.payload["metadata"]["product_id"]: point
            for point in all_qdrant_products
            if point.payload is not None
        }

        to_upsert = []

        for product in all_products:
            payload = {
                "page_content": (
                    f"Название: {product.title}\nОписание: {product.description}"
                ),
                "metadata": {
                    "source_type": "product",
                    "product_id": product.id,
                    "category_id": product.category_id,
                    "price": str(product.price),
                    "quantity": product.quantity,
                },
            }

            # Получаем точку и убираем её из словаря.
            old_point = qdrant_by_product_id.pop(product.id, None)

            if old_point is not None:
                old_payload = old_point.payload or {}

                # Ничего не изменилось.
                if old_payload == payload:
                    continue

                # Текст прежний: обновляем данные, сохраняя вектор.
                if old_payload.get("page_content") == payload["page_content"]:
                    await self.qdrant_client.overwrite_payload(
                        self.collection_name,
                        payload=payload,
                        points=[old_point.id],
                        wait=True,
                    )
                    continue

            # Для обновления сохраняем ID, для новой точки создаём UUID.
            point_id = (
                old_point.id
                if old_point is not None
                else str(uuid5(NAMESPACE_URL, f"marketplace:product:{product.id}"))
            )
            to_upsert.append((point_id, payload))

        # Новые и изменённые тексты обрабатываем вместе, пачками по 100.
        for start in range(0, len(to_upsert), 100):
            batch = to_upsert[start : start + 100]

            vectors = await self.embeddings.aembed_documents(
                [payload["page_content"] for _, payload in batch]
            )

            points = [
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                for (point_id, payload), vector in zip(batch, vectors, strict=True)
            ]

            await self.qdrant_client.upsert(
                self.collection_name,
                points=points,
                wait=True,
            )

        # Оставшиеся точки не встретились в актуальном списке PostgreSQL.
        if qdrant_by_product_id:
            await self.qdrant_client.delete(
                self.collection_name,
                points_selector=models.PointIdsList(
                    points=[point.id for point in qdrant_by_product_id.values()]
                ),
                wait=True,
            )
