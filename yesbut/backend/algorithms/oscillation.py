"""
Semantic Entropy Calculation

Core algorithm for computing semantic entropy using NLI-based clustering.
Used for uncertainty detection and oscillation monitoring.
"""

from typing import Dict, Any, List, Tuple, Optional
import math
import numpy as np
from collections import defaultdict


class SemanticEntropyCalculator:
    """
    Calculator for semantic entropy using NLI-based clustering.

    Semantic entropy measures the uncertainty in LLM outputs by:
    1. Generating multiple samples for the same query
    2. Clustering semantically equivalent responses using NLI
    3. Computing entropy over the cluster distribution

    Reference: Kuhn et al., "Semantic Uncertainty", ICLR 2023

    High entropy indicates high uncertainty (many different meanings).
    Low entropy indicates high confidence (consistent meaning).

    Attributes:
        nli_model: NLI model for semantic equivalence checking
        num_samples: Number of samples for entropy estimation
        equivalence_threshold: NLI threshold for semantic equivalence
    """

    def __init__(
        self,
        nli_model: Any = None,
        num_samples: int = 5,
        equivalence_threshold: float = 0.7,
    ):
        """
        Initialize the semantic entropy calculator.

        Args:
            nli_model: NLI model for checking semantic equivalence
            num_samples: Number of LLM samples for entropy estimation
            equivalence_threshold: Threshold for NLI entailment score
        """
        self.nli_model = nli_model
        self.num_samples = num_samples
        self.equivalence_threshold = equivalence_threshold

    async def compute_entropy(
        self,
        responses: List[str],
    ) -> float:
        """
        Compute semantic entropy for a set of responses.

        Args:
            responses: List of LLM response strings

        Returns:
            float: Semantic entropy value (0 = certain, higher = uncertain)
        """
        if not responses:
            return 0.0

        # Cluster responses by semantic equivalence
        clusters = await self.cluster_responses(responses)

        # Compute entropy from cluster distribution
        return self.compute_cluster_entropy(clusters, len(responses))

    async def cluster_responses(
        self,
        responses: List[str],
    ) -> List[List[int]]:
        """
        Cluster semantically equivalent responses.

        Uses NLI model to check bidirectional entailment between
        response pairs. Responses that mutually entail are clustered.

        Args:
            responses: List of response strings

        Returns:
            List[List[int]]: Clusters as lists of response indices
        """
        if not responses:
            return []

        n = len(responses)
        if n == 1:
            return [[0]]

        # Build equivalence matrix
        equivalence = [[False] * n for _ in range(n)]
        for i in range(n):
            equivalence[i][i] = True
            for j in range(i + 1, n):
                is_equiv = await self.check_semantic_equivalence(
                    responses[i], responses[j]
                )
                equivalence[i][j] = is_equiv
                equivalence[j][i] = is_equiv

        # Union-find clustering
        parent = list(range(n))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for i in range(n):
            for j in range(i + 1, n):
                if equivalence[i][j]:
                    union(i, j)

        # Group by cluster
        cluster_map = defaultdict(list)
        for i in range(n):
            cluster_map[find(i)].append(i)

        return list(cluster_map.values())

    async def check_semantic_equivalence(
        self,
        response_a: str,
        response_b: str,
    ) -> bool:
        """
        Check if two responses are semantically equivalent.

        Uses bidirectional NLI: A entails B AND B entails A.

        Args:
            response_a: First response
            response_b: Second response

        Returns:
            bool: True if semantically equivalent
        """
        if self.nli_model is None:
            # Fallback: simple string similarity
            return self._simple_similarity(response_a, response_b) > self.equivalence_threshold

        # Check bidirectional entailment
        score_ab = await self._compute_entailment(response_a, response_b)
        score_ba = await self._compute_entailment(response_b, response_a)

        # Both directions must exceed threshold
        return (score_ab >= self.equivalence_threshold and
                score_ba >= self.equivalence_threshold)

    def _simple_similarity(self, text_a: str, text_b: str) -> float:
        """Compute simple word overlap similarity."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    async def _compute_entailment(self, premise: str, hypothesis: str) -> float:
        """Compute NLI entailment score."""
        if self.nli_model is None:
            return self._simple_similarity(premise, hypothesis)

        # Call NLI model
        try:
            result = await self.nli_model.predict(premise, hypothesis)
            return result.get("entailment", 0.0)
        except Exception:
            return self._simple_similarity(premise, hypothesis)

    def compute_cluster_entropy(
        self,
        clusters: List[List[int]],
        total_responses: int,
    ) -> float:
        """
        Compute entropy from cluster distribution.

        H = -sum(p_i * log(p_i)) where p_i = |cluster_i| / total

        Args:
            clusters: List of clusters
            total_responses: Total number of responses

        Returns:
            float: Entropy value
        """
        if not clusters or total_responses == 0:
            return 0.0

        entropy = 0.0
        for cluster in clusters:
            p = len(cluster) / total_responses
            if p > 0:
                entropy -= p * math.log(p)

        return entropy

    async def estimate_uncertainty(
        self,
        query: str,
        llm: Any = None,
    ) -> Dict[str, Any]:
        """
        Estimate uncertainty for a query by sampling LLM.

        Args:
            query: Query to estimate uncertainty for
            llm: LLM to sample from

        Returns:
            Dict containing:
            - entropy: Semantic entropy value
            - num_clusters: Number of semantic clusters
            - cluster_sizes: Size of each cluster
            - is_high_uncertainty: Whether entropy exceeds threshold
        """
        if llm is None:
            return {
                "entropy": 0.0,
                "num_clusters": 0,
                "cluster_sizes": [],
                "is_high_uncertainty": False,
            }

        # Sample responses from LLM
        responses = []
        for _ in range(self.num_samples):
            try:
                response = await llm.generate(query, temperature=0.7)
                responses.append(response)
            except Exception:
                continue

        if not responses:
            return {
                "entropy": 0.0,
                "num_clusters": 0,
                "cluster_sizes": [],
                "is_high_uncertainty": False,
            }

        # Compute entropy
        clusters = await self.cluster_responses(responses)
        entropy = self.compute_cluster_entropy(clusters, len(responses))

        # High uncertainty threshold (log(num_samples) / 2)
        high_threshold = math.log(self.num_samples) / 2

        return {
            "entropy": entropy,
            "num_clusters": len(clusters),
            "cluster_sizes": [len(c) for c in clusters],
            "is_high_uncertainty": entropy > high_threshold,
        }


class OscillationDetector:
    """
    Detector for semantic oscillation in debate rounds.

    Combines embedding similarity and semantic entropy to detect
    when debate is not making progress (paraphrasing without substance).

    Detection signals:
    1. Embedding similarity > threshold for alternating positions
    2. Semantic entropy not decreasing over rounds
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        entropy_decrease_threshold: float = 0.1,
        stagnation_rounds: int = 3,
        embedding_model: Any = None,
    ):
        """
        Initialize the oscillation detector.

        Args:
            similarity_threshold: Threshold for position similarity
            entropy_decrease_threshold: Minimum entropy decrease per round
            stagnation_rounds: Rounds of stagnation before detection
            embedding_model: Model for computing embeddings
        """
        self.similarity_threshold = similarity_threshold
        self.entropy_decrease_threshold = entropy_decrease_threshold
        self.stagnation_rounds = stagnation_rounds
        self.embedding_model = embedding_model
        self.position_history: List[Dict[str, Any]] = []
        self.entropy_history: List[float] = []
        self._embedding_cache: Dict[str, List[float]] = {}

    def record_round(
        self,
        positions: Dict[str, str],
        entropy: float,
    ) -> None:
        """
        Record a debate round.

        Args:
            positions: Map of branch_id to position text
            entropy: Semantic entropy for this round
        """
        self.position_history.append(positions)
        self.entropy_history.append(entropy)

    async def check_oscillation(self) -> Dict[str, Any]:
        """
        Check for oscillation patterns.

        Returns:
            Dict containing:
            - is_oscillating: Whether oscillation detected
            - trigger: 'similarity' or 'entropy_stagnation' or None
            - details: Additional detection details
        """
        # Need at least 3 rounds to detect oscillation
        if len(self.position_history) < 3:
            return {
                "is_oscillating": False,
                "trigger": None,
                "details": {"reason": "insufficient_rounds"},
            }

        # Check for position similarity oscillation
        similarity_result = await self._check_similarity_oscillation()
        if similarity_result["is_oscillating"]:
            return {
                "is_oscillating": True,
                "trigger": "similarity",
                "details": similarity_result,
            }

        # Check for entropy stagnation
        if self.check_entropy_stagnation():
            return {
                "is_oscillating": True,
                "trigger": "entropy_stagnation",
                "details": {
                    "recent_entropy": self.entropy_history[-self.stagnation_rounds:],
                    "threshold": self.entropy_decrease_threshold,
                },
            }

        return {
            "is_oscillating": False,
            "trigger": None,
            "details": {},
        }

    async def _check_similarity_oscillation(self) -> Dict[str, Any]:
        """Check for alternating similar positions."""
        if len(self.position_history) < 3:
            return {"is_oscillating": False}

        # Check if positions alternate (A -> B -> A pattern)
        for branch_id in self.position_history[-1].keys():
            positions = [
                h.get(branch_id, "") for h in self.position_history[-3:]
            ]

            if len(positions) < 3:
                continue

            # Check similarity between round n and round n-2
            sim_0_2 = await self.compute_position_similarity(
                positions[0], positions[2]
            )

            # Check dissimilarity between consecutive rounds
            sim_0_1 = await self.compute_position_similarity(
                positions[0], positions[1]
            )
            sim_1_2 = await self.compute_position_similarity(
                positions[1], positions[2]
            )

            # Oscillation: high similarity between alternating, low between consecutive
            if (sim_0_2 > self.similarity_threshold and
                sim_0_1 < self.similarity_threshold and
                sim_1_2 < self.similarity_threshold):
                return {
                    "is_oscillating": True,
                    "branch_id": branch_id,
                    "similarity_0_2": sim_0_2,
                    "similarity_0_1": sim_0_1,
                    "similarity_1_2": sim_1_2,
                }

        return {"is_oscillating": False}

    async def compute_position_similarity(
        self,
        position_a: str,
        position_b: str,
    ) -> float:
        """
        Compute embedding similarity between positions.

        Args:
            position_a: First position text
            position_b: Second position text

        Returns:
            float: Cosine similarity (0-1)
        """
        if not position_a or not position_b:
            return 0.0

        emb_a = await self._get_embedding(position_a)
        emb_b = await self._get_embedding(position_b)

        if emb_a is None or emb_b is None:
            # Fallback to word overlap
            return self._word_overlap_similarity(position_a, position_b)

        return self._cosine_similarity(emb_a, emb_b)

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text, with caching."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        if self.embedding_model is None:
            return None

        try:
            embedding = await self.embedding_model.embed(text)
            self._embedding_cache[text] = embedding
            return embedding
        except Exception:
            return None

    def _cosine_similarity(
        self,
        vec_a: List[float],
        vec_b: List[float],
    ) -> float:
        """Compute cosine similarity between vectors."""
        a = np.array(vec_a)
        b = np.array(vec_b)

        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot / (norm_a * norm_b))

    def _word_overlap_similarity(self, text_a: str, text_b: str) -> float:
        """Compute word overlap similarity as fallback."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    def check_entropy_stagnation(self) -> bool:
        """
        Check if entropy has stagnated.

        Returns:
            bool: True if entropy not decreasing for stagnation_rounds
        """
        if len(self.entropy_history) < self.stagnation_rounds + 1:
            return False

        recent = self.entropy_history[-self.stagnation_rounds:]
        for i in range(1, len(recent)):
            if recent[i-1] - recent[i] >= self.entropy_decrease_threshold:
                return False

        return True

    def reset(self) -> None:
        """Reset detector state for new debate."""
        self.position_history = []
        self.entropy_history = []
        self._embedding_cache = {}

    def get_convergence_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for convergence monitoring.

        Returns:
            Dict with convergence metrics
        """
        if not self.entropy_history:
            return {
                "rounds": 0,
                "current_entropy": None,
                "entropy_trend": None,
                "convergence_rate": None,
            }

        n = len(self.entropy_history)
        current = self.entropy_history[-1]

        # Compute trend (linear regression slope)
        if n >= 2:
            x = list(range(n))
            y = self.entropy_history
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
            denominator = sum((xi - x_mean) ** 2 for xi in x)
            trend = numerator / denominator if denominator != 0 else 0
        else:
            trend = 0

        # Convergence rate (entropy decrease per round)
        if n >= 2:
            rate = (self.entropy_history[0] - current) / (n - 1)
        else:
            rate = 0

        return {
            "rounds": n,
            "current_entropy": current,
            "entropy_trend": trend,
            "convergence_rate": rate,
            "is_converging": trend < 0,
        }
