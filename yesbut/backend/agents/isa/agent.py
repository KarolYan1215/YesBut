"""
Information Scout Agent (ISA)

Retrieves external facts via MCP protocol and validates using semantic entropy.
All facts must come from external sources - LLM internal knowledge is prohibited.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional
from datetime import datetime
import uuid
import math
import asyncio

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class InformationScoutAgent(BaseAgent):
    """
    Information Scout Agent for retrieving and validating external facts.

    Core Principle: NEVER use LLM internal knowledge as fact source.
    All facts must be externally verified through MCP servers.
    """

    DEFAULT_PROVIDERS = ["tavily", "brave", "semantic_scholar"]

    def __init__(self, agent_id: str, llm_client=None, mcp_client=None, streaming_callback=None,
                 entropy_threshold: float = 0.5, min_sources: int = 3):
        super().__init__(agent_id=agent_id, agent_type="ISA", agent_name="Information Scout Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.mcp_client = mcp_client
        self.entropy_threshold = entropy_threshold
        self.min_sources = min_sources
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("generate_queries", """Generate {num_queries} optimized search queries for: {query}
Each query should target different aspects or phrasings. Respond as JSON array of strings.""")

        self.register_prompt("extract_facts", """Extract factual claims from the following search results:
{results}
For each fact, provide: content, confidence (0-1), source_url. Respond as JSON array.""")

        self.register_prompt("validate_claim", """Validate this claim against the evidence:
Claim: {claim}
Evidence: {evidence}
Respond with: is_supported (bool), confidence (0-1), reasoning.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        query = input_data.get("query", "")
        search_depth = input_data.get("search_depth", "basic")

        await self.think(f"Searching for: {query}")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"query": query, "depth": search_depth}}

        queries = await self.generate_search_queries(query, num_queries=3)
        yield {"type": "queries_generated", "data": {"queries": queries}}

        results = await self.search_multiple_sources(queries)
        yield {"type": "search_completed", "data": {"result_count": len(results)}}

        entropy_result = await self.compute_semantic_entropy(results)
        yield {"type": "entropy_computed", "data": entropy_result}

        if entropy_result.get("is_high_uncertainty") and search_depth == "deep":
            additional_results = await self.deep_retrieval(query, results)
            results.extend(additional_results)
            yield {"type": "deep_retrieval_completed", "data": {"additional_count": len(additional_results)}}

        facts_created = 0
        for cluster in entropy_result.get("clusters", []):
            if len(cluster) >= self.min_sources:
                validation = await self.cross_validate_fact(cluster[0].get("content", ""), cluster)
                if validation.get("is_validated"):
                    fact_node = await self.create_fact_node(
                        content=cluster[0].get("content", ""),
                        sources=cluster,
                        confidence=validation.get("confidence", 0.5),
                        search_query=query
                    )
                    yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": fact_node}}
                    facts_created += 1

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"facts_created": facts_created, "total_results": len(results)}}

    async def generate_search_queries(self, natural_query: str, num_queries: int = 3) -> List[str]:
        """Generate optimized search queries from natural language."""
        if self.llm_client is None:
            return [natural_query, f"{natural_query} facts", f"{natural_query} research"]

        prompt = self.get_prompt("generate_queries", query=natural_query, num_queries=num_queries)
        response_text = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response_text += chunk

        try:
            import json
            start, end = response_text.find("["), response_text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass
        return [natural_query]

    async def search_multiple_sources(self, queries: List[str], providers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Execute searches across multiple MCP providers."""
        providers = providers or self.DEFAULT_PROVIDERS
        all_results = []

        if self.mcp_client is None:
            for i, query in enumerate(queries):
                all_results.append({
                    "id": str(uuid.uuid4()),
                    "content": f"Mock result for: {query}",
                    "source": "mock_provider",
                    "url": f"https://example.com/result/{i}",
                    "confidence": 0.7,
                })
            return all_results

        for provider in providers:
            for query in queries:
                try:
                    results = await self._search_provider(provider, query)
                    all_results.extend(results)
                except Exception as e:
                    self.log("warning", f"Search failed for {provider}: {e}")

        return self._deduplicate_results(all_results)

    async def _search_provider(self, provider: str, query: str) -> List[Dict[str, Any]]:
        """Search a specific MCP provider."""
        if self.mcp_client is None:
            return []

        try:
            if hasattr(self.mcp_client, 'search'):
                results = await self.mcp_client.search(provider=provider, query=query)
                return [{"id": str(uuid.uuid4()), "content": r.get("content", ""), "source": provider,
                         "url": r.get("url", ""), "title": r.get("title", "")} for r in results]
        except Exception:
            pass
        return []

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity."""
        seen_content = set()
        unique_results = []
        for result in results:
            content_key = result.get("content", "")[:100].lower()
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
        return unique_results

    async def compute_semantic_entropy(self, results: List[Dict[str, Any]], num_samples: int = 5) -> Dict[str, Any]:
        """Compute semantic entropy for retrieved results."""
        if not results:
            return {"entropy": 0.0, "clusters": [], "is_high_uncertainty": False}

        clusters = self._cluster_by_similarity(results)
        total = len(results)
        entropy = 0.0

        for cluster in clusters:
            p = len(cluster) / total
            if p > 0:
                entropy -= p * math.log(p)

        return {
            "entropy": entropy,
            "clusters": clusters,
            "num_clusters": len(clusters),
            "is_high_uncertainty": entropy > self.entropy_threshold,
        }

    def _cluster_by_similarity(self, results: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Cluster results by content similarity."""
        if not results:
            return []

        clusters = []
        used = set()

        for i, result in enumerate(results):
            if i in used:
                continue
            cluster = [result]
            used.add(i)

            for j, other in enumerate(results[i+1:], start=i+1):
                if j in used:
                    continue
                if self._compute_similarity(result.get("content", ""), other.get("content", "")) > 0.5:
                    cluster.append(other)
                    used.add(j)

            clusters.append(cluster)

        return clusters

    def _compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute simple word overlap similarity."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        return intersection / union if union > 0 else 0.0

    async def cross_validate_fact(self, claim: str, initial_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cross-validate a fact claim against multiple independent sources."""
        supporting = []
        conflicting = []

        for source in initial_sources:
            source_content = source.get("content", "")
            similarity = self._compute_similarity(claim, source_content)
            if similarity > 0.3:
                supporting.append(source)
            elif similarity < 0.1 and source_content:
                conflicting.append(source)

        is_validated = len(supporting) >= self.min_sources
        confidence = len(supporting) / (len(supporting) + len(conflicting) + 1)

        return {
            "is_validated": is_validated,
            "confidence": min(1.0, confidence),
            "supporting_sources": supporting,
            "conflicting_sources": conflicting,
            "support_count": len(supporting),
            "conflict_count": len(conflicting),
        }

    async def create_fact_node(self, content: str, sources: List[Dict[str, Any]], confidence: float, search_query: str) -> Dict[str, Any]:
        """Create a FactNode with complete source attribution."""
        return {
            "id": str(uuid.uuid4()),
            "type": "fact",
            "content": content,
            "layer": 3,
            "branch_id": None,
            "parent_id": None,
            "confidence": confidence,
            "utility": confidence * 0.8,
            "sensitivity": None,
            "metadata": {
                "sources": [{"url": s.get("url", ""), "title": s.get("title", ""), "provider": s.get("source", "")} for s in sources[:5]],
                "search_query": search_query,
                "source_count": len(sources),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": self.agent_id,
            },
        }

    async def deep_retrieval(self, query: str, initial_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform deep retrieval when initial results have high uncertainty."""
        additional_results = []

        expanded_queries = [f"{query} detailed", f"{query} evidence", f"{query} study"]
        for eq in expanded_queries:
            results = await self.search_multiple_sources([eq], providers=["semantic_scholar"])
            additional_results.extend(results)

        urls_to_crawl = [r.get("url") for r in initial_results if r.get("url")][:3]
        for url in urls_to_crawl:
            if self.mcp_client and hasattr(self.mcp_client, 'crawl'):
                try:
                    crawled = await self.mcp_client.crawl(url)
                    if crawled:
                        additional_results.append({
                            "id": str(uuid.uuid4()),
                            "content": crawled.get("content", "")[:500],
                            "source": "crawl",
                            "url": url,
                        })
                except Exception:
                    pass

        return self._deduplicate_results(additional_results)
