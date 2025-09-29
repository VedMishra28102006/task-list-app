from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")

@app.route("/getTasks", methods=["GET"])
def getTasks():
	db = sqlite3.connect("data.db")
	db.row_factory = sqlite3.Row
	cursor = db.cursor()
	cursor.execute("SELECT * FROM tasks")
	rows = cursor.fetchall()
	db.close()
	tasks = [dict(row) for row in rows]
	return jsonify(tasks), 200

@app.route("/postTask", methods=["POST"])
def postTask():
	task = request.json.get("task")
	if not task:
		return jsonify({
			"error": "The field task is empty",
			"field": "taskInput",
			"label": "errorTaskInput"
		}), 400
	db = sqlite3.connect("data.db")
	cursor = db.cursor()
	cursor.execute("INSERT INTO tasks (task) VALUES(?)", (task,))
	db.commit()
	id = cursor.lastrowid
	db.close()
	return jsonify({
		"success": 1,
		"id": id,
		"task": task
	}), 200

@app.route("/deleteTask/<id>", methods=["DELETE"])
def deleteTask(id):
	db = sqlite3.connect("data.db")
	cursor = db.cursor()
	cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
	db.commit()
	db.close()
	if cursor.rowcount:
		return jsonify({
			"success": 1
		}), 200
	else:
		return jsonify({
			"error": "Task not found",
			"field": id
		}), 404

@app.route("/patchTask/<id>", methods=["PATCH"])
def patchTask(id):
	task = request.json.get("task")
	if not task:
		return jsonify({
			"error": "The field task is empty",
			"field": f"editInput{id}",
			"label": f"errorEditInput{id}"
		}), 400
	db = sqlite3.connect("data.db")
	cursor = db.cursor()
	cursor.execute("UPDATE tasks SET task=? WHERE id=?", (task, id))
	db.commit()
	db.close()
	if cursor.rowcount:
		return jsonify({
			"success": 1,
			"id": id,
			"task": task
		}), 200
	else:
		return jsonify({
			"error": "Task not found",
			"field": id
		}), 404

if __name__ == "__main__":
	db = sqlite3.connect("data.db")
	db.execute("""CREATE TABLE IF NOT EXISTS tasks (
		id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
		task TEXT NOT NULL
	)""")
	db.commit()
	db.close()
	app.run()