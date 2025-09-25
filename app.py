from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Read the CSV file
    df = pd.read_csv('nsw-grants.csv', encoding='utf-8', low_memory=False)
    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='table table-striped', index=False, border=0, escape=False)
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NSW Grants Table</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <style>
            body {{ margin: 2em; }}
            table {{ font-size: 0.95em; }}
            th, td {{ max-width: 350px; word-break: break-word; }}
        </style>
    </head>
    <body>
        <h1>NSW Grants</h1>
        <div class="table-responsive">{table_html}</div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)