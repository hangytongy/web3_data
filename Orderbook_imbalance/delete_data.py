import os
import csv
from datetime import datetime, timedelta

def delete_old_data():
    data_folder = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_folder):
        print("Data folder not found.")
        return

    current_date = datetime.now()
    cutoff_date = current_date - timedelta(days=5)

    for filename in os.listdir(data_folder):
        if filename.endswith("_data.csv"):
            file_path = os.path.join(data_folder, filename)
            
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Save the header
                rows_to_keep = [header]  # Start with the header
                
                for row in reader:
                    if 'AVERAGE' in row[0]:
                        rows_to_keep.append(row)
                    else:
                        try:
                            # Parse the timestamp for non-AVERAGE entries
                            row_date = datetime.strptime(row[0].split()[0], "%Y-%m-%d")
                            if row_date >= cutoff_date:
                                rows_to_keep.append(row)
                        except ValueError:
                            # If there's an error parsing the date, keep the row
                            rows_to_keep.append(row)
            # Write the filtered data back to the file
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows_to_keep)
            
            print(f"Processed {filename}: Removed old data.")

if __name__ == "__main__":
    delete_old_data()
    print("Data cleanup completed.")
