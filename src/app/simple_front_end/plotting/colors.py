def get_contrasting_color(color: str) -> str:
    """
    Given a color in hex format, return a contrasting color (black or white).
    """
    if not color.startswith("#") or len(color) != 7:
        raise ValueError(f"Invalid color format: {color}. Expected hex format #RRGGBB.")

    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    # Calculate the brightness of the color
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    # Return black for light colors and white for dark colors
    return "#000000" if brightness > 128 else "#FFFFFF"
