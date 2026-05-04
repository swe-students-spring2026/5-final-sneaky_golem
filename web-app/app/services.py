from bson import ObjectId


def get_board(db, board_id):
    return db.boards.find_one({"_id": ObjectId(board_id)})


def get_solutions(db, board_id):
    cursor = db.solutions.find({"board_id": board_id})
    results = []
    for doc in cursor:
        results.append({
            "solution_id": str(doc["_id"]),
            "solution_name": doc.get("solution_name"),
            "author_username": doc.get("author_username"),
            "like_count": doc.get("like_count", 0),
            "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
            "final_board": doc.get("final_board"),
        })
    return results


def get_solution(db, solution_id):
    doc = db.solutions.find_one({"_id": ObjectId(solution_id)})
    if doc is None:
        return None
    return {
        "solution_id": str(doc["_id"]),
        "solution_name": doc.get("solution_name"),
        "author_username": doc.get("author_username"),
        "like_count": doc.get("like_count", 0),
        "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
        "final_board": doc.get("final_board"),
        "steps": doc.get("steps", []),
    }
