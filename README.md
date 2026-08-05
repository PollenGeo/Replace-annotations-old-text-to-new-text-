=========================================
 OMERO Shape Comment Updater
=========================================

Description:
------------
This Python script allows users to update shape comments in OMERO based on a CSV file.
It connects to an OMERO server, enables selection of one, several, or all datasets in a
group, and updates shape annotations in OMERO images according to the provided CSV data.

Features:
---------
- Connects to an OMERO server with user-provided credentials.
- Lists available OMERO groups and allows switching between them.
- Lists all datasets available in the selected group.
- Allows selecting a single dataset, multiple datasets (comma-separated IDs),
  or ALL datasets in the group at once (by entering '0').
- Reads a CSV file to update shape comments in OMERO.
- Optionally links each image to its corresponding dataset if a 'dataset_id'
  column is included in the CSV (useful when working with multiple datasets).

CSV File Format:
----------------
The CSV file must contain the following columns:

| Column     | Required? | Description                                                        |
|------------|-----------|---------------------------------------------------------------------|
| image_id   | Yes       | ID of the OMERO image containing the shape.                        |
| shape_id   | Yes       | ID of the shape to be updated.                                     |
| old_text   | Yes       | The existing text comment on the shape (must match exactly).       |
| new_text   | Yes       | The new text comment to update.                                    |
| dataset_id | Optional  | ID of the dataset this image belongs to. Only used to auto-link    |
|            |           | the image to a dataset when more than one dataset was selected.    |

Notes:
- Column headers must be written exactly as shown above (lowercase).
- 'old_text' must match the current shape comment in OMERO exactly, or the
  row will be skipped.
- If only one dataset was selected and 'dataset_id' is not included, that
  single dataset is used automatically for all rows.
- If multiple datasets were selected (or all, via '0') and the CSV does not
  include 'dataset_id', comments will still be updated, but images will NOT
  be automatically linked to any dataset.

Requirements:
-------------
The script requires the following Python libraries:
- pandas
- omero-gateway (omero-py)
- tkinter (built-in for most Python distributions)

Installation:
-------------
Before running the script, install the required dependencies:

1. Install necessary Python packages:
   pip install pandas
   pip install omero-py

2. If `tkinter` is not installed, install it manually (Linux users only):
   sudo apt-get install python3-tk

Usage:
------
1. Run the script:
   python replacewithcsv.py

2. Enter OMERO server credentials when prompted.

3. Select the OMERO group you want to work in.

4. Select dataset(s):
   - Enter a single Dataset ID (e.g. 451)
   - Enter multiple Dataset IDs separated by commas (e.g. 451,452,455)
   - Enter '0' to select ALL datasets in the current group

5. Choose the CSV file containing the shape comments to update.

6. The script will process the file, update the shape comments, and (if
   applicable) link images to their corresponding datasets.

Author:
-------
This script was developed by **Daurys De Alba**.

For inquiries, contact:
- Email: daurysdealbaherra@gmail.com
- Email: DeAlbaD@si.edu
