# This is the file that brings all the code together and runs it.
from app import app

# Checking if this file is the entry point to the program.
if __name__ == "__main__":
    # If it is, then start the app with debug mode enabled.
    app.run(debug=True)

