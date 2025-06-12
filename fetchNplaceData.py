import subprocess
import sys
import os

def run_script(script_name: str):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)

    print(f"🚀 Kicking off {script_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"--- Output from {script_name} ---")
        print(result.stdout)
        if result.stderr:
            print(f"--- Errors/Warnings from {script_name} ---")
            print(result.stderr)
        
        print(f"✅ {script_name} finished successfully!\n")
        return True
        
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find {script_name}. Make sure it's in the same directory.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {script_name} failed to execute.")
        print(f"--- Return Code: {e.returncode} ---")
        print(f"--- STDOUT ---")
        print(e.stdout)
        print(f"--- STDERR ---")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred while running {script_name}: {e}")
        return False

def main_pipeline():
    print("🔥 Starting the data pipeline: Fetch & Place! 🔥\n")
    
    if not run_script("nifty_ohlc_fetcher.py"):
        print("\nPipeline stopped due to an error in the fetching step. 🛑")
        sys.exit(1)
        
    if not run_script("send_new_data_to_postgre.py"):
        print("\nPipeline stopped due to an error in the database insertion step. 🛑")
        sys.exit(1)
        
    print("🎉🎉🎉 All done! Data has been fetched and placed successfully. 🎉🎉🎉")

if __name__ == "__main__":
    main_pipeline()
