#!/bin/zsh

#python step1-lolchamps.py
#echo "Step 1 complete: Scraped targeted data from URL"
echo "Step 1 Scrape targeted data from URL.TEMPORALY DISABLED TO NOT FLOOD THE URL"

python step2-lolchamps.py
echo "Step 2 complete: extracted Champion names and their Pick rates"

python step3-lolchamps.py
echo "Step 3 complete: made data two-dimensional with Pandas. Should probably save it somewhere"

#python step4-lolchamps.py
#enable only if lost lists of champion names
echo "Step 4 complete: saved champion names in a list"

#python step5-lolchamps.py
echo "Step 5 in Beta mode: trying to iterate through champion names and scrape their counters."
echo "DISABLED BECAUSE COUNTERS ARE ALREADY SCRAPED AND SAVED"
#scraped only best counters. but script is unable to click for 'more counters'

#python step6-lolchamps.py
echo "Step 6 in building mode: collecting synergies for each support champion"
#EUW and KR versions. Atm EUW works only. Currently it only shows DUO synergy, but I want ADC-SUPP-JUNGLER Synergy

python step7.py
echo "Step 7 in building mode: combining data into final_data"

chmod +x lolchamps.sh