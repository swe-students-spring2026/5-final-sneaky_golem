"""
Converts a screenshot of a Tetris board into a 10x20 matrix of mino colors.
"""

from typing import Optional
import cv2
import numpy as np

MINO_PALETTE: dict[str, np.ndarray] = {
    "I": np.array([0, 240, 240]),
    "O": np.array([241, 239, 47]),
    "T": np.array([136, 44, 237]),
    "S": np.array([138, 234, 40]),
    "Z": np.array([207, 54, 22]),
    "J": np.array([0, 0, 240]),
    "L": np.array([221, 164, 34]),
    "X": np.array([0, 0, 0]),
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
    edges = cv2.Canny(blurred, threshold1=250, threshold2=750)

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

def cluster_by_bottom(vertical_lines, threshold=50):
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

def get_color_matrix(image: np.ndarray) -> list[list[float]]:
    """
    Get a 10x20 matrix of average colors from the cropped board image.
    Not yet implemented.
    """

def get_board_matrix(matrix: list[list[float]]) -> list[list[str]]:
    """
    Get a 10x20 matrix of Tetris minos from the color matrix.
    Not yet implemented.
    """

def visualize_matrix(matrix: list[list[str]]) -> str:
    """
    Return a simple ASCII representation of the board matrix, mainly for debugging purposes.
    Not yet implemented.
    """

def main():
    """testing the functions"""
    image = cv2.imread("images/test1.png")
    cropped = crop_board(image)

    cv2.imshow("cropped", cropped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
main()
