# pylint: disable=no-member

"""
Tests for board_reader.py.
"""

import numpy as np
import cv2
from app.board_reader import (
    crop_board,
    get_color_matrix,
    get_board_matrix,
    visualize_board,
    visualize_matrix_avg_color,
    extract_board,
)
from app.board_reader import EMPTY_LIGHTNESS_THRESHOLD, MINO_PALETTE


def test_crop_board_returns_none_when_no_lines():
    """
    Make sure crop_board() returns None if no detectable edges/lines exist.
    """
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    assert crop_board(img) is None


def test_get_color_matrix_none_input():
    """
    Make sure get_color_matrix() handles None input properly.
    """
    assert get_color_matrix(None) is None


def test_get_board_matrix_none_input():
    """
    Make sure get_board_matrix() handles None input properly.
    """
    assert get_board_matrix(None) is None


def test_get_color_matrix_handles_small_image():
    """
    Make sure small images still produce a correctly sized 20x10 matrix.
    """
    img = np.zeros((10, 10, 3), dtype=np.uint8)

    matrix = get_color_matrix(img)

    assert len(matrix) == 20
    assert len(matrix[0]) == 10


def test_get_board_matrix_empty_threshold():
    """
    Make sure colors below the lightness threshold are classified as empty ('X').
    """
    dark = [EMPTY_LIGHTNESS_THRESHOLD - 1] * 3
    matrix = [[dark for _ in range(10)] for _ in range(20)]

    board = get_board_matrix(matrix)

    assert all(cell == "X" for row in board for cell in row)


def test_get_board_matrix_palette_matching():
    """
    Make sure colors close to a palette value map to the correct mino.
    """
    matrix = [[MINO_PALETTE["T"].tolist() for _ in range(10)] for _ in range(20)]

    board = get_board_matrix(matrix)

    assert all(cell == "T" for row in board for cell in row)


def test_visualize_board_none():
    """
    Make sure visualize_board returns None when given None input.
    """
    assert visualize_board(None) is None


def test_visualize_matrix_none():
    """
    Make sure visualize_matrix_avg_color returns None when given None input.
    """
    assert visualize_matrix_avg_color(None) is None


def test_extract_board_failure():
    """
    Make sure extract_board returns None when no board can be detected.
    """
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    assert extract_board(img) is None


def test_extract_board_success():
    """
    Make sure extract_board successfully processes a valid test image.
    """
    img = cv2.imread("images/test1.png")

    board = extract_board(img)

    assert board is not None
    assert len(board) == 20
    assert len(board[0]) == 10
