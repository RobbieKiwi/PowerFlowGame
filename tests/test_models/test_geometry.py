from unittest import TestCase

from src.models.geometry import Point, point_linspace, make_circle


class TestGeometry(TestCase):
    def test_point(self) -> None:
        point = Point(x=3.0, y=4.0)
        self.assertEqual(point, Point(x=3.0, y=4.0))
        self.assertNotEqual(point, Point(x=3.0, y=5.0))
        self.assertAlmostEqual(point.length, 5.0)

    def test_point_combinations(self) -> None:
        point = Point(x=3.0, y=4.0)
        offset_point = Point(x=1.0, y=1.0)
        new_point = point + offset_point
        self.assertAlmostEqual(new_point.x, 4.0)
        self.assertAlmostEqual(new_point.y, 5.0)

        zero_point = point - point
        self.assertAlmostEqual(zero_point.x, 0.0)
        self.assertAlmostEqual(zero_point.y, 0.0)

    def test_point_scaling(self) -> None:
        point = Point(x=3.0, y=4.0)
        scaled_point = point * 2.0
        self.assertAlmostEqual(scaled_point.x, 6.0)
        self.assertAlmostEqual(scaled_point.y, 8.0)

        divided_point = point / 2.0
        self.assertAlmostEqual(divided_point.x, 1.5)
        self.assertAlmostEqual(divided_point.y, 2.0)

    def test_point_transpose(self) -> None:
        point = Point(x=3.0, y=4.0)
        transposed = point.transpose()
        self.assertEqual(transposed, Point(x=4.0, y=3.0))

    def test_linspace(self) -> None:
        point_a = Point(x=1.0, y=2.0)
        point_b = Point(x=1.0, y=6.0)
        points = point_linspace(start=point_a, end=point_b, num=3)

        self.assertEqual(len(points), 3)
        expected_x = [1, 1, 1]
        expected_y = [2, 4, 6]
        for x, y, point in zip(expected_x, expected_y, points):
            self.assertAlmostEqual(point.x, x)
            self.assertAlmostEqual(point.y, y)

    def test_circle(self) -> None:
        point_a = Point(x=1.0, y=2.0)
        circle_points = make_circle(center=point_a, radius=1.0, num_points=4)

        for p in circle_points:
            self.assertAlmostEqual((p - point_a).length, 1.0)

        expected_x = [2.0, 1.0, 0.0, 1.0]
        expected_y = [2.0, 3.0, 2.0, 1.0]
        for expected_x_val, expected_y_val, p in zip(expected_x, expected_y, circle_points):
            self.assertAlmostEqual(p.x, expected_x_val)
            self.assertAlmostEqual(p.y, expected_y_val)

    def test_str(self) -> None:
        point = Point(x=3.14159, y=2.71828)
        self.assertEqual(str(point), "<Point (3.1,2.7)>")
