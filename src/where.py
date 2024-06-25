import os

def main():
    # Get the absolute path of the directory where the script is located
    script_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"The script is run from: {script_dir}")

if __name__ == "__main__":
    main()
