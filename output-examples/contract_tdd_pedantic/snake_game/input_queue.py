from collections import deque

from snake_game.direction import Direction


class InputQueue:
    """Queue of pending direction changes with self-collision filtering.

    Invariant: no adjacent pair of directions in the queue (including
    current_direction as predecessor of the first element) are opposites.

    Contract:
        Pre (enqueue): direction is a valid Direction.
        Post (enqueue): direction is appended only if it's not opposite to the
            effective last direction (last queued, or current if queue empty).
        Pre (pop): none.
        Post (pop): if non-empty, returns the next direction and updates
            current_direction to match. If empty, returns None and
            current_direction is unchanged.
    """

    def __init__(self, current_direction: Direction) -> None:
        assert isinstance(current_direction, Direction), (
            f"Pre violated: current_direction must be a Direction, got {type(current_direction)}"
        )
        self._current: Direction = current_direction
        self._queue: deque[Direction] = deque()

    def enqueue(self, direction: Direction) -> None:
        assert isinstance(direction, Direction), (
            f"Pre violated: direction must be a Direction, got {type(direction)}"
        )
        effective_last = self._queue[-1] if self._queue else self._current
        if direction.is_opposite(effective_last):
            return
        self._queue.append(direction)

    def pop(self) -> Direction | None:
        """Pop the next queued direction, or None if empty.

        Post: if returned non-None, self._current is updated to that direction.
        """
        if not self._queue:
            return None
        direction = self._queue.popleft()
        self._current = direction
        return direction

    def clear(self) -> None:
        self._queue.clear()

    def reset(self, current_direction: Direction) -> None:
        """Reset queue with a new current direction.

        Post: queue is empty, current direction is updated.
        """
        assert isinstance(current_direction, Direction), (
            f"Pre violated: current_direction must be a Direction, got {type(current_direction)}"
        )
        self._queue.clear()
        self._current = current_direction
        assert len(self._queue) == 0, "Post violated: queue must be empty after reset"
