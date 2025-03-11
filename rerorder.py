import os
import pandas as pd


def clean_csv_filenames(csv_path, column_name='file name'):
    """Cleans leading spaces from the 'file name' column in the CSV."""
    df = pd.read_csv(csv_path)
    df[column_name] = df[column_name].astype(str).str.strip()
    df.to_csv(csv_path, index=False)
    print(f"Cleaned CSV file saved: {csv_path}")
    return df


def reorder_csv_to_match_folder(df, csv_path, column_name, folder_filenames):
    """Reorders the entire CSV file based on the order of filenames in the folder."""
    df[column_name] = df[column_name].astype(str)

    # Keep only rows that exist in the folder, then reorder them
    df_filtered = df[df[column_name].isin(folder_filenames)]
    df_sorted = df_filtered.set_index(column_name).reindex(folder_filenames).reset_index()

    # Save the reordered CSV
    df_sorted.to_csv(csv_path, index=False)
    print(f"CSV file reordered to match folder: {csv_path}")


def rename_files_to_match_csv(csv_filenames, folder_path):
    """Renames files in the folder to match the order of the CSV filenames."""
    folder_filenames = sorted(os.listdir(folder_path))  # Get current files in folder

    if len(csv_filenames) != len(folder_filenames):
        print("Mismatch in number of files! Cannot safely rename.")
        return

    for old_name, new_name in zip(folder_filenames, csv_filenames):
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        if old_name != new_name:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")


def main():
    # Specify paths
    csv_file_path = "App Music Library.csv"
    folder_to_check = "converted_wavs"
    column_name = "file name"

    # Process CSV file
    df = clean_csv_filenames(csv_file_path, column_name)
    csv_filenames = df[column_name].tolist()

    # Get folder filenames
    folder_filenames = sorted(os.listdir(folder_to_check))

    # Ask user what to do
    choice = input("Do you want to (1) reorder CSV to match folder or (2) rename folder files to match CSV? ")

    if choice == "1":
        reorder_csv_to_match_folder(df, csv_file_path, column_name, folder_filenames)
    elif choice == "2":
        rename_files_to_match_csv(csv_filenames, folder_to_check)
    else:
        print("Invalid choice. No changes made.")


if __name__ == "__main__":
    main()
