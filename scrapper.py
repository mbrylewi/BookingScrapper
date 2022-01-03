import datetime
import core
import os
import argparse

today = datetime.date.today()

parser = argparse.ArgumentParser(prog='Booking Scrapper',
                                 usage='Booking Scrapper for KEN',
                                 description='Given a list of competitors, checkin date, provides a sheet with informations about the hotel.')


parser.add_argument("-c","--competitors", 
                    nargs='+',
                    help='Used to specify the name of the hotels you would like to scrap data about.')

parser.add_argument("-d","--datecheckin",
                    default=today,
                    help='Used to specify the checkin day.')

parser.add_argument("-o","--outdir",
                    default=os.getcwd(),
                    help='Used to specify the directory of the output file.')

parser.add_argument("-i","--interval",
                    type=int,
                    default=1,
                    help='Used to specify the range in which the checkin date will fluctuate, if interval=2 and checkin=2020-01-01, will provide data for 2020-01-01 and 2020-01-02.')

parser.add_argument("-v","--verbosity",
                    default=False,
                    help='Use it if you want more logs during the process.',
                    action='store_true')

args = parser.parse_args()

if args.competitors == '':
  parser.error('No action performed, --competitors parameter required')


core.scrapper_competitive(competitors=args.competitors,
                          checkin=args.datecheckin,
                          path=args.outdir,
                          interval=args.interval,
                          is_verbose=args.verbosity)



core.scrapper(destination='Tokyo Area',
              checkin='2022-03-03',
              path="C:\\Users\\kawaremu\\Desktop\\generated_files",
              interval=2,
              limit_page=2)

core.simple_scrapper(destination='Asakusa Area',
                     checkin='2022-01-10',
                     limit_page=10)

