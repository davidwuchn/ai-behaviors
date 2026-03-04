from snake_game.direction import Direction
from snake_game.input_queue import InputQueue


class TestInputQueue:
    def test_empty_queue_returns_none(self):
        q = InputQueue(Direction.RIGHT)
        assert q.pop() is None

    def test_enqueue_and_pop_valid_direction(self):
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        assert q.pop() is Direction.UP

    def test_pop_removes_from_queue(self):
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.pop()
        assert q.pop() is None

    def test_rejects_opposite_of_current_direction(self):
        # Moving right, can't go left
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.LEFT)
        assert q.pop() is None

    def test_rejects_opposite_of_last_queued_direction(self):
        # Moving right, queue up, then try down (opposite of up)
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.enqueue(Direction.DOWN)  # rejected: opposite of UP (last queued)
        assert q.pop() is Direction.UP
        assert q.pop() is None

    def test_stacking_multiple_valid_moves(self):
        # Moving right, queue up then left (valid: left is not opposite of up)
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.enqueue(Direction.LEFT)
        assert q.pop() is Direction.UP
        assert q.pop() is Direction.LEFT

    def test_pop_updates_current_direction(self):
        # After popping UP, current becomes UP, so DOWN should be rejected
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.pop()  # current is now UP
        q.enqueue(Direction.DOWN)  # opposite of UP
        assert q.pop() is None

    def test_rejects_same_as_current_direction(self):
        # Moving right, pressing right again is pointless but harmless
        # Actually, pressing the same direction shouldn't be rejected —
        # it's a no-op from the game's perspective but not harmful.
        # Let's allow it.
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.RIGHT)
        assert q.pop() is Direction.RIGHT

    def test_complex_stacking_scenario(self):
        # Moving RIGHT. Queue: UP, LEFT, DOWN, RIGHT
        # UP: valid (not opposite of RIGHT)
        # LEFT: valid (not opposite of UP)
        # DOWN: valid (not opposite of LEFT)
        # RIGHT: valid (not opposite of DOWN)
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.enqueue(Direction.LEFT)
        q.enqueue(Direction.DOWN)
        q.enqueue(Direction.RIGHT)
        assert q.pop() is Direction.UP
        assert q.pop() is Direction.LEFT
        assert q.pop() is Direction.DOWN
        assert q.pop() is Direction.RIGHT
        assert q.pop() is None

    def test_clear_empties_queue(self):
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.enqueue(Direction.LEFT)
        q.clear()
        assert q.pop() is None

    def test_reset_sets_new_current_direction(self):
        q = InputQueue(Direction.RIGHT)
        q.enqueue(Direction.UP)
        q.reset(Direction.DOWN)
        # Queue should be cleared and current direction is DOWN
        assert q.pop() is None
        # Now LEFT should be rejected (opposite of... no, LEFT is not opposite of DOWN)
        q.enqueue(Direction.UP)  # opposite of DOWN, rejected
        assert q.pop() is None
        q.enqueue(Direction.LEFT)
        assert q.pop() is Direction.LEFT
