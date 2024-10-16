import pandas as pd
import matplotlib.pyplot as plt
import os

def data_to_png(df,folder_directory,token):

    image_path = os.path.join(folder_directory,f'data_table_{token}.png')
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 4))  # Set the size of the image

    # Hide axes
    ax.axis('tight')
    ax.axis('off')

    # Create a table from the DataFrame
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # Style the table (optional)
    table.auto_set_font_size(False)  # Disable automatic font sizing
    table.set_fontsize(12)  # Set font size
    table.scale(1.2, 1.2)  # Scale table size

    # Save the figure as an image
    plt.savefig(image_path, bbox_inches='tight', dpi=300)  # Save as PNG
    plt.close()  # Close the figure

    print(f"Table saved to {image_path}")

    return image_path