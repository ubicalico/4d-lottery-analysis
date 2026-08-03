One of the reason I built this is after chancing upon this neat [StackExchange article about randomness](https://math.stackexchange.com/questions/1267708/what-is-a-formal-definition-of-randomness).
There was so much historical data about 4D results. SG pools digitised those records so now data stretches as far back to 1980's.

## Libraries used

- **requests** — as the name implies, it is used to request for the resource from 4d website
- **pandas** — data cleaning, manipulation blah blah...
- **BeautifulSoup** - my poly lecturer would be proud of me for using this, your good ol webscraper
- **matplotlib** - interacts with the cleaned up data in pandas to visualise the trends and display the charts

## Usage

Created a neat little CLI (with aid from Claude since this code is severely outdated to be put public). 
Some of the libraries may or may not be required but best is to follow `requirements.txt`

```
pip install -r requirements.txt

python main.py all            # scrape (if no cache), analyse, visualise
python main.py scrape         # just download / resume
python main.py analyse        # print the summary report
python main.py visualise      # render charts into output/
```

Options: `--mode all` queries each of the 10,000 numbers explicitly (1,000
requests) instead of the permutation trick; `--batch-size` and `--delay`
tune request pacing; `--top N` sizes the top/bottom charts; `all --force`
re-scrapes over the cache.

## What have we observed



## What have I realised

After looking at all the numbers and trends, hours into building this code; there is one terrifying truth. Lottery is random. 
These trends sticks out because it is bound to happen. Some one once said that luck runs in circles, which also explains why Pi keeps showing up when theory of probability and statistics regarding randomness is discussed.
