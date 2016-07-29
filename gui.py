import os.path
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup as soup
import pkgutil


root = Tk()
root.title("Soup.io content downloader")
root.resizable(0, 0)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


root.iconbitmap(resource_path("icon.ico"))

root.minsize(400, 120)
root.maxsize(400, 120)

firstimage = ""

Label(root, text="Please, specify soup.io nickname:").grid(row=0, column=0, sticky=N, pady=10)
loginTextbox = Entry(root)
loginTextbox.grid(row=0, column=1, sticky=N, padx=10, pady=10)


def downloadimages():
    loginurl = str(Entry.get(loginTextbox))

    if loginurl == "":
        messagebox.showwarning("Uh-oh!", "I said \"specify soup.io nickname\", it won't work without this!")
    else:
        if "http://" in loginurl or "soup.io" in loginurl:
            messagebox.showwarning("Uh-oh!", "Just login, there's no need for full address!")
        else:
            path = loginurl + ' soup'
            if not os.path.exists(path):
                os.makedirs(path)

            i = 1
            website = "http://" + loginurl + ".soup.io"
            openwebsite = soup(urllib.request.urlopen(website), 'html.parser')
            imagelink = openwebsite.find_all(name="div", attrs={'class': 'imagecontainer'})

            temp = openwebsite.find(name="div", attrs={'class': 'imagecontainer'})
            firstimage = temp.find('img')['src']

            for src in imagelink:
                temp = src.find('img')['src']
                img_data = requests.get(temp).content
                if temp.find('.gif') != -1:
                    filename = os.path.join(path, str(i) + '.gif')
                    with open(filename, 'wb') as handler:
                        handler.write(img_data)
                    i += 1
                else:
                    filename = os.path.join(path, str(i) + '.png')
                    with open(filename, 'wb') as handler:
                        handler.write(img_data)
                    i += 1

            nextpage = openwebsite.find_all(name="a", attrs={'class': 'more keephash'})
            while str(nextpage):
                for item in nextpage:
                    nextpagelink = website + item['href']

                    while nextpagelink:
                        openwebsite = soup(urllib.request.urlopen(nextpagelink), "html.parser")
                        imagelink = openwebsite.find_all(name="div", attrs={'class': 'imagecontainer'})
                        nextpage = openwebsite.find_all(name="a", attrs={'class': 'more keephash'})

                        for g in nextpage:
                            nextpagelink = website + g['href']

                        for src in imagelink:
                            temp = src.find('img')['src']
                            img_data = requests.get(temp).content
                            if temp.find('.gif') != -1:
                                filename = os.path.join(path, str(i) + '.gif')
                                with open(filename, 'wb') as handler:
                                    handler.write(img_data)
                                i += 1
                            else:
                                filename = os.path.join(path, str(i) + '.png')
                                with open(filename, 'wb') as handler:
                                    handler.write(img_data)
                                    i += 1

                        if openwebsite.find_all(name="a", attrs={'class': 'more keephash'}) == []:
                            break
                if nextpagelink != []:
                    messagebox.showinfo("Download Successful", "All done!")
                    break
            root = ET.Element('root')
            tree = ET.ElementTree(root)
            username = ET.Element('username')
            imagelink = ET.Element('First-image')
            username.append(imagelink)
            root.append(username)
            username.set('login', loginurl)
            imagelink.text = firstimage

            tree.write(path + '/update.xml', xml_declaration=True, encoding='utf-8')

            return path


downloadButton = Button(root, text="Download", command=downloadimages).grid(row=1, columnspan=2, sticky=N)


def update():
    loginurl = str(Entry.get(loginTextbox))
    xmlfile = 'update.xml'

    if loginurl == "":
        messagebox.showwarning("Uh-oh!", "I said \"specify soup.io nickname\", it won't work without this!")
    else:
        if "http://" in loginurl or "soup.io" in loginurl:
            messagebox.showwarning("Uh-oh!", "Just login, there's no need for full address!")
        else:

            path = loginurl + ' soup'

            xmlpath = path + "/" + xmlfile

            date = datetime.now()
            pathupdate = str(date.day) + '-' + str(date.month) + '-' + str(date.year)
            fullpath = path + '/' + pathupdate

            if not os.path.isfile(xmlpath):
                messagebox.showwarning("Warning!",
                                       "You can't update your backup, you don't have any saved content yet!")

            else:

                website = "http://" + loginurl + ".soup.io"
                openwebsite = soup(urllib.request.urlopen(website), 'html.parser')
                imagelink = openwebsite.find_all(name="div", attrs={'class': 'imagecontainer'})
                temp = openwebsite.find(name="div", attrs={'class': 'imagecontainer'})
                firstimage = temp.find('img')['src']

                loadroot = ET.parse(path + "/" + xmlfile)
                xmlcontent = loadroot.getroot()

                for users in xmlcontent.findall('username'):
                    latestimage = users.find('First-image').text
                    latestimagestring = latestimage
                    if firstimage == latestimagestring:
                        messagebox.showinfo("Info", "Your backup is up to date!")
                    else:
                        messagebox.showinfo("Info", "Your backup is outdated, downloading missing files")

                        if not os.path.exists(fullpath):
                            os.makedirs(fullpath)

                        i = 1
                        for src in imagelink:
                            temp = src.find('img')['src']
                            img_data = requests.get(temp).content
                            if temp != latestimagestring:
                                if temp.find('.gif') != -1:
                                    filename = os.path.join(fullpath, str(i) + '.gif')
                                    with open(filename, 'wb') as handler:
                                        handler.write(img_data)
                                    i += 1
                                else:
                                    filename = os.path.join(fullpath, str(i) + '.png')
                                    with open(filename, 'wb') as handler:
                                        handler.write(img_data)
                                    i += 1
                            else:
                                messagebox.showinfo("Download Successful", "Finished!")
                                break
                        if i >= 19:

                            try:
                                nextpage = openwebsite.find_all(name="a", attrs={'class': 'more keephash'})
                                while str(nextpage):
                                    for item in nextpage:
                                        nextpagelink = website + item['href']

                                        while nextpagelink:
                                            openwebsite = soup(urllib.request.urlopen(nextpagelink), "html.parser")
                                            imagelink = openwebsite.find_all(name="div",
                                                                             attrs={'class': 'imagecontainer'})
                                            nextpage = openwebsite.find_all(name="a", attrs={'class': 'more keephash'})

                                            for g in nextpage:
                                                nextpagelink = website + g['href']

                                            for src in imagelink:
                                                temp = src.find('img')['src']
                                                img_data = requests.get(temp).content

                                                if temp != latestimagestring:
                                                    if temp.find('.gif') != -1:
                                                        filename = os.path.join(fullpath, str(i) + '.gif')
                                                        with open(filename, 'wb') as handler:
                                                            handler.write(img_data)
                                                        i += 1
                                                    else:
                                                        filename = os.path.join(fullpath, str(i) + '.png')
                                                        with open(filename, 'wb') as handler:
                                                            handler.write(img_data)
                                                        i += 1
                                                elif temp == latestimagestring:
                                                    messagebox.showinfo("Download Successful", "Finished!")
                                                    raise Exception

                                            if temp == latestimagestring:
                                                messagebox.showinfo("Download Successful", "Finished!")
                                                raise Exception

                            except Exception:
                                pass

                        root = ET.Element('root')
                        tree = ET.ElementTree(root)
                        username = ET.Element('username')
                        imagelink = ET.Element('First-image')
                        username.append(imagelink)
                        root.append(username)
                        username.set('login', loginurl)
                        imagelink.text = firstimage

                        tree.write(path + '/update.xml', xml_declaration=True, encoding='utf-8')


buttonUpdate = Button(root, text="Update already existing soup content", command=update)
buttonUpdate.grid(row=2, columnspan=2, sticky=N, padx=95, pady=10)

root.mainloop()
