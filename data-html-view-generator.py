import csv

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>The Sarvāmnāya Oral Tradition Archive</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Bootstrap and jQuery -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/datatables.net-dt/css/jquery.dataTables.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">

  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f9f5ef;
        padding: 20px;
    }
    header {
        background-color: #3e2723;
        color: white;
        padding: 20px;
        text-align: center;
    }
    header h1 {
        font-size: 2.5em;
        margin: 0;
    }
    header p {
        font-size: 1.1em;
    }
    .logo {
        width: 200px;
        height: auto;
        margin-bottom: 10px;
    }
    th {
        background-color: #5d4037;
        color: white;
    }
    td, th {
        text-align: center;
        padding: 10px;
    }
    .citation-btn {
        cursor: pointer;
        color: #007bff;
    }
    .modal-body code {
        white-space: pre-wrap;
        display: block;
        background: #f1f1f1;
        padding: 10px;
        border-radius: 5px;
    }
    a {
        text-decoration: none;
    }
  </style>
</head>
<body>

<header>
  <img src="https://www.vimarshafoundation.org/logo.png" alt="Vimarsha Foundation Logo" class="logo">
  <h1>The Sarvāmnāya Oral Tradition Archive</h1>
  <p>A project of <a href="https://www.vimarshafoundation.org/" target="_blank" style="color: #ffcc80;">Vimarsha Foundation</a></p>
</header>

<div class="container mt-4">
  <table id="archiveTable" class="display table table-striped">
    <thead>
      <tr>
        <th>Id</th>
        <th>YouTube ID</th>
        <th>Zenodo ID</th>
        <th>Title</th>
        <th>DOI</th>
        <th>Zenodo</th>
        <th>YouTube</th>
        <th>Citation</th>
      </tr>
    </thead>
    <tbody>
      <!--TABLE_ROWS-->
    </tbody>
  </table>
</div>

<!-- Modal -->
<div class="modal fade" id="citationModal" tabindex="-1" aria-labelledby="citationModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Citation</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span>&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <h6>APA:</h6>
        <code id="apaCitation">Loading...</code>
        <h6 class="mt-3">BibTeX:</h6>
        <code id="bibtexCitation">Loading...</code>
      </div>
    </div>
  </div>
</div>

<!-- Scripts in correct order -->
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/datatables.net/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js"></script>

<script>
$(document).ready(function() {
    $('#archiveTable').DataTable({
        paging: false,
        ordering: true,
        info: false
    });

    $('.citation-btn').on('click', function() {
        var doi = $(this).data('doi');
        $('#citationModal').modal('show');
        $('#apaCitation').text("Loading...");
        $('#bibtexCitation').text("Loading...");

        let recordId = doi.split('.').pop();

        fetch(`https://zenodo.org/api/records/${recordId}`)
        .then(res => res.json())
        .then(data => {
            const apa = data.metadata.citation ? data.metadata.citation.apa : "Not available";
            fetch(`https://zenodo.org/record/${recordId}/export/hx`)
              .then(res => res.text())
              .then(bib => {
                $('#apaCitation').text(apa);
                $('#bibtexCitation').text(bib);
              });
        }).catch(err => {
            $('#apaCitation').text("Could not fetch citation.");
            $('#bibtexCitation').text("Could not fetch citation.");
        });
    });
});
</script>

</body>
</html>
"""

# Load CSV
rows_html = ""
with open("zenodo_registry.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        doi = row["doi"]
        zenodo_link = row["zenodo_link"]
        youtube_link = row["youtube_link"]
        youtube_id = row["youtube_id"]
        zenodo_id = row["zenodo_id"]
        title = row["title"]
        id_ = row["id"]

        rows_html += f"""
        <tr>
          <td>{id_}</td>
          <td>{youtube_id}</td>
          <td>{zenodo_id}</td>
          <td>{title}</td>
          <td><a href="https://doi.org/{doi}" target="_blank">{doi}</a></td>
          <td><a href="{zenodo_link}" target="_blank"><i class="fas fa-cloud-download-alt"></i></a></td>
          <td><a href="{youtube_link}" target="_blank"><i class="fas fa-play-circle"></i></a></td>
          <td><i class="fas fa-book citation-btn" data-doi="{doi}"></i></td>
        </tr>
        """

# Replace placeholder
final_html = html_template.replace("<!--TABLE_ROWS-->", rows_html)

# Write output
with open("zenodo_archive.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ HTML generated: zenodo_archive.html")
