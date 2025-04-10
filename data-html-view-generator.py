import pandas as pd
from jinja2 import Template

# Read CSV file
csv_file = 'zenodo_registry.csv'  # Adjust this to your actual CSV file path
df = pd.read_csv(csv_file)

# Drop the 'audio_extracted' column as requested
df = df.drop(columns=['audio_extracted'])

# Convert DataFrame to JSON format
data_json = df.to_dict(orient='records')

# HTML template with embedded DataTable (no pagination, show all rows)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Data Table</title>

    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>

    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
        }

        table {
            width: 100%;
            margin-top: 20px;
        }

        th {
            text-align: left;
            padding: 8px;
            background-color: #f2f2f2;
        }

        td {
            padding: 8px;
        }

        #example_filter {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>

    <h2>CSV Data Table</h2>

    <table id="example" class="display">
        <thead>
            <tr>
                <th>id</th>
                <th>youtube_id</th>
                <th>zenodo_id</th>
                <th>title</th>
                <th>doi</th>
                <th>zenodo_link</th>
                <th>youtube_link</th>
            </tr>
        </thead>
        <tbody>
            <!-- Data will be dynamically filled by JavaScript -->
        </tbody>
    </table>

    <script>
        // Data from the Python script
        var tableData = {{ table_data|tojson }};
        
        // Initialize DataTables to show all rows without pagination
        $(document).ready(function() {
            $('#example').DataTable({
                "paging": false, // Disable pagination
                "lengthMenu": [[-1], ["All"]], // Show all rows
                "data": tableData, // Provide the data dynamically
                "columns": [
                    { "data": "id" },
                    { "data": "youtube_id" },
                    { "data": "zenodo_id" },
                    { "data": "title" },
                    { "data": "doi" },
                    { "data": "zenodo_link" },
                    { "data": "youtube_link" }
                ]
            });
        });
    </script>

</body>
</html>
"""

# Create a Jinja2 template and render with data
template = Template(html_template)
html_output = template.render(table_data=data_json)

# Write the HTML to a file
output_file = 'output.html'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(html_output)

print(f"HTML file successfully created: {output_file}")
