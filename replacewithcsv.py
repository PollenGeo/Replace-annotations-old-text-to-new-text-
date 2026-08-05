import pandas as pd
from omero.gateway import BlitzGateway
from omero.rtypes import rstring
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


def connect_to_omero():
    """
    Connect to the OMERO server using user-provided credentials.
    """
    root = tk.Tk()
    root.withdraw()

    host = simpledialog.askstring("OMERO Login", "Enter OMERO Host:", initialvalue="xxx")#put your initial host
    username = simpledialog.askstring("OMERO Login", "Enter OMERO Username:")
    password = simpledialog.askstring("OMERO Login", "Enter OMERO Password:", show="*")

    conn = BlitzGateway(username, password, host=host, port=4064, secure=True)
    if not conn.connect():
        raise ConnectionError("Failed to connect to OMERO. Check your credentials.")

    print("Connected to OMERO successfully!")

    # Retrieve the list of groups and their IDs
    groups = conn.getGroupsMemberOf()
    group_dict = {g.getId(): g.getName() for g in groups}

    if not group_dict:
        raise ValueError("No groups found for this user.")

    # Display the list of available groups with their IDs
    group_options = "\n".join([f"ID: {g_id} - Name: {g_name}" for g_id, g_name in group_dict.items()])
    selected_group_id = simpledialog.askinteger("Select Group", f"Available groups:\n{group_options}\n\nEnter Group ID:")

    if selected_group_id not in group_dict:
        raise ValueError("Invalid Group ID selected.")

    # Switch to the selected group using its ID
    conn.setGroupForSession(selected_group_id)
    print(f"Switched to Group ID: {selected_group_id} ({group_dict[selected_group_id]})")

    return conn, selected_group_id


def select_datasets(conn, group_id):
    """
    Let the user pick one or MORE existing datasets (comma-separated IDs),
    or type '0' to select ALL datasets in the group.
    Returns a dict {dataset_id: dataset_wrapper_object}.
    """
    datasets = list(conn.getObjects("Dataset"))

    if not datasets:
        raise ValueError("No datasets found in this group.")

    # Build the full list of datasets (no truncation)
    dataset_dict = {d.getId(): d.getName() for d in datasets}
    dataset_options = "\n".join([f"ID: {d_id} - Name: {d_name}" for d_id, d_name in dataset_dict.items()])

    choice = simpledialog.askstring(
        "Select Dataset(s)",
        f"Available datasets ({len(dataset_dict)}):\n{dataset_options}\n\n"
        "Enter one or more Dataset IDs separated by commas (e.g. 451,452,455)\n"
        "or type '0' to select ALL datasets in this group:"
    )

    if choice is None or choice.strip() == "":
        raise ValueError("No dataset selected.")

    choice = choice.strip()

    if choice == "0":
        selected_datasets = {d_id: conn.getObject("Dataset", d_id) for d_id in dataset_dict}
        print(f"ALL datasets in the group were selected ({len(selected_datasets)} in total).")
        return selected_datasets

    # Parse comma-separated IDs
    selected_ids = []
    for part in choice.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            selected_ids.append(int(part))
        except ValueError:
            print(f"'{part}' This is not a valid ID; it is ignored.")

    if not selected_ids:
        raise ValueError("No valid Dataset IDs provided.")

    selected_datasets = {}
    for ds_id in selected_ids:
        if ds_id in dataset_dict:
            selected_datasets[ds_id] = conn.getObject("Dataset", ds_id)
            print(f"Selected dataset: '{dataset_dict[ds_id]}' (ID: {ds_id}).")
        else:
            print(f"Dataset ID {ds_id} not found in this group, it is ignored.")

    if not selected_datasets:
        raise ValueError("None of the entered dataset IDs are valid.")

    return selected_datasets


def update_comments_from_csv(conn, csv_file, dataset_map):
    """
    Update shape comments in OMERO based on values from a CSV file.
    Required columns: 'image_id', 'shape_id', 'old_text', 'new_text'.
    Optional column: 'dataset_id' -> which dataset (from dataset_map) to link each image to.
    If 'dataset_id' is not present and only one dataset was selected, that one is used for all rows.
    """
    data = pd.read_csv(csv_file)
    required_columns = {'image_id', 'shape_id', 'old_text', 'new_text'}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"The CSV file must contain the following columns: {required_columns}")

    has_dataset_column = 'dataset_id' in data.columns
    default_dataset = None
    if not has_dataset_column:
        if len(dataset_map) == 1:
            default_dataset = list(dataset_map.values())[0]
        else:
            print(
                "NOTICE: You selected multiple datasets, but the CSV file does not have a 'dataset_id' column. "
                "The automatic link from image to dataset will not be created; only the comments will be updated."
            )

    update_service = conn.getUpdateService()

    for _, row in data.iterrows():
        image_id = int(row['image_id'])
        shape_id = int(row['shape_id'])
        old_comment = str(row['old_text'])
        new_comment = str(row['new_text'])

        print(f"Processing Image ID={image_id}, Shape ID={shape_id}, Old='{old_comment}', New='{new_comment}'")

        image = conn.getObject("Image", image_id)
        if not image:
            print(f"Image ID {image_id} not found. Skipping Shape ID {shape_id}.")
            continue

        # Decide which dataset (if any) to link this image to
        target_dataset = None
        if has_dataset_column and not pd.isna(row['dataset_id']):
            row_ds_id = int(row['dataset_id'])
            target_dataset = dataset_map.get(row_ds_id)
            if target_dataset is None:
                print(f"dataset_id {row_ds_id} is not among the selected datasets. The image is not linked.")
        elif default_dataset is not None:
            target_dataset = default_dataset

        if target_dataset is not None:
            parent = image.getParent()
            if parent is None or parent.getId() != target_dataset.getId():
                target_dataset.linkImage(image)
                print(f"Image {image_id} linked to Dataset ID {target_dataset.getId()}.")

        # Retrieve the Shape by ID
        shape = None
        for roi in image.getROIs():
            for s in roi.getShapes():
                if s.getId().getValue() == shape_id:
                    shape = s
                    break
            if shape:
                break

        if not shape:
            print(f"Shape ID {shape_id} not found in Image ID {image_id}. Skipping...")
            continue

        if shape.getTextValue().getValue() != old_comment:
            print(f"Shape ID {shape_id} comment does not match '{old_comment}'. Skipping...")
            continue

        print(f"Updating Shape ID {shape_id} from '{old_comment}' to '{new_comment}'")
        shape.setTextValue(rstring(new_comment))
        update_service.saveAndReturnObject(shape)

    print("All updates completed successfully.")


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    conn = None
    try:
        conn, group_id = connect_to_omero()

        dataset_map = select_datasets(conn, group_id)

        messagebox.showinfo(
            "IMPORTANT",
            "The first row of the CSV file must have the following column titles:\n\n"
            "image_id, shape_id, old_text, new_text\n\n"
            "Optional column (if you selected more than one dataset):\n"
            "dataset_id"
        )

        csv_file = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )

        if not csv_file:
            print("No file selected. Exiting.")
        else:
            update_comments_from_csv(conn, csv_file, dataset_map)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()
