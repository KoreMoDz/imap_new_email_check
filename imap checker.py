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

# Read credentials from a txt file. Each line should be in the format "email:password".
# The file should be located in the same directory as the script.
with open("credentials.txt", "r") as f:
    lines = f.readlines()

# Extract the email and password from each line in credentials.txt
account_list = [re.findall(r"[^@]+@[^@]+\.[^@]+:[^\s]+", line.strip())[0] for line in lines if re.findall(r"[^@]+@[^@]+\.[^@]+:[^\s]+", line.strip())]

# This is the file where the results will be written.
output_file = "output.txt"

# Check if the output file exists
file_exists = os.path.exists(output_file)

# Write the current run timestamp
current_time = time.strftime("%x at %X")
with open(output_file, "a") as f:
    if not file_exists:
        f.write("-----------\n")
    f.write(f"Run of {current_time}\n\n")

def generate_imap_server(email_address):
    domain = email_address.split("@")[1]
    return f"mail.{domain}"

def check_inbox(account, password):
    imap_server = generate_imap_server(account)
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(account, password)
    except imaplib.IMAP4.error as e:
        # If there's an error during login, print it and return from the function.
        print(f"Error logging in to account: {account}. Error: {str(e)}")
        return
    print(f"Successfully connected to account: {account} (IMAP Server: {imap_server})")

    mail.select("inbox")

    result, data = mail.uid("search", None, "(UNSEEN)")
    if result == "OK":
        has_new_email = False  # Added: variable to track new emails
        # Iterate over each email.
        for num in data[0].split():
            result, email_data = mail.uid("fetch", num, "(BODY[HEADER])")
            if result == "OK":
                raw_email = email_data[0][1].decode("utf-8")
                email_message = email.message_from_string(raw_email)
                subject = decode_header(email_message["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # If the subject is in base64/quoted-printable encoding, decode it.
                    subject = subject.decode()
                print(f"Account: {account} has a new email. Subject: {subject}")
                has_new_email = True  # Added: indicate the presence of new emails
                # Write the results to the output file only if there are new emails.
                with open(output_file, "a") as f:
                    f.write(f"Account: {account}:{password} | New email: {subject}\n")
        if not has_new_email:
            # Write to the output file if there are no new emails.
            with open(output_file, "a") as f:
                f.write(f"Account: {account}:{password} | No new emails\n")
    else:
        print(f"No new emails for account: {account}")
        has_new_email = False  # Added: indicate the absence of new emails
        # Write to the output file if there are no new emails.
        with open(output_file, "a") as f:
            f.write(f"Account: {account}:{password} | No new emails\n")

    mail.logout()

# Iterate over all the accounts in the list.
for account_password in account_list:
    account, password = account_password.split(":")
    try:
        check_inbox(account, password)
    except Exception as e:
        print(f"Error checking account: {account}. Error: {str(e)}")
