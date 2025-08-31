from flask import Flask, render_template_string, request
from playwright.sync_api import sync_playwright
import datetime

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head><title>Headless IG Tracker</title></head>
<body>
  <h2>📊 Instagram Headless Tracker</h2>
  <form method="POST">
    <textarea name="links" rows="6" cols="60" placeholder="Paste IG links..."></textarea><br><br>
    <button type="submit">Track</button>
  </form>
  {% if results %}
    <h3>Results</h3>
    <table border="1" cellpadding="6">
      <tr><th>Link</th><th>Likes</th><th>Comments</th><th>Views</th><th>Checked At</th></tr>
      {% for r in results %}
      <tr>
        <td><a href="{{r.link}}" target="_blank">{{r.link}}</a></td>
        <td>{{r.likes}}</td>
        <td>{{r.comments}}</td>
        <td>{{r.views}}</td>
        <td>{{r.time}}</td>
      </tr>
      {% endfor %}
    </table>
  {% endif %}
</body>
</html>
"""

def scrape_stats(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)

            # Wait for article to load
            page.wait_for_selector("article", timeout=10000)

            # Extract stats
            likes = page.query_selector("section span") or None
            comments = page.query_selector("ul li span") or None
            views = page.query_selector("span:has-text('views')") or None

            result = {
                "link": url,
                "likes": likes.inner_text() if likes else "N/A",
                "comments": comments.inner_text() if comments else "N/A",
                "views": views.inner_text() if views else "N/A",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            browser.close()
            return result
    except Exception as e:
        return {"link": url, "likes": "Error", "comments": "Error", "views": "Error", "time": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        links = request.form.get("links").splitlines()
        for link in links:
            if link.strip():
                results.append(scrape_stats(link.strip()))
    return render_template_string(HTML, results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
