"""
Converts a screenshot of a Tetris board into a 10x20 matrix of mino colors.
"""

from typing import Optional
import cv2
import numpy as np

MINO_PALETTE: dict[str, np.ndarray] = {
    "I": np.array([134, 176, 90]),
    "O": np.array([69, 154, 176]),
    "T": np.array([150, 69, 152]),
    "S": np.array([72, 178, 140]),
    "Z": np.array([61, 61, 164]),
    "J": np.array([157, 63, 75]),
    "L": np.array([60, 103, 169]),
    "X": np.array([0, 0, 0]),
    "G": np.array([66, 66, 66]),
}

BOARD_COLS = 10
BOARD_ROWS = 20

EMPTY_LIGHTNESS_THRESHOLD = 30

def crop_board(image: np.ndarray) -> Optional[np.ndarray]:
    """
    Crop the Tetris board from a screenshot.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=200, threshold2=600)

    # cv2.imshow("edges", edges)
    # cv2.waitKey(0)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=100,
        maxLineGap=20
    )

    if lines is None:
        return None

    vertical_lines = []
    horizontal_lines = []

    # print(lines)

    for line in lines:
        x1, y1, x2, y2 = line[0]

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx < 10 and dy > 50:
            vertical_lines.append((x1, y1, x2, y2))
        elif dy < 10 and dx > 50:
            horizontal_lines.append((x1, y1, x2, y2))

    if len(vertical_lines) < 2 or len(horizontal_lines) < 1:
        return None

    # print(vertical_lines)
    # print(horizontal_lines)

    clusters = cluster_by_bottom(vertical_lines)

    if not clusters:
        return None

    best_cluster = max(clusters, key=cluster_score)

    lines = best_cluster["lines"]
    xs = [x_mid(l) for l in lines]

    leftmost = min(xs)
    rightmost = max(xs)

    center_x = (leftmost + rightmost) / 2

    lines_sorted = sorted(lines, key=lambda l: abs(x_mid(l) - center_x))

    left_line = None
    right_line = None

    for line in lines_sorted:
        xm = x_mid(line)

        if xm < center_x and left_line is None:
            left_line = line
        elif xm > center_x and right_line is None:
            right_line = line

        if left_line is not None and right_line is not None:
            break

    if left_line is None or right_line is None:
        return None

    # print(left_line)
    # print(right_line)

    x_left = x_mid(left_line)
    x_right = x_mid(right_line)
    y_bottom = (max(left_line[1], left_line[3]) + max(right_line[1], right_line[3])) / 2
    y_top = max(0, y_bottom - abs(x_right - x_left) * 2)

    # print("left", x_left, "right", x_right, "top", y_top, "bottom", y_bottom)

    h, w = image.shape[:2]

    x1 = int(max(0, min(w, x_left)))
    x2 = int(max(0, min(w, x_right)))
    y1 = int(max(0, min(h, y_top)))
    y2 = int(max(0, min(h, y_bottom)))

    if x2 <= x1 or y2 <= y1:
        return None

    cropped = image[y1:y2, x1:x2]

    return cropped

def cluster_by_bottom(vertical_lines, threshold=10):
    """
    Find clusters of vertical lines by their bottom-most y-value.
    Used in detect_board_edges().
    """

    clusters = []

    for line in vertical_lines:
        bottom = max(line[1], line[3])

        placed = False
        for cluster in clusters:
            if abs(bottom - cluster["bottom_mean"]) < threshold:
                cluster["lines"].append(line)

                bottoms = [max(l[1], l[3]) for l in cluster["lines"]]
                cluster["bottom_mean"] = sum(bottoms) / len(bottoms)

                placed = True
                break

        if not placed:
            clusters.append({
                "lines": [line],
                "bottom_mean": bottom
            })

    return clusters

def x_mid(line):
    """
    Find the mean x-value for a line.
    """

    return (line[0] + line[2]) / 2

def cluster_score(cluster):
    """
    Score the cluster based on how wide the widest pair of lines is.
    """

    xs = [x_mid(l) for l in cluster["lines"]]
    return max(xs) - min(xs)

def get_color_matrix(image: Optional[np.ndarray]) -> Optional[list[list[float]]]:
    """
    Get a 10x20 matrix of average colors from the cropped board image.
    """

    if image is None:
        return None

    rows, cols = BOARD_ROWS, BOARD_COLS
    h, w, _ = image.shape

    cell_w = w // cols

    matrix = []

    for r in range(rows):
        y2 = h - r * cell_w
        y1 = h - (r + 1) * cell_w

        if y1 < 0:
            break

        row_colors = []

        for c in range(cols):
            x1 = c * cell_w
            x2 = (c + 1) * cell_w

            margin = int(min(cell_w, cell_w) * 0.2)
            cell = image[y1+margin:y2-margin, x1+margin:x2-margin]

            if cell.size == 0:
                mean_color = [0, 0, 0]
            else:
                mean_color = cell.mean(axis=(0, 1)).tolist()

            row_colors.append(mean_color)

        matrix.append(row_colors)

    while len(matrix) < rows:
        matrix.append([[0, 0, 0] for _ in range(cols)])

    matrix.reverse()

    return matrix

def get_board_matrix(matrix: Optional[list[list[float]]]) -> Optional[list[list[str]]]:
    """
    Get a 10x20 matrix of Tetris minos from the color matrix.
    """

    if matrix is None:
        return None

    board = []

    for row in matrix:
        board_row = []

        for color in row:
            color_np = np.array(color)

            if np.mean(color_np) < EMPTY_LIGHTNESS_THRESHOLD:
                board_row.append("X")
                continue

            best_mino = None
            best_dist = float("inf")

            for mino, palette_color in MINO_PALETTE.items():
                dist = np.linalg.norm(color_np - palette_color)

                if dist < best_dist:
                    best_dist = dist
                    best_mino = mino

            board_row.append(best_mino)

        board.append(board_row)

    return board

def visualize_matrix_avg_color(matrix: Optional[list[list[list[float]]]], cell_size: int = 20) -> Optional[np.ndarray]:
    """
    Convert a 20x10 averaged color matrix back into an image for visualization
    Mainly for debugging purposes.
    """

    if matrix is None:
        return None

    rows = len(matrix)
    cols = len(matrix[0])

    img = np.zeros((rows * cell_size, cols * cell_size, 3), dtype=np.uint8)

    for r in range(rows):
        for c in range(cols):
            color = np.array(matrix[r][c], dtype=np.uint8)

            y1 = r * cell_size
            y2 = (r + 1) * cell_size
            x1 = c * cell_size
            x2 = (c + 1) * cell_size

            img[y1:y2, x1:x2] = color

    return img

def visualize_board(matrix: Optional[list[list[list[int]]]], cell_size: int = 20) -> Optional[np.ndarray]:
    """
    Convert the board matrix to an image with the colors, for easy visualization.
    """

    if matrix is None:
        return None

    rows = len(matrix)
    cols = len(matrix[0])

    img = np.zeros((rows * cell_size, cols * cell_size, 3), dtype=np.uint8)

    for r in range(rows):
        for c in range(cols):
            mino = matrix[r][c]

            color = MINO_PALETTE.get(mino, MINO_PALETTE["X"]).astype(np.uint8)

            y1 = r * cell_size
            y2 = (r + 1) * cell_size
            x1 = c * cell_size
            x2 = (c + 1) * cell_size

            img[y1:y2, x1:x2] = color

    return img

def extract_board(image: np.ndarray) -> Optional[list[list[str]]]:
    """
    The whole board extraction pipeline.
    """
    cropped = crop_board(image)
    if cropped is None:
        return None

    color_matrix = get_color_matrix(cropped)
    return get_board_matrix(color_matrix)

def main():
    """testing the functions"""
    # image = cv2.imread("images/test4.png")

    # cropped = crop_board(image)

    # cv2.imshow("original", image)
    # cv2.waitKey(0)

    # cv2.imshow("cropped", cropped)
    # cv2.waitKey(0)

    # color_matrix = get_color_matrix(cropped)

    # averaged_colors = visualize_matrix_avg_color(color_matrix)
    # cv2.imshow("averaged colors", averaged_colors)
    # cv2.waitKey(0)

    # board_matrix = get_board_matrix(color_matrix)
    # board_matrix = extract_board(image)

    # print(board_matrix)

    # reconstructed_board = visualize_board(board_matrix)

    # if reconstructed_board is None:
        # print("board extraction failed")
    # else:
        # cv2.imshow("reconstructed board", reconstructed_board)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

# main()
