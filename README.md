# JHU Duty Scheduler

While there are codes (check sources below) that help with generating duty schedule, we want to have a fairer method that doesn't require running codes over and over again. Also, with the emergence of a new ways to do duty, we want to regenerate pair duty for the weekend as well. 

### Note: Please look at the sample files to see how to create a txt file

## File txt

The format for each RA in txt file is:
```
Name | Building | Number of weekdays already finished | Number of weekends already finished | Dates unavailable to be on duty
```


## System Requirement

* Python 3.x

## Execution

We keep the same code format as source for easy execution, but we change the Python version. 

To generate a duty schedule, run:

``` Python
python scheduler.py -i input.txt -o output.txt -s mm/dd/yyyy -e mm/dd/yyyy -bs mm/dd/yyyy -be mm/dd/yyyy
```
Alternatively,

``` Python 3
python scheduler.py --infile someFile.txt --outfile someOutput.txt --start-date mm/dd/yyyy --end-date  mm/dd/yyyy --break-start-date  mm/dd/yyyy --break-end-date  mm/dd/yyyy --
```

Example run:
``` Python 3
python scheduler.py -i sample1.txt -o out1.txt -s 09/13/2019 -e 12/20/2019 -bs 11/27/2019 -be 11/29/2019 --available

python scheduler.py -i sample2.txt -o out2.txt -s 09/13/2019 -e 12/20/2019 -bs 11/27/2019 -be 11/29/2019 --two --available

```

If you need to generate two duties for two buildings in the weekend, add flag `-two` to script above. 

## TODO

* Code cleaning
* Web version (similar to Haroon's version)
* Day of the week (low priority since not encouraging this)
* Google Calendar API/Microsoft Calendar API
* Automatically detect multiple buildings
* Export to Calendar format

## Sources

Credit to original codes from [Haroon](https://github.com/hsghori/scheduler). 
