import time
import requests
from bs4 import BeautifulSoup

#global variables
WORD = ''
source = ''


def readfile():
    """reads the word text file and saves the text in variable WORD"""
    global WORD
    with open("word.txt", "r") as f:
        WORD = f.readlines(1)
        #while loop will continue reading file until it is not blank
        while WORD == []:
            time.sleep(2)
            WORD = f.readlines(1)
        f.close()


def deleteline():
    """Deletes the line from word.txt file"""
    with open("word.txt", "w") as f:
        f.write("")
        f.close()


def main():
    """collects the src data from url"""
    global source
    global WORD

    #converts the WORD from a list to a string
    WORD = '' + ''.join(WORD)

    #replaces any space in the WORD with a '+'
    WORD = WORD.replace(' ', '+')

    #inserts the WORD into the url, sends a get request, receives the data
    url = f'https://commons.wikimedia.org/w/index.php?search={WORD}&title=Special:MediaSearch&go=Go&type=image'
    req = requests.get(url)
    data = BeautifulSoup(req.text, 'html.parser')

    #finds all the images in the data, converts first image into a string then separates list elements by space
    images = data.find_all('img', src = True)
    image_string = str(images[0])
    image_list = list(image_string.split(' '))

    #Searches for src word then saves it into source variable.
    for match in image_list:
        if 'src="' in match:
          source = match
    print(source)


def urllink():
    """Writes the url into url text file"""
    global source
    source = source[5:-1]
    with open("url.txt", "w") as f:
        f.write(source)
        f.close()


#--------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    readfile()
    deleteline()
    main()
    urllink()