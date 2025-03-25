#!/bin/bash

# Directory containing the post files
POSTS_DIR="jk-chess/_posts"

# Check if the _posts directory exists
if [ ! -d "$POSTS_DIR" ]; then
  echo "Error: Directory $POSTS_DIR does not exist."
  exit 1
fi

# Iterate over each markdown file in the directory
for file in "$POSTS_DIR"/*.md; do
  # Extract the filename without the directory path
  filename=$(basename "$file")

  # Check if the filename matches the incorrect pattern
  if [[ ! "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+\.md$ ]]; then
    # Generate a new filename with the correct pattern
    new_filename=$(date +"%Y-%m-%d")-${filename}

    # Rename the file
    mv "$file" "$POSTS_DIR/$new_filename"
    echo "Renamed $filename to $new_filename"
  fi
done

echo "All files have been renamed."