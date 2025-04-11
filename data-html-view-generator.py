import csv
import requests
import html

# File paths
csv_file_path = "zenodo_registry.csv"  # Path to your CSV file
output_html_path = "zenodo_archive.html"  # Desired output HTML file

# HTML template parts
html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>The Sarvāmnāya Oral Tradition Archive</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="icon" href="https://www.vimarshafoundation.org/favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #f4f5f7;
            color: #333;
            padding: 40px 20px;
            font-size: 1em;
        }
        h1 {
            font-size: 2em;
            font-weight: bold;
            color: #004b87;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.1em;
            margin-bottom: 40px;
            color: #004b87;
        }
        .logo {
            display: block;
            margin: 0 auto 30px auto;
            width: 200px;
        }
        .table-container {
            margin-bottom: 30px;
        }
        .table {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .table th, .table td {
            text-align: center;
            vertical-align: middle;
            padding: 12px;
        }
        .table th {
            background-color: #004b87;
            color: white;
        }
        .table a {
            color: #004b87;
        }
        .modal-content {
            border-radius: 8px;
        }
        .modal-header {
            background-color: #004b87;
            color: white;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        .modal-body {
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
            background-color: #f7f7f7;
        }
        .modal-body code {
            display: block;
            background-color: #f1f1f1;
            border: 1px solid #e1e1e1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .btn-primary {
            background-color: #004b87;
            border-color: #004b87;
            border-radius: 5px;
            padding: 8px 20px;
        }
        .btn-primary:hover {
            background-color: #003b6a;
            border-color: #003b6a;
        }
        .footer {
            background-color: #004b87;
            color: white;
            padding: 20px 0;
            text-align: center;
            font-size: 0.85em;
            margin-top: 40px;
        }
        .footer a {
            color: white;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <img class="logo" src="https://static.wixstatic.com/media/6877d8_58c2bf304142418baeaf28fdc42f9dc6~mv2.png/v1/fill/w_357,h_418,al_c,lg_1,q_85,enc_avif,quality_auto/Logo%20transparent.png" alt="Vimarsha Foundation Logo">
    <h1>The Sarvāmnāya Oral Tradition Archive</h1>
    <p class="subtitle">A project of <a href="https://www.vimarshafoundation.org/">Vimarsha Foundation</a></p>

    <div class="table-container">
        <table class="table table-bordered table-hover" id="archiveTable">
            <thead>
                <tr>
                    <th><i class="fas fa-id-badge"></i> ID</th>
                    <th><i class="fas fa-book"></i> Title</th>
                    <th><i class="fab fa-youtube"></i> YouTube</th>
                    <th><i class="fas fa-archive"></i> Zenodo</th>
                    <th><i class="fas fa-cogs"></i> DOI</th>
                    <th><i class="fas fa-quote-right"></i> Citation</th>
                </tr>
            </thead>
            <tbody>
"""

html_footer = """
            </tbody>
        </table>
    </div>

    <!-- Modals -->
    <div id="modalsContainer"></div>

    <div class="footer">
        <p>&copy; 2025 Vimarsha Foundation | <a href="https://www.vimarshafoundation.org/">www.vimarshafoundation.org</a></p>
        <p>All rights reserved. The Sarvāmnāya Oral Tradition Archive is an ongoing project dedicated to preserving the spiritual and cultural heritage of the Sarvāmnāya lineage.</p>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

rows_html = ""
modals_html = ""
bibtex_library = ""

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        zenodo_id = row['zenodo_id']
        doi = row['doi']
        title = row['title']
        youtube_link = row['youtube_link']
        zenodo_link = row['zenodo_link']
        doi_link = f"https://doi.org/{doi}"

        # Get BibTeX citation from Zenodo
        bibtex_citation = "Unavailable"
        try:
            bibtex_url = f"https://zenodo.org/record/{zenodo_id}/export/bibtex"
            bibtex_citation = requests.get(bibtex_url).text.strip()
        except Exception as e:
            bibtex_citation = f"Error fetching citation: {e}"

        row_id = row["id"]
        modal_id = f"citationModal{row_id}"

        # Escape HTML characters to prevent issues
        title_escaped = html.escape(title)
        bibtex_citation_escaped = html.escape(bibtex_citation)

        rows_html += f"""
        <tr>
            <td>{row_id}</td>
            <td>{title_escaped}</td>
            <td><a href="{youtube_link}" target="_blank"><i class="fab fa-youtube"></i> Watch</a></td>
            <td><a href="{zenodo_link}" target="_blank"><i class="fas fa-archive"></i> Zenodo</a></td>
            <td><a href="{doi_link}" target="_blank">{doi}</a></td>
            <td><a href="#" class="citation-btn" data-toggle="modal" data-target="#{modal_id}">View Citation</a></td>
        </tr>
        """

        modals_html += f"""
        <div class="modal fade" id="{modal_id}" tabindex="-1" role="dialog" aria-labelledby="{modal_id}Label" aria-hidden="true">
          <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="{modal_id}Label">Citations for: {title_escaped}</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                <pre><code>{bibtex_citation_escaped}</code></pre>
              </div>
            </div>
          </div>
        </div>
        """

        # Add BibTeX citation to the full library
        bibtex_library += bibtex_citation + "\n\n"

# Final HTML with BibTeX modal content
full_html = html_head + rows_html + "</tbody></table></div>" + modals_html + html_footer

with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

output_html_path
