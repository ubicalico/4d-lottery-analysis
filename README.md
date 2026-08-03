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

## What has been observed
[bottom_numbers]: https://github.com/ubicalico/4d-lottery-analysis/blob/main/img/bottom_numbers.png
[heatmap]: https://github.com/ubicalico/4d-lottery-analysis/blob/main/img/digit_position_heatmap.png
[first_prize]: https://github.com/ubicalico/4d-lottery-analysis/blob/main/img/first_prize_top.png
[top_numbers]: https://github.com/ubicalico/4d-lottery-analysis/blob/main/img/top_numbers.png

Given that the probability of winning is 23 out of 10,000 and 4D has been around for awhile; all the possible permutations has won a prize at least twice. 
![bottom numbers][bottom_numbers]

This heatmap is interesting. What we know as random, does not exist mathematically. We can see that the number 6 in 2nd position has the least occurrence while number 4 in 3rd position is the most occuring. If it's random, do we expect this heatmap to be more evenly-distributed?
![heatmap][heatmap]

So are things still really random? Some of these numbers have been tested through the draw times and coming out ahead not once at least 4 times! Other than that, what do these numbers have in common? They form parts of the Pi digits.
![first_prize][first_prize]

What if you don't want to win the top prize? What if you just want to bet on the best performing number? The number that has came out at least once every 2.5 years since the inception of 4D? Well, that number is 9395 with a staggering 29 appearances. A bit of stretch but 9395 has 95 which is also part of the empirical rule of the normal distribution within two standard deviations. Don't believe it? Still within this graph we have 9509 with 25 appearances, so go figure.
![top_numbers][top_numbers]

## What have I realised

After looking at all the numbers and trends, hours into building this code; there is one terrifying truth. Lottery is random. 
These trends sticks out because it is bound to happen mathematically. Some one once said that luck runs in circles, which also explains why Pi keeps showing up when theory of probability and statistics regarding randomness is discussed.

