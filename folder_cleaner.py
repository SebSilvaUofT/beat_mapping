import os
import pandas as pd


def clean_csv_filenames(csv_path, column_name='file name'):
    # Load the CSV file
    df = pd.read_csv(csv_path)

    # Strip leading spaces from 'file name' column
    # df[column_name] = df[column_name].astype(str).str.strip()
    #
    # # # Save the cleaned file
    # df.to_csv(csv_path, index=False)
    # print(f"Cleaned CSV file saved: {csv_path}")

    return df[column_name].tolist()  # Return the cleaned file names as a list

def check_file_uniqueness(csv_filenames, folder_path):
    """Checks that each file name in the CSV occurs exactly once in the folder."""
    folder_filenames = os.listdir(folder_path)  # Get all files in folder

    # Convert to sets for easy comparison
    csv_set = set(csv_filenames)
    folder_set = set(folder_filenames)

    # Find missing and extra files
    missing_files = csv_set - folder_set  # In CSV but not in folder
    extra_files = folder_set - csv_set    # In folder but not in CSV

    # Check for duplicates in folder
    duplicate_files = [file for file in folder_filenames if folder_filenames.count(file) > 1]

    # Print discrepancies
    if missing_files:
        print("\nMissing files (listed in CSV but not found in folder):")
        for file in missing_files:
            print(f"- {file}")

    if extra_files:
        print("\nExtra files (present in folder but not listed in CSV):")
        for file in extra_files:
            print(f"- {file}")

    if duplicate_files:
        print("\nDuplicate files (appear more than once in folder):")
        for file in set(duplicate_files):  # Use set to avoid duplicate messages
            print(f"- {file}")

    if not missing_files and not extra_files and not duplicate_files:
        print("\n✅ All files are present exactly once!")


def compare_filenames(excel_filenames, folder_path):
    # Get a sorted list of filenames from the folder
    folder_filenames = sorted(os.listdir(folder_path))

    # Compare the two lists
    discrepancies = []
    for i, (excel_file, folder_file) in enumerate(zip(excel_filenames, folder_filenames)):
        if excel_file != folder_file:
            discrepancies.append(f"Mismatch at index {i}: CSV='{excel_file}', Folder='{folder_file}'")

    # Check if folder has extra/missing files
    if len(excel_filenames) != len(folder_filenames):
        discrepancies.append(f"File count mismatch: CSV={len(excel_filenames)}, Folder={len(folder_filenames)}")

    # Print results
    if discrepancies:
        print("\nDiscrepancies found:")
        for issue in discrepancies:
            print(issue)
    else:
        print("\nAll filenames match in order!")


if __name__ == "__main__":
    # Specify paths
    csv_file_path = r"App Music Library.csv"  # Change this
    folder_to_check = r"C:\Users\Sebastian\PycharmProjects\beat_mapping\converted_wavs"  # Change this

    # Process CSV file
    cleaned_filenames = clean_csv_filenames(csv_file_path)

    # Compare with folder
    compare_filenames(cleaned_filenames, folder_to_check)
