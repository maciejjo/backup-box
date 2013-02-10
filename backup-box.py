#! /usr/bin/python
# -*- coding: utf-8 -*-

from dropbox import client, rest, session
import os
import sys
import time

APP_KEY = 'quro1mvj5rp9cyw'
APP_SECRET = 'j4xljayripqrl8c'
UBX_DIRS = {
    'code':'/home/maciejjo/code',
    'docs':'/home/maciejjo/docs',
    'www':'/home/maciejjo/www'
    }
ACCESS_TYPE = 'app_folder'
LOGFILE = '/home/maciejjo/logs/backup-box.log'
TOKEN_FILE = '/home/maciejjo/.token.txt'

def print_to_logfile(line):
    logfile = open(LOGFILE, 'a')
    logfile.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ' ' + line + '\n')
    logfile.close()

print_to_logfile('Starting session...')
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
if not(os.path.exists(TOKEN_FILE)):
    print_to_logfile('ERROR! No token found! Run Manually.')
    exit(0)
    request_token = sess.obtain_request_token()
    url = sess.build_authorize_url(request_token)
    print "url:", url
    print "Wejdź i daj 'Allow' a tu enter."
    raw_input()
    access_token = sess.obtain_access_token(request_token)
    token_file = open(TOKEN_FILE,'w')
    token_file.write("%s|%s" % (access_token.key,access_token.secret))
    token_file.close()
else:
    print_to_logfile('Token found at ' + TOKEN_FILE)
    token_file = open(TOKEN_FILE)
    token_key, token_secret = token_file.read().split('|')
    token_file.close()
    sess.set_token(token_key, token_secret)

client = client.DropboxClient(sess)
client_info = client.account_info()
print_to_logfile("Account: " + client_info['display_name'] + ' (' + client_info['email'] + '|' + str(client_info['uid']) + ')')

for label, directory in UBX_DIRS.iteritems():
    cmd = 'tar czf current.tar.gz -C %s .' % directory
    print_to_logfile("Creating archive with '" + cmd + "'")
    os.system(cmd)
    remote_path='/'+label+'.tar.gz'
    try:
        client.file_delete(remote_path)
        print_to_logfile("Deleting " + remote_path + " from Dropbox!")
    except Exception:
        print_to_logfile("File " + remote_path + " doesnt exist")

    f = open('current.tar.gz')
    client.put_file(remote_path, f)
    print_to_logfile("Sending new " + remote_path + " to Dropbox")
    os.system('rm current.tar.gz')
    print_to_logfile("Deleting temporary file")

print_to_logfile("Ending sessison. Bye!")

