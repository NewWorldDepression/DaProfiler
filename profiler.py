# profiler.py (adapted to new modules/mail/mail_gen.py)
from colorama.initialise import init

import threading
import time
import colorama
import treelib
import random
import sys
import os
import argparse
import json
import requests
import webbrowser
import socketio
import string
import logging

from tqdm import tqdm
from treelib import Node, Tree
from colorama import Fore, Back, Style, init
from statistics import mean
init(autoreset=True)

# modules
from modules.social_medias import wattpad_search
from modules.social_medias import skype_search
from modules.social_medias import copainsdavant_search
from modules.social_medias import instagram_search
from modules.social_medias import twitter_search
from modules.social_medias import facebook_search
from modules.social_medias import linkedin_search
from modules.official_documents import dirigeants_bfmtv
from modules.official_documents import death_records
from modules.official_documents import pagesblanches_search
from modules.mail import mail_gen
from modules.mail import scylla_sh
from modules.mail import mail_check
from modules.diplomes import last_diplomes
from modules.social_medias import soundcloud
from modules.visual import logging as visual_logging
from modules.api_modules import leakcheck_net

# Banner display
def banner():
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')

    print("""
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠾⠛⢉⣉⣉⣉⡉⠛⠷⣦⣄⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⣠⣴⣿⣿⣿⣿⣿⡿⣿⣶⣌⠹⣷⡀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣆⠉⠻⣧⠘⣷⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠈⠀⢹⡇⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⠛⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⢸⡇⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⢿⡆⠈⠛⠻⠟⠛⠉⠀⠀⠀⠀⠀⠀⣾⠃⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⡀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠃⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⠿⣦⣄⠀⠀⠀⠀⠀⠀⠀⣀⣴⠟⠁⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣦⠀⠀⠈⠉⠛⠓⠲⠶⠖⠚⠋⠉⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⢀⣄⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """)
    print("        Get someone's digital identity anonymously")
    print("             Made by "+Style.BRIGHT+Fore.RED+"NewWorldDepression "+Fore.RESET+Style.RESET_ALL+"with 💝")

banner()

# Get the arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Victim name")
parser.add_argument('-ln','--lastname',help="Last name of victim")
parser.add_argument('-json','--json',help="Print result in json")
parser.add_argument('-zp','--zp',help="Zip code (Optional)")

args = parser.parse_args()

# Set the vars
name       = (args.lastname or "").strip()
pren       = (args.name or "").strip()
json_print = (args.json or "").strip().lower()
zip_code   = (args.zp or "").strip()

def randomString(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

thisIsATmpTokenListener = randomString(25)

possible_usernames = []
folder_name = f"{pren}_{name}"

personnal_life = []
social_medias  = []

# Create the folder for the reports
os.makedirs('Reports/{}'.format(folder_name), exist_ok=True)

# Opening json report template
with open('modules/report.json','r', encoding='utf8') as data_file:
    data_export = json.load(data_file)

# initialize a bunch of keys if missing (defensive)
data_export.setdefault('DeathRecords', {})
data_export.setdefault('LinkedIN', {})
data_export.setdefault('AdressPhone', {})
data_export.setdefault('Diploma_Bac', {})
data_export.setdefault('CopainsDavant', {})
data_export.setdefault('Work', {})
data_export.setdefault('Twitter', {})
data_export.setdefault('Skype', {})
data_export.setdefault('Instagram', {})
data_export.setdefault('Facebook', {})
data_export.setdefault('Emails', {})
data_export.setdefault('UI', {'Pie': {}, 'Bar': {}})

# Main
# initialize defaults
copainsdavant_results = None
facebook_results = None
twitter_results = None
official_linkedin_search_results = None
avis_deces_results = None
bfmtv_results = None
instagram_results = None
skype_results = None
diplome_bac = None
pagesblanche = None
linkedin_results = None
possible_mail = []
skype2mail = []
pin2mail = None

try:
    if pren and name:
        print("\nFinding and filtering online identities ...")
        # Each external call is wrapped to avoid a hard crash if one fails
        try:
            copainsdavant_results = copainsdavant_search.copains_davant(name=name,pren=pren)
        except Exception:
            copainsdavant_results = None

        try:
            facebook_results = facebook_search.facebook_search(name=name,pren=pren)
        except Exception:
            facebook_results = None

        try:
            twitter_results = twitter_search.twitter_search(name=name,pren=pren)
        except Exception:
            twitter_results = None

        try:
            official_linkedin_search_results = linkedin_search.official_linkedin_search(pren=pren,name=name)
        except Exception:
            official_linkedin_search_results = None

        try:
            avis_deces_results = death_records.death_search(name=name,pren=pren)
        except Exception:
            avis_deces_results = None

        try:
            bfmtv_results = dirigeants_bfmtv.bfmtv_search(name=name,pren=pren)
        except Exception:
            bfmtv_results = None

        try:
            instagram_results = instagram_search.ig_search(name=name,pren=pren)
        except Exception:
            instagram_results = None

        try:
            skype_results = skype_search.skype_searchh(name=name,pren=pren)
        except Exception:
            skype_results = None

        try:
            diplome_bac = last_diplomes.last_diplomes_bac(name=name,pren=pren)
        except Exception:
            diplome_bac = None

        try:
            if zip_code:
                pagesblanche = pagesblanches_search.adresse_search(name=name,pren=pren,zipc=str(zip_code))
            else:
                pagesblanche = pagesblanches_search.adresse_search(name=name,pren=pren,zipc=None)
        except Exception:
            pagesblanche = None

        try:
            linkedin_results = linkedin_search.linkedin_search(name=name,pren=pren)
        except Exception:
            linkedin_results = None

        # some modules may perform background work (soundcloud, wattpad)
        try:
            soundcloud.webdriver_usage(name=name,pren=pren)
        except Exception:
            pass

        try:
            wattpad_results = wattpad_search.wattpad_module(pren,name)
        except Exception:
            wattpad_results = None

        # mails - using the robust functions from modules/mail/mail_gen.py
        try:
            possible_mail = mail_gen.check(name=name,pren=pren) or []
        except Exception:
            possible_mail = []

        try:
            skype2mail = mail_gen.skype2email(name=name,pren=pren) or []
        except Exception:
            skype2mail = []

        try:
            pin2mail = mail_gen.pinterest2email(name=name,pren=pren)
        except Exception:
            pin2mail = None

    else:
        # no input names provided
        linkedin_results = None
        facebook_results = None
        twitter_results = None
        avis_deces_results = None
        bfmtv_results = None
        instagram_results = None
        copainsdavant_results = None
        skype_results = None
        pagesblanche = None
        possible_mail = []
        skype2mail = []
        pin2mail = None
        pren = ""
        name = ""
except TypeError:
    linkedin_results = None
    facebook_results = None
    twitter_results = None
    avis_deces_results = None
    bfmtv_results = None
    instagram_results = None
    copainsdavant_results = None
    skype_results = None
    pagesblanche = None
    possible_mail = []
    skype2mail = []
    pin2mail = None
    pren = ""
    name = ""

average_age = []

tree = Tree()
tree.create_node(f"{pren} {name}", 1)
data_export['Name'] = pren
data_export['LastName'] = name

# Re-check diplomas (non-fatal)
try:
    diplome_bac = diplome_bac or last_diplomes.last_diplomes_bac(name=name,pren=pren)
except Exception:
    diplome_bac = diplome_bac

# Death records
if avis_deces_results:
    tree.create_node("Death Records",41518181871541514778,parent=1)
    for i in avis_deces_results[:5]:
        try:
            tree.create_node('{} | {}\t| {}'.format(i.get('Age','?'),i.get('Name','?'),i.get('Loc','?')),parent=41518181871541514778)
            try:
                average_age.append(int(i.get('Age',0)))
            except Exception:
                pass
        except Exception:
            pass
    data_export['DeathRecords']['Exists'] = True
    data_export['DeathRecords']['Records'] = avis_deces_results[:5]

# LinkedIn quick view
if linkedin_results:
    tree.create_node('LinkedIN Profile',15418911611515145145,parent=1)
    tree.create_node(linkedin_results,parent=15418911611515145145)

# Official LinkedIn via API
if official_linkedin_search_results:
    try:
        Loc           = official_linkedin_search_results.get('Loc')
        job           = official_linkedin_search_results.get('Job')
        email         = official_linkedin_search_results.get('email')
        urnid         = official_linkedin_search_results.get('urnid')
        url           = official_linkedin_search_results.get('url')
        twitters      = official_linkedin_search_results.get('twitters') or []
        birthdate     = official_linkedin_search_results.get('birthdate')
        phone_numbers = official_linkedin_search_results.get('phone_numbers') or []

        tree.create_node('LinkedIN (Via API)',15458156411556562162,parent=1)
        tree.create_node(f'UrnID : {urnid}',5151515155,parent=15458156411556562162)
        tree.create_node(f'Url   : {url}',55185514542335,parent=15458156411556562162)
        if twitters:
            tree.create_node('Twitters',25848145481514,parent=15458156411556562162)
            for t in twitters:
                tree.create_node(t,parent=25848145481514)
        if phone_numbers:
            tree.create_node('Phone Numbers',28945181781,parent=15458156411556562162)
            for p in phone_numbers:
                tree.create_node(p,parent=28945181781)
        if Loc:
            tree.create_node(f'Location : {Loc}',4561561510515656,parent=15458156411556562162)
        if job:
            tree.create_node(f'Job : {job}',511515,parent=15458156411556562162)
        if birthdate:
            tree.create_node(f'Birth Date : {birthdate}',5881981648,parent=1058151514851)
        if email:
            tree.create_node(f'Email : {str(email)}',parent=15458156411556562162)

        data_export['LinkedIN']['Exist']        = True
        data_export['LinkedIN']['Job']          = job
        data_export['LinkedIN']['urnid']        = urnid
        data_export['LinkedIN']['Url']          = url
        data_export['LinkedIN']['Twitters']     = twitters
        data_export['LinkedIN']['Birthdate']    = birthdate
        data_export['LinkedIN']['PhoneNumbers'] = phone_numbers
    except Exception:
        pass

# PagesBlanches (address / phone)
if pagesblanche:
    personnal_life.append('.')
    full_name = pagesblanche.get('Name')
    adress = pagesblanche.get('Adress')
    phone = pagesblanche.get('Phone')
    sure_status = pagesblanche.get('Not_Sure', False)

    data_export['AdressPhone']['Not_Sure'] = sure_status
    data_export['AdressPhone']['Exists'] = True
    data_export['AdressPhone']['FullName'] = full_name
    data_export['AdressPhone']['Phone'] = phone
    data_export['AdressPhone']['Adress'] = adress

    if sure_status:
        tree.create_node("Adress - Phone",2,parent=1)
    else:
        tree.create_node("Adress - Phone (You must verify this information)",2,parent=1)
    try:
        tree.create_node("Full Name : {}".format(full_name),22,parent=2)
        tree.create_node("Adress    : {}".format(adress),33,parent=2)
        tree.create_node("Phone     : {}".format(phone),44,parent=2)
        if pagesblanche.get('carrier'):
            tree.create_node('Carrier : {}'.format(pagesblanche.get('carrier')),894,parent=44)
        if pagesblanche.get('Loc_phone'):
            tree.create_node('Localisation : {}'.format(pagesblanche.get('Loc_phone')),55,parent=44)
            data_export['AdressPhone']['PhoneLocation'] = pagesblanche.get('Loc_phone')
        if pagesblanche.get('Type_tel'):
            tree.create_node('Type  : {}'.format(pagesblanche.get('Type_tel')),66,parent=44)
    except Exception:
        pass

# Diploma BAC
if diplome_bac and diplome_bac.get('Exists'):
    try:
        tree.create_node('DIPLOME BAC',58,parent=1)
        tree.create_node('Bac     : '+diplome_bac.get('Diplome',''),848151541514,parent=58)
        tree.create_node('Academy : '+diplome_bac.get('academie',''),848151241514,parent=58)
        tree.create_node('Mention : '+diplome_bac.get('mention',''),848151341514,parent=58)
        tree.create_node('City    : '+diplome_bac.get('ville',''),848151641514,parent=58)
        tree.create_node('Source  : '+diplome_bac.get('Link',''),45994851726,parent=58)

        data_export['Diploma_Bac']['Exists']   = True
        data_export['Diploma_Bac']['Academie'] = diplome_bac.get('academie')
        data_export['Diploma_Bac']['Mention']  = diplome_bac.get('mention')
        data_export['Diploma_Bac']['City']     = diplome_bac.get('ville')
        data_export['Diploma_Bac']['Diplome']  = diplome_bac.get('Diplome')
        data_export['Diploma_Bac']['Link']     = diplome_bac.get('Link')
    except Exception:
        pass

# Copains d'avant
if copainsdavant_results:
    personnal_life.append('.')
    data_export['CopainsDavant']['Exists'] = True
    try:
        tree.create_node("Copains d'avant",3,parent=1)
        tree.create_node('Full Name    : {}'.format(copainsdavant_results.get('full_name','')),77,parent=3)
        tree.create_node('Born Date    : {}'.format(copainsdavant_results.get('born','')),88,parent=3)
        tree.create_node('Location : {}'.format(copainsdavant_results.get('localisation','')),99,parent=3)
        tree.create_node('Url          : {}'.format(copainsdavant_results.get('url_full','')),111,parent=3)

        data_export['CopainsDavant']['FullName']   = copainsdavant_results.get('full_name')
        data_export['CopainsDavant']['BornDate']   = copainsdavant_results.get('born')
        data_export['CopainsDavant']['ProfileUrl'] = copainsdavant_results.get('url_full','').replace('https://','')
        data_export['CopainsDavant']['Location']   = copainsdavant_results.get('localisation')

        if copainsdavant_results.get('Other_locations'):
            chars = "abcdefghijklmnopqrstuvwxyz1234567890"
            number_sk = ''.join(random.choice(chars) for _ in range(6))
            tree.create_node('Other Locations',number_sk,parent=3)
            for i in copainsdavant_results.get('Other_locations'):
                if i != copainsdavant_results.get('localisation'):
                    tree.create_node(i,parent=number_sk)
            data_export['CopainsDavant']['OtherLocations'] = copainsdavant_results.get('Other_locations')

        if copainsdavant_results.get('pdp') and copainsdavant_results.get('pdp') != "None":
            try:
                tree.create_node('Profile Picture : {}'.format(copainsdavant_results.get('pdp')),151515454545,parent=3)
                data_export['CopainsDavant']['ProfilePicUrl'] = copainsdavant_results.get('pdp').replace('https://','')
            except Exception:
                pass

        if copainsdavant_results.get('Job') and copainsdavant_results.get('Job') != "None":
            try:
                tree.create_node('Job : {}'.format(copainsdavant_results.get('Job')),154156132489411,parent=3)
                data_export['CopainsDavant']['Job'] = copainsdavant_results.get('Job')
            except Exception:
                pass

        if copainsdavant_results.get('familial_situation') and copainsdavant_results.get('familial_situation') != "None":
            try:
                tree.create_node('Familial Situation : {}'.format(copainsdavant_results.get('familial_situation').strip()),44984154114515,parent=3)
                data_export['CopainsDavant']['FSituation'] = copainsdavant_results.get('familial_situation')
            except Exception:
                pass

        if copainsdavant_results.get('nb_enfants') and copainsdavant_results.get('nb_enfants') != "None":
            try:
                tree.create_node('Number of kids : {}'.format(copainsdavant_results.get('nb_enfants')),1654518948741,parent=3)
                data_export['CopainsDavant']['NbKids'] = copainsdavant_results.get('nb_enfants')
            except Exception:
                pass
    except TypeError:
        pass

# BFMtv / Work
if bfmtv_results:
    personnal_life.append('.')
    data_export['Work']['Exists'] = True
    try:
        data_export['Work']['FullName'] = bfmtv_results.get('full_name')
        data_export['Work']['BornDate'] = bfmtv_results.get('naissance')
        data_export['Work']['Company']  = bfmtv_results.get('company')
        data_export['Work']['Function'] = bfmtv_results.get('fonction')
        data_export['Work']['Warrant']  = bfmtv_results.get('mandats')
        data_export['Work']['Link']     = bfmtv_results.get('link','').replace('https://','')
        data_export['Work']['Capital']  = bfmtv_results.get('Capital')
        data_export['Work']['Desc']     = bfmtv_results.get('Desc')

        tree.create_node("Work - Job",4,parent=1)
        tree.create_node('Full Name  : {}'.format(bfmtv_results.get('full_name','')),222,parent=4)
        tree.create_node('Born Date  : {}'.format(bfmtv_results.get('naissance','')),333,parent=4)
        tree.create_node('Adress     : {}'.format(bfmtv_results.get('addr','')),888,parent=4)
        tree.create_node('Company    : {}'.format(bfmtv_results.get('company','')),777,parent=4)
        tree.create_node('Desc       : {}'.format(bfmtv_results.get('Desc','')),78285,parent=4)
        tree.create_node('Capital    : {}'.format(bfmtv_results.get('Capital','')),84566,parent=4)
        tree.create_node('Link       : {}'.format(bfmtv_results.get('link','')),666,parent=4)
        tree.create_node('Function   : {}'.format(bfmtv_results.get('fonction','')),444,parent=4)
        tree.create_node('Warrant    : {}'.format(bfmtv_results.get('mandats','')),555,parent=4)
    except Exception:
        pass

# Twitter
if twitter_results:
    social_medias.append('.')
    data_export['Twitter']['Exists'] = True
    data_export['Twitter']['Accounts'] = twitter_results
    tree.create_node('Twitters',665847555858,parent=1)
    for i in twitter_results:
        temp = []
        chars = "abcdefghijklmnopqrstuvwxyz1234567890"
        number_sk = ''.join(random.choice(chars) for _ in range(6))
        domain_list = ['@gmail.com','@hotmail.fr','@hotmail.com','@orange.fr','@outlook.com','@outlook.fr']
        for domain in domain_list:
            try:
                a = mail_check.verify(i.replace('@','')+domain)
            except Exception:
                a = None
            if a == "True" or a is True:
                temp.append(i.replace('@','').lower()+domain)
        if len(temp) == 0:
            tree.create_node(i,parent=665847555858)
        else:
            tree.create_node(i,number_sk,parent=665847555858)
            for temp_mail in temp:
                tree.create_node(temp_mail,parent=number_sk)

# Skype results display
if skype_results:
    social_medias.append('.')
    data_export['Skype']['Exists'] = True
    data_export['Skype']['AccountList'] = skype_results
    if len(skype_results) > 0:
        tree.create_node("Skype",6,parent=1)
        tree.create_node("Accounts : {}".format(str(len(skype_results))),12,parent=6)
        for i in skype_results:
            chars = "abcdefghijklmnopqrstuvwxyz1234567890"
            number_sk = ''.join(random.choice(chars) for _ in range(6))
            tree.create_node(i,number_sk,parent=12)

# Diplomas (brevet)
try:
    diplomess = last_diplomes.last_diplomes_brevet(name=name,pren=pren)
except Exception:
    diplomess = None

if diplomess:
    try:
        tree.create_node('BREVET DES COLLEGES',452,parent=1)
        tree.create_node('Name     : {}'.format(diplomess.get('Name','')),1816864648,parent=452)
        tree.create_node('Diploma  : {}'.format(diplomess.get('Diplome','')),45855887,parent=452)
        tree.create_node('Details  : {}'.format(diplomess.get('mention','')),45855847,parent=452)
        tree.create_node('Academy  : {}'.format(diplomess.get('academie','')),45855687,parent=452)
        tree.create_node('Location : {}'.format(diplomess.get('ville','')),45855881,parent=452)
        tree.create_node('Source   : {}'.format(diplomess.get('Link','')),45896472,parent=452)

        data_export['Diploma_Brevet'] = {
            'Name': diplomess.get('Name'),
            'Exists': True,
            'Academie': diplomess.get('academie'),
            'Mention': diplomess.get('mention'),
            'City': diplomess.get('ville'),
            'Link': diplomess.get('Link'),
        }
    except Exception:
        pass

# Instagram
if instagram_results:
    if len(instagram_results) > 0:
        social_medias.append('.')
        data_export['Instagram']['Exists'] = True
        tree.create_node("Instagram",7,parent=1)
        tree.create_node('Accounts : {}'.format(str(len(instagram_results))),13,parent=7)
        acc_json_list = []
        for i in instagram_results:
            chars = "abcdefghijklmnopqrstuvwxyz1234567890"
            username = i
            number_ski = ''.join(random.choice(chars) for _ in range(6))
            try:
                bio_infos = instagram_search.getInstagramEmailFromBio(username)
            except Exception:
                bio_infos = {'emails': [], 'paypal': [], 'city_list': [], 'lgbt_points': None, 'school': None,
                             'best_friend': None, 'love_date': None, 'age': None, 'origins': None,
                             'fb_list': None, 'twitter_list': None, 'Hobbies': None, 'love_situation': None,
                             'religions': None, 'astrology': None}
            tree.create_node(i,number_ski,parent=13)
            try:
                data = instagram_search.get_extra_data(username)
                ob_phone = False
                ob_mail  = False
                if data and data != {}:
                    if data.get('obfuscated_email') is not None:
                        ob_mail = data.get('obfuscated_email')
                        tree.create_node("Obfuscated Email -> "+ob_mail,parent=number_ski)
                    if data.get('obfuscated_phone') is not None:
                        ob_phone = data.get('obfuscated_phone')
                        tree.create_node("Obfuscated Phone -> "+ob_phone,parent=number_ski)
            except Exception:
                ob_phone = False
                ob_mail = False

            acc_json_list.append({"Username":username,'obfuscated_phone':ob_phone,'obfuscated_email':ob_mail})

            bio_emails = bio_infos.get('emails', [])
            paypal_bio = bio_infos.get('paypal', [])
            city_loc   = bio_infos.get('city_list', [])
            is_lgbt    = bio_infos.get('lgbt_points')
            schoolname = bio_infos.get('school')
            bestfriend = bio_infos.get('best_friend')
            love_date  = bio_infos.get('love_date')
            age_bio    = bio_infos.get('age')
            ethnicity  = bio_infos.get('origins')
            facebook_l = bio_infos.get('fb_list')
            twitter_l  = bio_infos.get('twitter_list')
            hobbies    = bio_infos.get('Hobbies')
            love_situa = bio_infos.get('love_situation')
            religions  = bio_infos.get('religions')
            astrologys = bio_infos.get('astrology')

            if love_situa:
                nnumber_ski = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node('Love Situation',nnumber_ski,parent=number_ski)
                for it in love_situa:
                    tree.create_node(it,parent=nnumber_ski)
            if astrologys:
                nnumber_ski = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node('Astrologic sign',nnumber_ski,parent=number_ski)
                for it in astrologys:
                    tree.create_node(it,parent=nnumber_ski)
            if religions:
                nnumber_ski = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node('Religion(s)',nnumber_ski,parent=number_ski)
                for it in religions:
                    tree.create_node(it,parent=nnumber_ski)
            if hobbies:
                nnumber_ski = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node('Hobbies',nnumber_ski,parent=number_ski)
                for it in hobbies:
                    tree.create_node(it,parent=nnumber_ski)
            if bestfriend:
                nnumber_ski = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node('Good relationship with',nnumber_ski,parent=number_ski)
                for it in bestfriend:
                    tree.create_node('{}'.format(it),parent=nnumber_ski)
            if is_lgbt:
                lgbt_flag = (Fore.RED+"█"+Fore.YELLOW+"█"+Fore.GREEN+"█"+Fore.BLUE+"█"+Fore.MAGENTA+"█"+Fore.RESET)
                tree.create_node('{} LGBT Member'.format(lgbt_flag),parent=number_ski)
            if ethnicity:
                tree.create_node('Ethnicity : {}'.format(str(ethnicity).replace('[','').replace(']','').replace("'","")),parent=number_ski)
            if facebook_l:
                tree.create_node('Facebook : {}'.format(str(facebook_l).replace('[','').replace(']','').replace("'","")),parent=number_ski)
            if twitter_l:
                tree.create_node('Twitter : {}'.format(str(twitter_l).replace('[','').replace(']','').replace("'","")),parent=number_ski)
            if schoolname:
                tree.create_node('School Name : {}'.format(schoolname),parent=number_ski)
            if city_loc:
                tree.create_node('City : {}'.format(city_loc[0]),parent=number_ski)
            if paypal_bio:
                for it in paypal_bio:
                    tree.create_node('Paypal in bio -> '+it,parent=number_ski)
            if bio_emails:
                for it in bio_emails:
                    chars = "abcdefghijklmnopqrstuvwxyz1234567890"
                    number_skkk = ''.join(random.choice(chars) for _ in range(6))
                    number_skk = ''.join(random.choice(chars) for _ in range(6))
                    tree.create_node('Email from bio -> '+Fore.CYAN+it+Fore.RESET,number_skkk,parent=number_ski)
        data_export['Instagram']['AccountList'] = acc_json_list

# Facebook
if facebook_results:
    social_medias.append('.')
    data_export['Facebook']['Exists'] = True
    nb = str(len(facebook_results))
    tree.create_node("Facebook",9,parent=1)
    tree.create_node('Accounts : {}'.format(nb),10,parent=9)
    data_export['Facebook']['AccountList'] = facebook_results
    for i in facebook_results:
        tree.create_node(i,parent=10)

# Emails extraction / leaks
if (possible_mail and len(possible_mail) > 0) or (skype2mail and len(skype2mail) > 0) or (pin2mail is not None):
    tree.create_node('Emails extracted',146,parent=1)

    # skype-derived emails (high prob)
    if skype2mail:
        tree.create_node('[++] High probability',142,parent=146)
        no_doubles = []
        for email in skype2mail:
            if email in no_doubles:
                continue
            chars = "abcdefghijklmnopqrstuvwxyz1234567890"
            number = ''.join(random.choice(chars) for _ in range(6))
            no_doubles.append(email)
            tree.create_node(email,number,parent=142)

            # scylla results
            try:
                scylla_results = scylla_sh.scylla_search(email=email)
            except Exception:
                scylla_results = None
            if scylla_results:
                tree.create_node('Leaked From : Scylla.sh',1518451,parent=number)
                for leak in scylla_results:
                    try:
                        chars = "abcdefghijklmnopqrstuvwxyz1234567890"
                        number_leak = ''.join(random.choice(chars) for _ in range(6))
                        tree.create_node('Leak Name : {}'.format(leak.get('Name','?')),parent=1518451)
                        tree.create_node('Password  : {}'.format(leak.get('Password','?')),parent=1518451)
                    except Exception:
                        pass

            # leakcheck (API)
            try:
                a = leakcheck_net.leak_check_api(mail=email)
            except Exception:
                a = None
            if a:
                chars = "abcdefghijklmnopqrstuvwxyz1234567890"
                number_pass = ''.join(random.choice(chars) for _ in range(6))
                tree.create_node("Leaked Creditentials",number_pass,parent=number)
                for leak in a:
                    try:
                        password  = leak.get('password')
                        leak_name = leak.get('leak_name')
                        leak_date = leak.get('leak_date')
                        tree.create_node('Password  : {}'.format(password),parent=number_pass)
                        tree.create_node('Leak Name : {}'.format(leak_name),parent=number_pass)
                        tree.create_node('Leak Date : {}'.format(leak_date),parent=number_pass)
                    except Exception:
                        pass

        data_export['Emails']['HighProbEmails'] = no_doubles

    # pinterest-derived emails (very high prob)
    if pin2mail:
        tree.create_node('[+++] Very high probability',45451451545545155154,parent=146)
        for i in (pin2mail or []):
            tree.create_node('-> '+Fore.RED+i+Fore.RESET+" (Scraped from pinterest profile)",parent=45451451545545155154)

    # permutated mailbox guesses
    if possible_mail and len(possible_mail) != 0:
        tree.create_node("("+str(len(possible_mail))+") Possible Mailbox",8,parent=146)
        data_export['Emails']['PermutatedMailbox'] = possible_mail
        for i in possible_mail:
            tree.create_node(i,parent=8)

print("✅ Ready to be consulted !")
print('\n')

# For data Analyzation
data_export['UI']['Pie']['PersonnalLife']   = len(personnal_life)
data_export['UI']['Pie']['SocialMedias']    = len(social_medias)
data_export['UI']['Bar']['TwitterFounds']   = len(twitter_results or [])
data_export['UI']['Bar']['InstagramFounds'] = len(instagram_results or [])
data_export['UI']['Bar']['FacebookFounds']  = len(facebook_results or [])
data_export['UI']['Bar']['SkypeFounds']     = len(skype_results or [])

if json_print in ("true", "yes", "oui"):
    print('-- JSON START --')
    print(json.dumps(data_export, ensure_ascii=False, indent=2))
    print('-- JSON END --')
else:
    try:
        tree.show()
    except Exception:
        # fallback to basic print if tree.show fails
        print(json.dumps(data_export, ensure_ascii=False, indent=2))

# Save report
out_path = f'Reports/{folder_name}/{name}_{pren}.json'
try:
    with open(out_path,'w',encoding='utf8') as f:
        json.dump(data_export,f,indent=4,ensure_ascii=False)
except FileNotFoundError:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path,'w',encoding='utf8') as f:
        json.dump(data_export,f,indent=4,ensure_ascii=False)
