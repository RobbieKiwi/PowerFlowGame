from unittest import TestCase

from src.models.colors import Color


class TestColors(TestCase):
    def test_making_colours(self) -> None:
        red = Color("red")
        self.assertEqual(red.rgb_hex_str, "#FF0000")
        self.assertEqual(red.rgb, (255, 0, 0))
        self.assertEqual(red.hsv, (0, 255, 255))

        other_reds = [
            Color((255, 0, 0)),
            Color(x=(0, 255, 255), color_model="hsv"),
            Color(x="#00FFFF", color_model="hsv"),
        ]
        for r in other_reds:
            self.assertEqual(red, r)

        black = Color("black")
        self.assertEqual(black.rgb_hex_str, "#000000")
        self.assertEqual(black.rgb, (0, 0, 0))
        self.assertEqual(black.hsv, (0, 0, 0))

        white = Color("white")
        self.assertEqual(white.rgb_hex_str, "#FFFFFF")
        self.assertEqual(white.rgb, (255, 255, 255))
        self.assertEqual(white.hsv, (0, 0, 255))

    def test_brightness_factor(self) -> None:
        black = Color("black")
        gray = Color("gray")
        white = Color("white")
        red = Color("red")
        green = Color("green")
        blue = Color("blue")

        self.assertEqual(black.brightness_factor, 0.0)
        self.assertAlmostEqual(gray.brightness_factor, 0.5, places=2)
        self.assertEqual(white.brightness_factor, 1.0)

        for color in [red, green, blue]:
            self.assertAlmostEqual(color.brightness_factor, 0.5, places=2)

    def test_color_distance(self) -> None:
        red = Color("red")
        blue = Color("blue")
        green = Color("green")
        black = Color("black")
        white = Color("white")

        self.assertEqual(black.calculate_distance_factor(other=black), 0.0)
        self.assertEqual(black.calculate_distance_factor(other=white), 1.0)

        mid_distance = black.calculate_distance_factor(other=red)
        self.assertTrue(0.4 < mid_distance < 0.6, f"Expected mid distance to be around 0.5, got {mid_distance}")
        self.assertEqual(black.calculate_distance_factor(other=green), mid_distance)
        self.assertEqual(black.calculate_distance_factor(other=blue), mid_distance)

        other_distance = white.calculate_distance_factor(other=red)
        self.assertTrue(0.7 < other_distance < 0.9, f"Expected other distance to be around 0.8, got {other_distance}")
        self.assertEqual(white.calculate_distance_factor(other=green), other_distance)
        self.assertEqual(white.calculate_distance_factor(other=blue), other_distance)

        self.assertEqual(red.calculate_distance_factor(other=green), other_distance)
        self.assertEqual(red.calculate_distance_factor(other=blue), other_distance)
        self.assertEqual(green.calculate_distance_factor(other=blue), other_distance)
