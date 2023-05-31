# imap_new_email_check
Email Checker is a Python script that allows you to monitor multiple email accounts for new messages. It uses the IMAP protocol to connect to the specified email server and checks the inbox for any unread emails. The script is designed to automate email management and provide notifications when new emails arrive.

## Features
- Supports multiple email accounts specified in a `credentials.txt` file.
- Connects to the specified email server via IMAP SSL.
- Retrieves unread email messages from the inbox.
- Decodes the email subjects if they are in base64 or quoted-printable encoding.
- Outputs the results to an `output.txt` file, including the account information and the subject of any new emails found.
- Handles login errors and retries for improved reliability.

## Usage
1. Create a text file named `credentials.txt` in the same directory as the script.
2. Each line in `credentials.txt` should contain an email address and password separated by a colon (e.g., `email@example.com:password`).
3. Make sure the email addresses are from the same email server specified in the script.
4. Run the script to check for new emails in each account.
5. The results will be written to the `output.txt` file, including the timestamp of each run and information about any new emails found.

Note: Ensure that the script has necessary permissions to read and write files in the directory.

Feel free to customize the script and adapt it to your specific needs.

