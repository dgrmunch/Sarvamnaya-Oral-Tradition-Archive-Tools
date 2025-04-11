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
    <style>
        body {
            font-family: 'Georgia', serif;
            background-color: #fdf6e3;
            color: #3e3e3e;
            padding: 30px;
            font-size: 0.8em;
        }
        h1 {
            font-size: 2em;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        .logo {
            display: block;
            margin: 0 auto 20px auto;
            max-width: 200px;
        }
        .table-responsive {
            margin-top: 30px;
        }
        .table th, .table td {
            text-align: center;
        }
        .table th {
            background-color: #343a40;
            color: white;
        }
        .table td {
            vertical-align: middle;
        }
        .modal-body pre {
            font-family: monospace;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }
        .modal-header {
            background-color: #007bff;
            color: white;
        }
        .modal-footer {
            border-top: none;
        }
        .copy-btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }
        .copy-btn:hover {
            background-color: #0056b3;
        }
    </style>
    <link href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css" rel="stylesheet">
</head>
<body>
    <img class="logo" src="https://static.wixstatic.com/media/6877d8_58c2bf304142418baeaf28fdc42f9dc6~mv2.png/v1/fill/w_357,h_418,al_c,lg_1,q_85,enc_avif,quality_auto/Logo%20transparent.png" alt="Vimarsha Foundation Logo">
    <h1>The Sarvāmnāya Oral Tradition Archive</h1>
    <p class="subtitle">A project of <a href="https://www.vimarshafoundation.org/">Vimarsha Foundation</a></p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover" id="archiveTable">
            <thead class="thead-dark">
                <tr>
                    <th>Title</th>
                    <th>DOI</th>
                    <th>Cite</th>
                    <th>Zenodo Id</th>
                    <th>YouTube Id</th> 
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

<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
<script>
    $(document).ready(function() {
        $('#archiveTable').DataTable({
            "paging": true,
            "searching": true,
            "ordering": true
        });
    });
</script>
</body>
</html>
"""

rows_html = ""
modals_html = ""

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        zenodo_id = row['zenodo_id']
        doi = row['doi']
        title = row['title']
        youtube_link = row['youtube_link']
        zenodo_link = row['zenodo_link']
        doi_link = f"https://doi.org/{doi}"

        # Get BibTeX citations from Zenodo
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
            <td>{title_escaped}</td>
            <td><a href="{doi_link}" target="_blank">{doi}</a></td>
            <td><a href="#" class="citation-btn" data-toggle="modal" data-target="#{modal_id}">Cite</a></td>
            <td><a href="{zenodo_link}" target="_blank">{row["zenodo_id"]}</a></td>
            <td><a href="{youtube_link}" target="_blank">{row["youtube_id"]}</a></td>      
        </tr>
        """

        modals_html += f"""
        <div class="modal fade" id="{modal_id}" tabindex="-1" role="dialog" aria-labelledby="{modal_id}Label" aria-hidden="true">
          <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="{modal_id}Label">{title_escaped}</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                <strong>BibTeX:</strong><br>
                <pre>{bibtex_citation_escaped}</pre>
              </div>
            </div>
          </div>
        </div>
        """

# Combine all parts and write to file
full_html = html_head + rows_html + "</tbody></table></div>" + modals_html + html_footer

with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"HTML file saved to {output_html_path}")
