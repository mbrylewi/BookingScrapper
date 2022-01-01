# Get started with the project
Start by running this command in your terminal to get the libraries so the code would work.

`$ pip install -r requirements.txt`


# How to use

To execute the script related to the scrapper, you can do as mentionned :

`$ python scrappy.py --competitors <your_list_of_competitors> --checking <YYYY-MM-DD> --interval <number> --outdir <path_of_directory> --verbosity`

<your_list_of_competitors" should be provided as : "competiror 1" "competiror 2" "competiror 3" "competiror n" (there is no limit)


# Execution of the command using the parser
Logs will tell at which part is the scrapper. (Creating the url,generating file,saving, etc...)
By default, logs are off. If you want them on, add the --verbosity paramater.

`$ python scrapper.py --competitors  "apa hotel" "washington hotel tokyo"  --checkin 2022-01-05 --outdir "C:/Users/Documents/generated_file" --interval 2 --verbosity`

This command will provide you data for APA Hotel and Washington Hotel Tokyo, for the dates of 2022-01-05 and 2022-01-06 since you provided the value 2 for the "interval" parameter. You will find the xlxs file saved under the path "C:/Users/Documents/generated_file".


For each parameter, there is an abbreviation, the same command is equivalent in this form : 

`$ python scrapper.py -c  "apa hotel" "washington hotel tokyo"  -d 2022-01-05 -o "C:/Users/Documents/generated_file"  -v`


# Help and more

If you want more informations about how use the scrapper, go and type :

python scrapper.py -h 

OR

python scrapper.py --help


# Usable Parameters

| Parameter     | Utility                                                                                                                                                     | Required | Default           |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------------|
| `competitors` | Used to specify the name of the hotels you would like to scrap data about.                                                                                  | Yes      | None              |
| `datacheckin` | Used to specify the checkin day.                                                                                                                            | No       | tomorrow          |
| `outdir`      | Used to specify the directory of the output file.                                                                                                           | No       | current directory |
| `interval`    | Used to specify the range in which the checkin date will fluctuate,  if interval=2 and checkin=2020-01-01, will provide data for 2020-01-01 and 2020-01-02. | No       | 1                 |
| `verbosity`   | Use it if you want more logs during the process.                                                                                                            | No       | Off               |


When a parameter is not required, you do not have to add  it the command.

For example :

`$ python scrapper.py --competitors  "Stay Japan Art Deco" "Le Meridien "  --checkin 2022-02-03`
