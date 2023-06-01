#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 02:45:38 2023

@author: KoreMoDz
"""

import os
import imaplib
import email
import re
import time
from email.header import decode_header
from colorama import Fore, init
from bs4 import BeautifulSoup
from datetime import datetime

init()

# Read credentials from a txt file
with open("credentials.txt", "r") as f:
    lines = f.readlines()

account_list = [re.findall(r"[^@]+@[^@]+\.[^@]+:[^\s]+", line.strip())[0] for line in lines if re.findall(r"[^@]+@[^@]+\.[^@]+:[^\s]+", line.strip())]

output_file = "output.txt"
file_exists = os.path.exists(output_file)

current_time = time.strftime("%x at %X")
new_email_accounts = [] 
no_new_email_accounts = []  

def generate_imap_server(email_address):
    domain = email_address.split("@")[1]
    return f"mail.{domain}"

def decode_email(email_data):
    # List of common encodings to try
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'utf-16', 'windows-1252']
    raw_email = None

    # Try decoding the email using each encoding in the list
    for encoding in encodings:
        try:
            raw_email = email_data.decode(encoding)
            return raw_email
        except UnicodeDecodeError:
            pass
    return None

def check_mailbox(account, password):
    server_imap = generate_imap_server(account)
    try:
        mail = imaplib.IMAP4_SSL(server_imap)
        mail.login(account, password)
    except imaplib.IMAP4.error as e:
        print(Fore.RED + f"Error logging in to account: {account}. Error: {str(e)}")
        return
    print(Fore.GREEN + f"Connection successful to account: {account} (IMAP Server: {server_imap})")

    mail.select("inbox")

    result, data = mail.uid("search", None, "(UNSEEN)")
    if result == "OK":
        has_new_email = False
        for num in data[0].split():
            result, email_data = mail.uid("fetch", num, "(BODY[])")
            if result == "OK":
                raw_email = email_data[0][1].decode("utf-8")
                email_message = email.message_from_string(raw_email)

                # Extract the email subject
                subject = decode_header(email_message["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                # Extract the email content
                email_content = ""
                if email_message.is_multipart():
                    for part in email_message.get_payload():
                        if part.get_content_type() == "text/html":
                            email_content += part.get_payload(decode=True).decode()
                else:
                    email_content = email_message.get_payload(decode=True)

                # Search for the verification code in the email content
                verification_code = None
                link = None
                if email_content:
                    soup = BeautifulSoup(email_content, 'html.parser')

                    # Search for the verification code in the email content
                    code_tag = soup.find('p', class_='rc-2fa-code rc-2fa-code-override')
                    if code_tag:
                        verification_code = code_tag.get_text().strip()

                    # Search for the link in the email content
                    link_tag = soup.find('a', href=True)
                    if link_tag:
                        link = link_tag['href']
                        # Decode the link if it is a Rockstar link
                        if 'rockstargames' in link:
                            link = urllib.parse.unquote(link)

                if verification_code or link:
                    print(Fore.GREEN + f"Account: {account} has a new email. Subject: {subject}. Verification code: {verification_code}, Link: {link}")
                    has_new_email = True
                    new_email_accounts.append((account, password, subject, verification_code, link))  #Save the account, verification code, and link in the list of new emails
                else:
                    print(Fore.YELLOW + f"Account: {account} has a new email but no verification code or link was found. Subject: {subject}")

        if not has_new_email:
            no_new_email_accounts.append((account, password))  #Save the account in the list of accounts without new emails
    else:
        no_new_email_accounts.append((account, password))  #Save the account in the list of accounts without new emails

    mail.logout()

    # Sort the list of new emails based on the send date (from most recent to least recent)
    new_email_accounts.sort(key=lambda x: x[2], reverse=True)


for account_password in account_list:
    account, password = account_password.split(":")
    try:
        check_mailbox(account, password)
    except Exception as e:
        print(Fore.RED + f"Error checking account: {account}. Error: {str(e)}")

#Write all results to the output file, first grouping accounts with new emails
with open(output_file, "a") as f:
    if not file_exists:
        f.write("-----------\n")
    f.write(f"Run on {current_time}\n\n")
    for account, password, subject, verification_code, link in new_email_accounts:
        f.write(f"Account: {account}:{password} | New email: {subject} | Verification code: {verification_code} | Link: {link}\n")
    f.write("\n")
    for account, password in no_new_email_accounts:
        f.write(f"Account: {account}:{password} | No new email\n")
    f.write("-----------\n")

    except Exception as e:
        print(f"Error checking account: {account}. Error: {str(e)}")
