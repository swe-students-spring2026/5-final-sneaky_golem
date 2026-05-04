import json
from flask import current_app, render_template, request
from . import services


def register_routes(app):

    @app.route("/board/<board_id>")
    def saved_board(board_id):
        db = current_app.db

        puzzle = services.get_board(db, board_id)
        if puzzle is None:
            return "Board not found", 404

        solutions = services.get_solutions(db, str(puzzle["_id"]))

        solution_id = request.args.get("solution")
        if solution_id:
            active_solution = services.get_solution(db, solution_id)
        elif solutions:
            active_solution = services.get_solution(db, solutions[0]["solution_id"])
        else:
            active_solution = None

        return render_template(
            "saved_board.html",
            puzzle=puzzle,
            board_json=json.dumps(puzzle.get("matrix")),
            solutions_json=json.dumps(solutions),
            active_solution_json=json.dumps(active_solution),
        )
