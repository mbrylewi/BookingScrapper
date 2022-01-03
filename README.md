# Get started with the project
Start by running this command in your terminal to get the libraries so the code would work.

`$ pip install -r requirements.txt`


# How to use

To execute the script related to the scrapper, you can do as mentionned :

`$ python scrapper.py --competitors <your_list_of_competitors> --datecheckin <YYYY-MM-DD> --interval <number> --outdir <path_of_directory> --verbosity`

<your_list_of_competitors" should be provided as : "competiror 1" "competiror 2" "competiror 3" "competiror n" (there is no limit)


# Execution of the command using the parser
Logs will tell at which part is the scrapper. (Creating the url,generating file,saving, etc...)
By default, logs are off. If you want them on, add the --verbosity paramater.

`$ python scrapper.py --competitors  "apa hotel" "washington hotel tokyo"  --datecheckin 2022-01-05 --outdir "C:/Users/Documents/generated_file" --interval 2 --verbosity`

This command will provide you data for APA Hotel and Washington Hotel Tokyo, for the dates of 2022-01-05 and 2022-01-06 since you provided the value 2 for the "interval" parameter. You will find the xlxs file saved under the path "C:/Users/Documents/generated_file".


For each parameter, there is an abbreviation.

- This command :

`$ python scrapper.py -c  "apa hotel" "washington hotel tokyo"  -d 2022-01-05 -o "C:/Users/Documents/generated_file"  -v`

- Is equivalent to this one : 

`$ python scrapper.py --competitors  "apa hotel" "washington hotel tokyo"  --datecheckin 2022-01-05 --outdir "C:/Users/Documents/generated_file"  --verbosity`




# Usable Parameters

| Parameter       | Abbreviation | Utility                                                                                                                                                     | Required | Default           |
|-----------------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------------|
| `--competitors` | `-c`         | Used to specify the name of the hotels you would like to scrap data about.                                                                                  | Yes      | None              |
| `--datacheckin` | `-d`         | Used to specify the checkin day.                                                                                                                            | No       | tomorrow          |
| `--outdir`      | `-o`         | Used to specify the directory of the output file.                                                                                                           | No       | current directory |
| `--interval`    | `-i`         | Used to specify the range in which the checkin date will fluctuate,  if interval=2 and checkin=2020-01-01, will provide data for 2020-01-01 and 2020-01-02. | No       | 1                 |
| `--verbosity`   | `-v`         | Use it if you want more logs during the process.                                                                                                            | No       | Off               |

* When a parameter is not required, you do not have to add  it the command.

For example :

- This  command will provide data for the hotels "Stay Japan Art Deco" and  "Le Meridien" for the tomorrow date (at the date you launch the script).

`$ python scrapper.py --competitors  "Stay Japan Art Deco" "Le Meridien "`


# Help and more

If you want more informations about how use the scrapper, go and type :

`$ python scrapper.py -h`

OR

`$ python scrapper.py --help`


# Others functions available in the program

### The scrapper function 

If you would like to retrieve all data from all the pages given an area, go ahead and add this line of code to `scrapper.py` :

`core.scrapper(destination='Tokyo Area',
              checkin='2022-03-03',
              path="C:\\Users\\kawaremu\\Desktop\\generated_files",
              interval=2,
              limit_page=2)`

You can change the parameters, as for path. By default, the files are generated in the **current directory**. 
If you add your own path, make sure to replace the slashes with "\\".


> You can limit the number of pages,if you do not, it will provide all the pages matching the request.

After pasting this 


### The simple_scrapper() function

Without saving the file,  you can check quickly the tendency of an area providing the date, it will not generate a file but will show you in the console.

* For example, you can get **simply the name and the hotel price** (without the details on the rooms and commodities), by adding this line of code to the main file `scrapper.py`:

`core.simple_scrapper(destination='Asakusa Area',
                     checkin='2022-01-10',
                     limit_page=10)`

