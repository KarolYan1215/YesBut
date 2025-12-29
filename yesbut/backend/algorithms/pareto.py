"""
Pareto Optimization Algorithm

Multi-objective Pareto optimization for filtering phase.
Identifies non-dominated solutions on the Pareto front.
"""

from typing import Dict, Any, List, Tuple, Optional
import math


class ParetoOptimizer:
    """
    Multi-objective Pareto optimizer for solution filtering.

    Implements Pareto dominance checking and front extraction
    for the filtering phase of the three-phase pipeline.

    A solution A dominates solution B if:
    - A is at least as good as B in all objectives
    - A is strictly better than B in at least one objective

    The Pareto front contains all non-dominated solutions.

    Attributes:
        objectives: List of objective names
        directions: Optimization direction per objective ('max' or 'min')
    """

    def __init__(
        self,
        objectives: List[str],
        directions: List[str] = None,
    ):
        """
        Initialize the Pareto optimizer.

        Args:
            objectives: List of objective names (e.g., ['feasibility', 'value', 'novelty'])
            directions: Optimization direction per objective (default: all 'max')
        """
        self.objectives = objectives
        self.directions = directions or ['max'] * len(objectives)

    def dominates(
        self,
        solution_a: Dict[str, float],
        solution_b: Dict[str, float],
    ) -> bool:
        """
        Check if solution A dominates solution B.

        Args:
            solution_a: Objective values for solution A
            solution_b: Objective values for solution B

        Returns:
            bool: True if A dominates B
        """
        strictly_better = False

        for obj, direction in zip(self.objectives, self.directions):
            a_val = solution_a.get(obj, 0)
            b_val = solution_b.get(obj, 0)

            if direction == 'max':
                if a_val < b_val:
                    return False
                if a_val > b_val:
                    strictly_better = True
            else:  # min
                if a_val > b_val:
                    return False
                if a_val < b_val:
                    strictly_better = True

        return strictly_better

    def compute_pareto_front(
        self,
        solutions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Compute the Pareto front from a set of solutions.

        Args:
            solutions: List of solutions with objective values

        Returns:
            List[Dict]: Non-dominated solutions on Pareto front
        """
        if not solutions:
            return []

        pareto_front = []

        for candidate in solutions:
            is_dominated = False

            for other in solutions:
                if other is candidate:
                    continue

                if self.dominates(other, candidate):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(candidate)

        return pareto_front

    def compute_hypervolume(
        self,
        pareto_front: List[Dict[str, Any]],
        reference_point: Dict[str, float],
    ) -> float:
        """
        Compute hypervolume indicator for Pareto front.

        Hypervolume measures the volume of objective space
        dominated by the Pareto front.

        Uses inclusion-exclusion principle for 2D/3D cases,
        and Monte Carlo estimation for higher dimensions.

        Args:
            pareto_front: Solutions on Pareto front
            reference_point: Reference point for hypervolume calculation

        Returns:
            float: Hypervolume value
        """
        if not pareto_front:
            return 0.0

        n_objectives = len(self.objectives)

        if n_objectives == 2:
            return self._compute_hypervolume_2d(pareto_front, reference_point)
        elif n_objectives == 3:
            return self._compute_hypervolume_3d(pareto_front, reference_point)
        else:
            return self._compute_hypervolume_monte_carlo(pareto_front, reference_point)

    def _compute_hypervolume_2d(
        self,
        pareto_front: List[Dict[str, Any]],
        reference_point: Dict[str, float],
    ) -> float:
        """Compute 2D hypervolume using sweep line algorithm."""
        obj1, obj2 = self.objectives[0], self.objectives[1]
        dir1, dir2 = self.directions[0], self.directions[1]

        # Normalize directions (convert min to max by negating)
        points = []
        for sol in pareto_front:
            x = sol.get(obj1, 0) if dir1 == 'max' else -sol.get(obj1, 0)
            y = sol.get(obj2, 0) if dir2 == 'max' else -sol.get(obj2, 0)
            points.append((x, y))

        ref_x = reference_point.get(obj1, 0) if dir1 == 'max' else -reference_point.get(obj1, 0)
        ref_y = reference_point.get(obj2, 0) if dir2 == 'max' else -reference_point.get(obj2, 0)

        # Sort by first objective descending
        points.sort(key=lambda p: p[0], reverse=True)

        hypervolume = 0.0
        prev_y = ref_y

        for x, y in points:
            if x > ref_x and y > ref_y:
                hypervolume += (x - ref_x) * (y - prev_y)
                prev_y = y

        return hypervolume

    def _compute_hypervolume_3d(
        self,
        pareto_front: List[Dict[str, Any]],
        reference_point: Dict[str, float],
    ) -> float:
        """Compute 3D hypervolume using WFG algorithm approximation."""
        # Simplified 3D hypervolume using slicing
        obj1, obj2, obj3 = self.objectives[0], self.objectives[1], self.objectives[2]

        points = []
        for sol in pareto_front:
            x = sol.get(obj1, 0)
            y = sol.get(obj2, 0)
            z = sol.get(obj3, 0)
            points.append((x, y, z))

        ref = (
            reference_point.get(obj1, 0),
            reference_point.get(obj2, 0),
            reference_point.get(obj3, 0),
        )

        # Sort by z-coordinate
        points.sort(key=lambda p: p[2], reverse=True)

        hypervolume = 0.0
        prev_z = ref[2]
        accumulated_2d = []

        for x, y, z in points:
            if z > ref[2]:
                # Compute 2D hypervolume at this z-slice
                accumulated_2d.append((x, y))
                slice_hv = self._compute_2d_area(accumulated_2d, (ref[0], ref[1]))
                hypervolume += slice_hv * (z - prev_z)
                prev_z = z

        return hypervolume

    def _compute_2d_area(
        self,
        points: List[Tuple[float, float]],
        reference: Tuple[float, float],
    ) -> float:
        """Compute 2D dominated area."""
        if not points:
            return 0.0

        # Sort by x descending
        sorted_points = sorted(points, key=lambda p: p[0], reverse=True)

        area = 0.0
        prev_y = reference[1]

        for x, y in sorted_points:
            if x > reference[0] and y > reference[1]:
                area += (x - reference[0]) * (y - prev_y)
                prev_y = max(prev_y, y)

        return area

    def _compute_hypervolume_monte_carlo(
        self,
        pareto_front: List[Dict[str, Any]],
        reference_point: Dict[str, float],
        n_samples: int = 10000,
    ) -> float:
        """Compute hypervolume using Monte Carlo estimation."""
        import random

        # Find bounding box
        bounds = {}
        for obj in self.objectives:
            values = [sol.get(obj, 0) for sol in pareto_front]
            ref_val = reference_point.get(obj, 0)
            bounds[obj] = (ref_val, max(values))

        # Compute bounding box volume
        box_volume = 1.0
        for obj in self.objectives:
            box_volume *= bounds[obj][1] - bounds[obj][0]

        if box_volume <= 0:
            return 0.0

        # Monte Carlo sampling
        dominated_count = 0
        for _ in range(n_samples):
            # Sample random point in bounding box
            sample = {}
            for obj in self.objectives:
                sample[obj] = random.uniform(bounds[obj][0], bounds[obj][1])

            # Check if dominated by any solution
            for sol in pareto_front:
                if self._point_dominated_by(sample, sol):
                    dominated_count += 1
                    break

        return box_volume * (dominated_count / n_samples)

    def _point_dominated_by(
        self,
        point: Dict[str, float],
        solution: Dict[str, Any],
    ) -> bool:
        """Check if a point is dominated by a solution."""
        for obj, direction in zip(self.objectives, self.directions):
            p_val = point.get(obj, 0)
            s_val = solution.get(obj, 0)

            if direction == 'max':
                if p_val > s_val:
                    return False
            else:
                if p_val < s_val:
                    return False

        return True

    def compute_crowding_distance(
        self,
        pareto_front: List[Dict[str, Any]],
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Compute crowding distance for diversity preservation.

        Crowding distance measures how isolated a solution is
        in objective space. Used for selection when front is too large.

        Args:
            pareto_front: Solutions on Pareto front

        Returns:
            List[Tuple]: Solutions with their crowding distances
        """
        if len(pareto_front) <= 2:
            return [(sol, float('inf')) for sol in pareto_front]

        n = len(pareto_front)
        distances = [0.0] * n

        for obj in self.objectives:
            # Sort by this objective
            sorted_indices = sorted(
                range(n),
                key=lambda i: pareto_front[i].get(obj, 0)
            )

            # Boundary solutions get infinite distance
            distances[sorted_indices[0]] = float('inf')
            distances[sorted_indices[-1]] = float('inf')

            # Get objective range
            obj_min = pareto_front[sorted_indices[0]].get(obj, 0)
            obj_max = pareto_front[sorted_indices[-1]].get(obj, 0)
            obj_range = obj_max - obj_min

            if obj_range == 0:
                continue

            # Compute crowding distance contribution
            for i in range(1, n - 1):
                prev_val = pareto_front[sorted_indices[i - 1]].get(obj, 0)
                next_val = pareto_front[sorted_indices[i + 1]].get(obj, 0)
                distances[sorted_indices[i]] += (next_val - prev_val) / obj_range

        return [(pareto_front[i], distances[i]) for i in range(n)]

    def filter_solutions(
        self,
        solutions: List[Dict[str, Any]],
        max_solutions: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Filter solutions using Pareto dominance and crowding.

        First extracts Pareto front, then uses crowding distance
        to select diverse subset if front is too large.

        Args:
            solutions: All candidate solutions
            max_solutions: Maximum solutions to return

        Returns:
            List[Dict]: Filtered solutions
        """
        pareto_front = self.compute_pareto_front(solutions)

        if len(pareto_front) <= max_solutions:
            return pareto_front

        # Use crowding distance to select diverse subset
        with_distance = self.compute_crowding_distance(pareto_front)
        with_distance.sort(key=lambda x: x[1], reverse=True)

        return [sol for sol, _ in with_distance[:max_solutions]]

    def rank_solutions(
        self,
        solutions: List[Dict[str, Any]],
    ) -> List[Tuple[Dict[str, Any], int]]:
        """
        Rank solutions by Pareto dominance layers.

        Layer 0 = Pareto front
        Layer 1 = Front after removing layer 0
        etc.

        Args:
            solutions: All solutions to rank

        Returns:
            List[Tuple]: Solutions with their rank (layer number)
        """
        if not solutions:
            return []

        remaining = list(solutions)
        ranked = []
        rank = 0

        while remaining:
            # Find current Pareto front
            front = self.compute_pareto_front(remaining)

            # Assign rank to front solutions
            for sol in front:
                ranked.append((sol, rank))
                remaining.remove(sol)

            rank += 1

        return ranked

    def compute_contribution(
        self,
        solution: Dict[str, Any],
        pareto_front: List[Dict[str, Any]],
        reference_point: Dict[str, float],
    ) -> float:
        """
        Compute hypervolume contribution of a solution.

        The contribution is the hypervolume lost if this solution
        is removed from the front.

        Args:
            solution: Solution to compute contribution for
            pareto_front: Current Pareto front
            reference_point: Reference point for hypervolume

        Returns:
            float: Hypervolume contribution
        """
        if solution not in pareto_front:
            return 0.0

        hv_with = self.compute_hypervolume(pareto_front, reference_point)

        front_without = [s for s in pareto_front if s is not solution]
        hv_without = self.compute_hypervolume(front_without, reference_point)

        return hv_with - hv_without
