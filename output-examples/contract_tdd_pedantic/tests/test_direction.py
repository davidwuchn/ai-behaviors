from snake_game.direction import Direction


class TestDirection:
    def test_four_directions_exist(self):
        assert Direction.UP is not None
        assert Direction.DOWN is not None
        assert Direction.LEFT is not None
        assert Direction.RIGHT is not None

    def test_opposite_pairs(self):
        assert Direction.UP.opposite() is Direction.DOWN
        assert Direction.DOWN.opposite() is Direction.UP
        assert Direction.LEFT.opposite() is Direction.RIGHT
        assert Direction.RIGHT.opposite() is Direction.LEFT

    def test_is_opposite(self):
        assert Direction.UP.is_opposite(Direction.DOWN)
        assert Direction.DOWN.is_opposite(Direction.UP)
        assert Direction.LEFT.is_opposite(Direction.RIGHT)
        assert Direction.RIGHT.is_opposite(Direction.LEFT)

    def test_not_opposite(self):
        assert not Direction.UP.is_opposite(Direction.LEFT)
        assert not Direction.UP.is_opposite(Direction.RIGHT)
        assert not Direction.UP.is_opposite(Direction.UP)
        assert not Direction.LEFT.is_opposite(Direction.UP)
        assert not Direction.LEFT.is_opposite(Direction.DOWN)

    def test_delta(self):
        # UP means row decreases (y goes up)
        assert Direction.UP.delta() == (0, -1)
        assert Direction.DOWN.delta() == (0, 1)
        assert Direction.LEFT.delta() == (-1, 0)
        assert Direction.RIGHT.delta() == (1, 0)

    def test_all_directions(self):
        all_dirs = Direction.all()
        assert len(all_dirs) == 4
        assert set(all_dirs) == {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
