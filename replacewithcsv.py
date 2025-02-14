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

    host = simpledialog.askstring("OMERO Login", "Enter OMERO Host:", initialvalue="xxx") #Put your initial host
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


def select_or_create_dataset(conn, group_id):
    """
    Allow the user to select an existing dataset (by ID) or create a new one.
    """
    datasets = list(conn.getObjects("Dataset"))

    if not datasets:
        print("No datasets found in this group. A new dataset will be created.")
        dataset_name = simpledialog.askstring("Create Dataset", "Enter new dataset name:")
        if not dataset_name:
            raise ValueError("Dataset name is required.")

        dataset = conn.getUpdateService().saveAndReturnObject(
            conn.getObjectFactory().createDataset(name=dataset_name)
        )
        print(f"New Dataset '{dataset_name}' created with ID {dataset.getId()}.")
        return dataset

    # Display the list of available datasets with their IDs
    dataset_dict = {d.getId(): d.getName() for d in datasets}
    dataset_options = "\n".join([f"ID: {d_id} - Name: {d_name}" for d_id, d_name in dataset_dict.items()])

    dataset_choice = simpledialog.askinteger(
        "Select Dataset",
        f"Available datasets:\n{dataset_options}\n\nEnter Dataset ID or type '0' to create a new one:"
    )

    if dataset_choice == 0:
        dataset_name = simpledialog.askstring("Create Dataset", "Enter new dataset name:")
        if not dataset_name:
            raise ValueError("Dataset name is required.")

        dataset = conn.getUpdateService().saveAndReturnObject(
            conn.getObjectFactory().createDataset(name=dataset_name)
        )
        print(f"New Dataset '{dataset_name}' created with ID {dataset.getId()}.")
        return dataset
    elif dataset_choice in dataset_dict:
        dataset = conn.getObject("Dataset", dataset_choice)
        print(f"Using existing Dataset '{dataset_dict[dataset_choice]}' (ID: {dataset_choice}).")
        return dataset
    else:
        raise ValueError("Invalid Dataset ID selected.")


def update_comments_from_csv(conn, csv_file, dataset):
    """
    Update shape comments in OMERO based on values from a CSV file.
    The CSV file must contain the following columns: 'image_id', 'shape_id', 'old_text', and 'new_text'.
    """
    # Load the CSV file
    data = pd.read_csv(csv_file)
    required_columns = {'image_id', 'shape_id', 'old_text', 'new_text'}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"The CSV file must contain the following columns: {required_columns}")

    update_service = conn.getUpdateService()

    for _, row in data.iterrows():
        image_id = int(row['image_id'])
        shape_id = int(row['shape_id'])
        old_comment = str(row['old_text'])
        new_comment = str(row['new_text'])

        print(f"Processing Image ID={image_id}, Shape ID={shape_id}, Old='{old_comment}', New='{new_comment}'")

        # Retrieve the image
        image = conn.getObject("Image", image_id)
        if not image:
            print(f"Image ID {image_id} not found. Skipping Shape ID {shape_id}.")
            continue

        # Add image to the selected dataset (if not already linked)
        if image.getParent() is None or image.getParent().getId() != dataset.getId():
            dataset.linkObject(image)
            print(f"Image {image_id} linked to Dataset ID {dataset.getId()}.")

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

        # Validate the old comment
        if shape.getTextValue().getValue() != old_comment:
            print(f"Shape ID {shape_id} comment does not match '{old_comment}'. Skipping...")
            continue

        # Update the Shape comment
        print(f"Updating Shape ID {shape_id} from '{old_comment}' to '{new_comment}'")
        shape.setTextValue(rstring(new_comment))
        update_service.saveAndReturnObject(shape)

    print("All updates completed successfully.")


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    try:
        conn, group_id = connect_to_omero()

        # Select or create a dataset using its ID
        dataset = select_or_create_dataset(conn, group_id)

        # Show a message about the required CSV structure
        messagebox.showinfo(
            "IMPORTANT",
            "The first row of the CSV file must have the following column titles:\n\n"
            "image_id, shape_id, old_text, new_text"
        )

        # Ask the user to select the CSV file
        csv_file = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )

        if not csv_file:
            print("No file selected. Exiting.")
        else:
            update_comments_from_csv(conn, csv_file, dataset)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()
