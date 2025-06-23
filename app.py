from flask import Flask, render_template, request, redirect, url_for
import os, re
from bs4 import BeautifulSoup

app = Flask(__name__)
HTML_DIR = "docs_html"  # Your folder with converted HTML docs

DOCUMENTS = {
    "uscc_420-1.html": {
        "title": "USCC Pamphlet 420-1",
        "description": "Guide to Standards of Cadet Living Areas and Barracks Arrangement"
    },
    "uscc_600-20.html": {
        "title": "USCC Pamphlet 600-20",
        "description": "Guide to United States Corps of Cadets Conduct Policy"
    },
    "uscc_670-1.html": {
        "title": "USCC Pamphlet 670-1",
        "description": "Guide to the Cadet Appearance and Wear of USMA Uniforms and Insignia"
    },
    "uscc_351-1.html": {
        "title": "USCC Reg 351-1",
        "description": "Cadet Disciplinary System"
    },
    "uscc_reg_600-20.html": {
        "title": "USCC Regulation 600-20",
        "description": "United States Corps of Cadets Command Policy for Conduct Appearance and Living Standards"
    }
}

# Helper: Highlight search terms in snippet
def highlight_terms(text, terms):
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

@app.route('/')
def index():
    return render_template('index.html', documents=DOCUMENTS)

@app.route('/search', methods=['GET', 'POST'])
def search():
    doc = request.args.get('doc') or request.form.get('doc')
    if not doc or doc not in DOCUMENTS:
        return redirect(url_for('index'))

    query = ""
    results = []

    if request.method == 'POST':
        query = request.form['query'].strip()
        terms = query.lower().split()

        filepath = os.path.join(HTML_DIR, doc)
        with open(filepath, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        page_divs = soup.find_all("div", id=re.compile(r"page-\d+"))

        # Find matches where all terms appear in a page
        for div in page_divs:
            page_num = div.get("id").split("-")[-1]
            text = div.get_text(" ", strip=True).lower()
            if all(term in text for term in terms):
                snippet = div.get_text(" ", strip=True)[:500]
                snippet = highlight_terms(snippet, terms)
                results.append({"page": page_num, "snippet": snippet})

        # Sort results by page number ascending (optional)
        results.sort(key=lambda x: int(x["page"]))

    return render_template('search.html', doc=doc, document=DOCUMENTS[doc], results=results, query=query)

@app.route('/view/<filename>')
def view_file(filename):
    page = request.args.get("page")
    anchor = f"#page-{page}" if page else ""
    html_path = os.path.join(HTML_DIR, filename)
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    return render_template('view.html', content=content, anchor=anchor)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
    app.run(host="0.0.0.0", port=port)

