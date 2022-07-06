#This was written to crawl through the 3000+ MS job postings and filter them down via Regular Expressions.
#my god have mercy on my soul.

import re
import requests #this needs to be installed via pip
import json
import subprocess
import webbrowser


LOCATIONS = ["redmond", "bellevue"]
SEARCH = "software engineer"
NEGATIVETITLE = ["senior", "principal", "lead","manager", "sr ", "sr.", "security", "linux", "research", "phd", "principle", "ios", "javascript", "csi", "ux", "2", "ii"] #things the title CANNOT
TITLES = ["software engineer", "software developer", "sde"] #things that the title MUST include
NEGATIVEDETAILS = ["3+", "4+", "5+", "6+", "7+", "8+", "9+", "3 years", "4 years", "5 years", "6 years", "7 years", "8 years", "9 years"] #job details cannot include these strings
DETAILS = ["c++"] #job details MUST include these


def qualify(job):
    locQualify = False
    #apply screening job filters (title, location, etc.)
    for loc in LOCATIONS:
        if loc in job["location"].lower():
            locQualify = True

    titleQualify = False #if one or more title appears in the job, we qualify
    for t in TITLES:
        if t in job["title"].lower():
            titleQualify = True

    for t in NEGATIVETITLE:
        if t in job["title"].lower():
            return False
    return titleQualify and locQualify
    

def detailQualify(job):
    r = requests.get("https://careers.microsoft.com/us/en/job/" + job["jobId"])
    thing = r.text
    #bit ugly, but it shortens our string to look at to just the info we are looking for.
    searchResults =  re.findall("<!--\*\/ var phApp = phApp.+", r.text)[0]
    for exp in NEGATIVEDETAILS:
        if exp in searchResults.lower():
            return False

    detailFound = False
    for detail in DETAILS:
        if detail in searchResults.lower():
            detailFound = True
    return detailFound

def populateJobs():
    searchUrl = "https://careers.microsoft.com/us/en/search-results?keywords=" + SEARCH.replace(" ", "%20") + "&from=%PAGE%&s=1"
    page = 0
    jobs = []
    while True:
        
        r = requests.get(searchUrl.replace("%PAGE%", str(page)))
        thing2 = r.text
        thing2.replace("\\n", "\n")
        #f = open("test.txt", "w+")
        #bit ugly, but it shortens our string to look at to just the info we are looking for.
        searchResults =  re.findall("\"eagerLoadRefineSearch.+(?=}; phApp)", r.text)[0]
        searchResults = searchResults.replace("\"eagerLoadRefineSearch\":","") #it is going to be easier to read if we remove this key.
        resultMap = json.loads(searchResults)
        print(str(int((page/ resultMap["totalHits"])*100)))
        
        for job in resultMap["data"]["jobs"]:

            if qualify(job):
                if detailQualify(job):
                    jobs.append(job["jobId"] + " https://careers.microsoft.com/us/en/job/" + job["jobId"])
                    #print(job["jobId"] + " https://careers.microsoft.com/us/en/job/" + job["jobId"])
        page += 50
        if page > resultMap["totalHits"]:
            break
    return jobs

def manualLook(jobList):

    for job in reversed(jobList):
        Id, url = job.split(" ") 
        webbrowser.open(url)
        bInput = input("Do you want job " + Id + ": ")

        if bInput == "n":
            jobList.remove(job)
    

    #at the very end:
    print("=========================================================")
    for j in jobList:
        print(j)


jobList = populateJobs()

manualLook(jobList)

