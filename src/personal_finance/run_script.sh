#!/bin/zsh

# activate the virtual environment, because that's where all modules are installed, not in system python
source ~/scraping_env/bin/activate

# Navigate to the directory where your Python script is located
cd /home/eikov/fin

# Run your Python script
python3 scrape.py  #or latest version like v2.3.py

# optional: for better analysis create visual charts with pandas, mathplotlib
python3 pandamat.py

chmod +x run_script.sh
