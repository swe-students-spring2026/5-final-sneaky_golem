from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests

main = Blueprint("main", __name__)


@main.route("/tetris", methods=["GET"])
async def tetris_board():
    """
    Retrieves playable tetris board.
    """
    return render_template("zztetris/index.html")