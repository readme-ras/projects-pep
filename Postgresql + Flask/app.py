import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key")

API_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000")


def api(method, path, **kwargs):
    """Helper to call the FastAPI backend."""
    url = f"{API_BASE}{path}"
    resp = requests.request(method, url, timeout=10, **kwargs)
    resp.raise_for_status()
    return resp.json() if resp.content else {}


@app.route("/")
def index():
    try:
        items = api("GET", "/items")
    except Exception as e:
        flash(f"Could not reach API: {e}", "error")
        items = []
    return render_template("index.html", items=items)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        try:
            api("POST", "/items", json={
                "name":        request.form["name"],
                "description": request.form.get("description", ""),
            })
            flash("Item created!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template("form.html", item=None, action=url_for("create"))


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    if request.method == "POST":
        try:
            api("PUT", f"/items/{item_id}", json={
                "name":        request.form["name"],
                "description": request.form.get("description", ""),
            })
            flash("Item updated!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error: {e}", "error")
    try:
        item = api("GET", f"/items/{item_id}")
    except Exception as e:
        flash(f"Item not found: {e}", "error")
        return redirect(url_for("index"))
    return render_template("form.html", item=item, action=url_for("edit", item_id=item_id))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    try:
        api("DELETE", f"/items/{item_id}")
        flash("Item deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
