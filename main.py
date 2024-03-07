import requests
from bs4 import BeautifulSoup
import math
import openai
import time
import openpyxl
import pandas as pd

# Set your OpenAI API key
api_key = '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'
openai.api_key = api_key

l = []
target_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search/?&geoId=91000006&location=Wien%2C%20Österreich&start={}'
df = pd.DataFrame(columns=['Jobname', 'Firma','Standort','Karrierestufe', 'Tätigkeitsbereich','Beschäftigungsverhältns', 'Branche','Fähigketen'])

for i in range(0,3): # math.ceil(11700/25)):

    res = requests.get(target_url.format(i))
    soup = BeautifulSoup(res.text, 'html.parser')
    alljobs_on_this_page = soup.find_all("li")
    jobcollection=[]
    for x in range(0, len(alljobs_on_this_page)):
        job_url = alljobs_on_this_page[x].find("a").get("href")
        job = requests.get(job_url)
        jobsoup = BeautifulSoup(job.text, 'html.parser')
        thisjobs = jobsoup.find_all("div", class_="description__text description__text--rich")
        information=[0,0,0,0]
        information = jobsoup.find_all("span",
                                 class_="description__job-criteria-text description__job-criteria-text--criteria")



        titel = jobsoup.find("h1",class_="top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title")
        company = jobsoup.find("a",class_="topcard__org-name-link topcard__flavor--black-link")

        location = jobsoup.find("span",class_="topcard__flavor topcard__flavor--bullet")
        #jobcollection.append([thisjobs[0].text,information[0].text,information[1].text,information[2].text,information[3].text,titel.text,company.text,location.text])

        print(thisjobs[0].text)
        print(job_url)
        try: print(information[0].text)
        except IndexError:
            information[0] =0
        try:
            print(information[1].text)
        except  IndexError:
            information[1] = 0

        print(information[2].text)
        print(information[3].text)
        print(titel.text)
        print(company.text)
        print(location.text)

        job_text= thisjobs[0].text
        input_text = f"gib mir, falls vorhanden, die notwendige Ausbildung (bitte nicht in ganzen Sätzen, sondern nur den Ausdruck), und eine Liste der sonstigen Anforderungen an den Bewerber in Form einer Liste, möglichst kurz aus. Wenn der Text in einer anderen Sprache ist, bitte auf Deutsch übersetzen: "+ job_text

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Verwenden Sie das GPT-3.5-turbo-Modell
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_text}
            ]
        )
        newrow = {'Jobname': titel.text, 'Firma': company.text, 'Standort': location.text,
                  'Karrierestufe': information[0].text, 'Tätigkeitsbereich': information[2].text,
                  'Beschäftigungsverhältns': information[1].text,
                  'Branche': information[3].text, 'Fähigketen':response['choices'][0]['message']['content']}
        df = pd.concat([df, pd.DataFrame([newrow])], ignore_index=True)
        if_sheet_exists = 'overlay'
        writer = pd.ExcelWriter('jobs.xlsx', engine='openpyxl', mode='a',  if_sheet_exists='overlay')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()

        #df.to_excel('jobs.xlsx', index=False)

        print(response['choices'][0]['message']['content'])
        print(job_url)
        time.sleep(20)

