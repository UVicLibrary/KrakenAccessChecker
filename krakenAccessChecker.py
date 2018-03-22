"""
----------------
accessChecker.py
----------------

To run:

Input csv file should have two columns
 - column one is the name of the vendor selected from the list below
 - column two is the url
 - column three is the title of journal

Execute the command: "python accessChecker.py {name_of_csv_file}"

Output will be written to accessCheckerResults.csv
"""

import sys
from bs4 import BeautifulSoup 
import csv
import re 
import requests 
from selenium import webdriver
import yaml


def get_columns():
    yml = open('AccessCheckerSettings.yml', 'r')
    settings = yaml.load(yml)
    columns = []
    for setting in settings["Columns"]:
        if settings["Columns"][setting]:
            columns.append(setting)
    yml.close()
    return columns

def get_rows(filename):
    file_extension = filename.split('.')[-1]
    if file_extension == "csv":
        f = open(filename,'r')
        reader=csv.reader(f)
    if file_extension == "txt":
        f = open(filename,'rU')
        reader=csv.reader((line.replace('\0','') for line in f),delimiter='\t')
        for _ in range(28):
            next(reader) # skip (**) headings
    header = next(reader)
    rows = [dict(zip(header, map(str, row))) for row in reader]
    f.close()
    for index,row in enumerate(rows):
        if not bool(row):
            del rows[index]
    return rows
    
def main(filename, vendor):
    columns = get_columns()
    rows= get_rows(filename)
    output = csv.writer(open('accessCheckerResults.csv', "w", newline=''))
    num_lines = len(open(filename).read().splitlines())
    output_header = ["Vendor"] + columns + ["Have Access?"]
    output.writerow(output_header)
    for index, row in enumerate(rows):
        message = globals().get(vendor)(row["Default URL"])
        print(str(index + 1) +  " of " + str(num_lines) + " | " + message + " | " + row["Default URL"])
        
        output_row = [vendor]
        for column in columns:
            if column in row:
                output_row.append(row[column]) 
            else:
                output_row.append('')
        output_row.append(message)
        output.writerow(output_row)
    #[vendor, row["Title"], row["Default URL"], message]
    

def adam(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')	
    if soup.find_all(text = re.compile("Download whole document")) or soup.find_all(text = re.compile("Download entire document")):
        return "Right On!"
    else: 
        return "Look into this . . . "

def asp(url, count, num_lines):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("div", id = "1"):
        return "Right On!"
    elif soup.find_all("title", text = re.compile("Trial login")):
        return "Nope!"
    else: 
        return "Look into this . . . "

def curio(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("div", class_="container content"): 
        return "Right On!"
    elif soup.find_all("h2", class_ = "pull-right"): 
        return "Nope!"
    else: 
        return "Look into this . . . "

def ebookcentral(url): #updated Feb 2018 PP
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(text = re.compile("Your institution has access")):
        return "Right On!"
    elif soup.find_all(text = re.compile("Sorry, this book is not available")):
        return "Nope!"
    else: 
        return "Look into this . . . "
"""
    browser = webdriver.PhantomJS() 
    browser.get(url)
    soup=BeautifulSoup(browser.page_source)
    if soup.find_all(text = re.compile("Your institution has access")):
        return "Right On!" 
    elif soup.find_all(text = re.compile("Your institution has access to 1 copy of this book.")):
        return "Right On! [supo]"  
    elif soup.find_all(text = re.compile("Sorry, this book is not available")):
        return "Nope!"
    else: 
        return "Look into this . . . "
"""
def ebsco(url):
    browser = webdriver.PhantomJS() 
    browser.get(url)
    soup=BeautifulSoup(browser.page_source)
    if soup.find_all("a", class_= "record-type pdf-ft") or soup.find_all("a", class_= "record-type epub"):
        return "Right on!"
    else: 
        return "Nope!"

def fod(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("i", class_= "fa fa-play") or soup.find_all(text = re.compile("Show Segments")):
        return "Right On!"
    elif soup.find_all("span", id = "MainContent_lblSearchTerm"): 
        return "Nope!"
    else: 
        return "Look into this . . . "

def gale(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')	
    if soup.find_all(text = re.compile("Table of Contents")):
        return "Right On!"
    else: 
        return "Look into this . . . "

def harvard(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')	
    if soup.find_all("li", class_= "paidAccess"):
        return "Right On!"
    elif soup.find_all("a", class_= "get-access"):
        return "Nope!"
    else: 
        return "Look into this . . . " 

def ilib(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(text = re.compile("Download Page Range")):
        return "Right On!"
    elif soup.find_all(text = re.compile("Access Error")):
        return "Nope!"
    else: 
        return "Look into this . . . "

#igi updated Oct 2017/PP        
def igiglobal(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(text = re.compile("Full-Book Download")):
        return "Right On!"
    elif soup.find_all(text = re.compile("Purchase")):
        return "Nope!"
    else: 
        return "Look into this . . . "
 
#ingenta created Feb 2018/PP       
def ingenta(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(src="/images/icon_s_square.gif"):
        return "Right On!"
    elif soup.find_all(src="/images/icon_f_square.gif"):
        return "Free content"
    elif soup.find_all(text = re.compile("Wiley-Blackwell")):
        return "has changed publishers to Wiley"
    elif soup.find_all(text = re.compile("Content Not Found")): 
        return "Content Not Found"
    else: 
        return "Look into this . . . "
def jstor(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("a", class_= "pdfLink tt-track-nolink"):
        return "Right On!"
    elif soup.find_all("span", text = re.compile("Your institution has not purchased this book from JSTOR.")): 
        return "Nope!"
    else: 
        return "Look into this . . . "

def muse(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("span", class_= "access_yes"):
        return "Right On!"
    elif soup.find_all("span", class_= "access_no"):
        return "Nope!"
    else: 
        return "Look into this . . . "

def nfb(url):
    r = requests.get(url[1])
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(text = re.compile("Access your rentals without")):
        return "Nope!"
    elif soup.find_all("div", class_= "embed-player-container"): 
        return "Right On!"
    else: 
        return "Look into this . . . "

#cannot get oxford to work? OCt 2017/PP
def oxford(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')	
    if soup.find_all(text = re.compile("availabilityIcon unlocked")):
        return "Right On!"
    elif soup.find_all(text = re.compile("availabilityIcon locked")):
        return "Nope!"
    else: 
        return "Look into this . . . "
        
#springer updated Oct 2017/PP
def springer(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("a", class_= "webtrekk-track pdf-link"):
        return "Right On!"
    elif soup.find_all("a", class_= "test-bookpdf-link"):
        return "Right On!"
    elif soup.find_all("a", class_= "access-link"):
        return "Nope!"
    elif soup.find_all("title", text = re.compile("Deleted DOI")):
        return "Deleted DOI!"
    elif soup.find_all("div", id = "error"):
        return "Page not found"
    else: 
        return "Look into this . . . "

def tandf(url):
    r = requests.get(url[1])
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all("a", text = re.compile("Download a copy")) or soup.find_all("a", text = re.compile("Quick access")):
        return "Right On!"
    elif soup.find_all("span", text = re.compile("Sorry, you do not have access to this book.")):
        return "Nope!"
    else: 
        return "Look into this . . . "
        
 #wiley updated Feb 2018/PP      
def wiley(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all(text = re.compile("You have full text access to this content")):
        return "Right On!" 
    elif soup.find_all(text = re.compile("Page not found")):
        return "Page not found"
    elif soup.find_all(text = re.compile("RMetS")):
        return "Royal Meteorological Society"
    elif soup.find_all(text = re.compile("AGU Publications")):
        return "AGU Publications"
    elif soup.find_all(text = re.compile("American Anthropological Association")):
        return "American Anthropological Association"
    elif soup.find_all(text = re.compile("You have free access to this content")):
        return "Free Access"
    elif soup.find_all(text = re.compile("BES Society Header")):
        return "british ecological society"
    elif soup.find_all(text = re.compile("Hub Branding")):
        return "Powered by Wiley"
    elif soup.find_all(text = re.compile("You have full text access to this Open Access content")):
        return "Open Access"
    else: 
        return "Look into this . . . "
# Run it!
if __name__ == "__main__":
    if sys.argv[1] and sys.argv[1] == "vendors":
        methods = list(globals())
        main_ind =  methods.index('main')
        for vendor in methods[main_ind+1:]:
            print(vendor)
    elif len(sys.argv) != 3:
        print("Correct Usage: "+sys.argv[0]+" file/path/and/name.ext vendor")
        print("To see a list of vendors run: "+sys.argv[0]+" vendors")
    else:
        main(sys.argv[1],sys.argv[2])