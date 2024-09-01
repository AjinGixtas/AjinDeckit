from curses import A_DIM
def draw_bw_image(layer, image_path, x_origin, y_origin, x_img_origin=0, y_img_origin=0, x_size=-1, y_size=-1):
    with open(image_path, 'r', encoding='utf-8') as f:
        try: height, width = map(int, f.readline().split())
        except ValueError: raise ValueError("Invalid format for height and width in the image file.")

        # Adjust height and width if x_size or y_size are specified
        height, width = height if y_size <= 0 else min(height, y_size), width if x_size <= 0 else min(width, x_size)

        # Skip lines until reaching the image origin
        for _ in range(y_img_origin): next(f, None)  # Use next with a default value to avoid StopIteration

        # Read and draw the image line by line
        for y in range(y_origin, y_origin + height): layer.addstr(y, x_origin, f.readline().rstrip()[x_img_origin:x_img_origin + width])

def draw_colored_image(layer, image_path, x_origin, y_origin, x_img_origin=0, y_img_origin=0, x_size=-1, y_size=-1, color_pair_obj=None):
    with open(image_path, 'r', encoding='utf-8') as f:
        try: height, width = map(int, f.readline().split())
        except ValueError: raise ValueError("Invalid format for height and width in the image file.")

        # Adjust height and width if x_size or y_size are specified
        height, width = height if y_size <= 0 else min(height, y_size), width if x_size <= 0 else min(width, x_size)

        # Skip lines until reaching the image origin
        for _ in range(y_img_origin): next(f, None)  # Use next with a default value to avoid StopIteration

        # Read and draw the image line by line
        if color_pair_obj == None:
            for y in range(y_origin, y_origin + height): layer.addstr(y, x_origin, f.readline().rstrip()[x_img_origin:x_img_origin + width])
        else: 
            for y in range(y_origin, y_origin + height): layer.addstr(y, x_origin, f.readline().rstrip()[x_img_origin:x_img_origin + width], color_pair_obj)