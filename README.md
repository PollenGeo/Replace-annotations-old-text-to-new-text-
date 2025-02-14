=========================================
 OMERO Shape Comment Updater
=========================================

Description:
------------
This Python script allows users to update shape comments in OMERO based on a CSV file. 
It connects to an OMERO server, enables dataset selection or creation, and updates 
shape annotations in OMERO images according to the provided CSV data.

Features:
---------
- Connects to an OMERO server with user-provided credentials.
- Lists available OMERO groups and allows switching between them.
- Enables users to select an existing dataset or create a new one.
- Reads a CSV file to update shape comments in OMERO.
- Links images to the specified dataset if they are not already associated.

CSV File Format:
----------------
The CSV file must contain the following columns:

| Column    | Description                                      |
|-----------|--------------------------------------------------|
| image_id  | ID of the OMERO image containing the shape.      |
| shape_id  | ID of the shape to be updated.                   |
| old_text  | The existing text comment on the shape.          |
| new_text  | The new text comment to update.                  |

Requirements:
-------------
The script requires the following Python libraries:
- pandas
- omero-gateway
- tkinter (built-in for most Python distributions)

Installation:
-------------
Before running the script, install the required dependencies:

1. Install necessary Python packages:
pip install pandas pip install omero-py

2. If `tkinter` is not installed, install it manually (Linux users only):
sudo apt-get install python3-tk

Usage:
------
1. Run the script:
python replacewithcsv.py
2. Enter OMERO server credentials when prompted.
3. Select or create an OMERO dataset.
4. Choose the CSV file containing the shape comments to update.
5. The script will process the file and update the shapes accordingly.

Author:
-------
This script was developed by **Daurys De Alba**.

For inquiries, contact:
- Email: daurysdealbaherra@gmail.com
- Email: DeAlbaD@si.edu
