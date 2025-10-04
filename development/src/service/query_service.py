from repository.orm import GroupRepository
from utils.db_connection import get_db_session
from utils.slm_call import SLMService
from utils.vector_search import VectorSearchService

class QueryService:
    def __init__(self):
        self.slm_service = SLMService()
        self.vector_service = VectorSearchService()

    async def process_query(self, query: str, group_id: int = None, k: int = 5):
        """Process user query and return answer"""
        try:
            # Perform vector search
            if group_id:
                search_results = await self.vector_service.search_with_group_filter(
                    query, group_id, k
                )
                async with get_db_session() as session:
                    group_repo = GroupRepository(session)
                    group = await group_repo.get_group_by_id(group_id)
                    group_name = group.name if group else "Unknown"
            else:
                search_results = await self.vector_service.search_all_documents(query, k)
                group_name = "All Documents"

            if not search_results:
                return {
                    "query": query,
                    "answer": "No relevant documents found for your query.",
                    "group_used": group_name,
                    "chunks_found": 0
                }

            # Generate answer using SLM
            context = "\n\n".join([result['content'] for result in search_results])
            answer = await self.slm_service.generate_answer(query, context)

            return {
                "query": query,
                "answer": answer,
                "group_used": group_name,
                "chunks_found": len(search_results)
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")

    async def similarity_search_in_group(self, group_id: int, query: str, k: int = 5):
        """Perform similarity search within a specific group"""
        search_results = await self.vector_service.search_with_group_filter(
            query, group_id, k
        )
        
        return {
            "query": query,
            "group_id": group_id,
            "results": [
                {
                    "content": result['content'],
                    "score": result['score'],
                    "document_id": result['metadata'].get('document_id'),
                    "chunk_index": result['metadata'].get('chunk_index')
                }
                for result in search_results
            ]
        }


    async def find_group(self, query :str, k: int = 1):
        """Find the most relevant group for a given query"""
        try:
            async with get_db_session() as session:
                group_repo = GroupRepository(session)
                group = await group_repo.get_all_groups()
                if not group:
                    return None
                group_details = {grp.id: grp.description for grp in group}
            group_id = await self.slm_service.identify_relevant_group(query, group_details)
            print(f"Identified group ID: {group_id}")
            if group_id is None or group_id == '0':
                return {"group_id": None, "message": "No relevant group found.", "query": query}
            querying = QueryService()
            response = await querying.process_query(query, int(group_id), 5)
            return response

        except Exception as e:
            raise Exception(f"Error processing query while finding group: {str(e)}")