#!/bin/zsh

python step1-lolchamps.py
echo "Step 1 Scrape targeted data from URL."
#echo "TEMPORALY DISABLED, Data already extracted"
#TBD: show the date when was the last time it scraped, 

python step2-lolchamps.py
echo "Step 2 complete: extracted Champion names and their Pick rates"
#TBD: Winrates from diamond+

python step3-lolchamps.py
echo "Step 3 complete: made data two-dimensional with Pandas, just for fun"

python step4-lolchamps.py
#enable only if list of champion names are lost
echo "Step 4 complete: saved champion names in a list"
#echo "TEMPORALY DISABLED, champ names already saved"

python step5-lolchamps.py
echo "Step 5 in Beta mode: trying to iterate through champion names and scrape their counters."
#echo "DISABLED BECAUSE COUNTERS ARE ALREADY SCRAPED AND SAVED"
#scraped only best counters. but script is unable to click for 'more counters'

python step6-lolchamps.py
echo "Step 6 in Beta mode: collecting synergies for each support champion"
#echo "DISABLED BECAUSE SYNERGIES ARE ALREADY SCRAPED AND SAVED"
#EUW and KR versions. Atm EUW works only. Currently it only shows DUO synergy, but I want ADC-SUPP-JUNGLER Synergy

python step7-lolchamps.py
echo "Step 7 complete: combining data into final_data"

python step8-db.py
echo "Step 8 in beta mode: sending final_data to Postgres Server tables"

#last extraction: 2024/03/04
chmod +x lolchamps.sh