#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''AWS KMS Key Rotation Script.
    Author: dad2jrn
    License: MIT

This python script will attempt to rotate KMS keys by creating a second (new) key, make
inactive (disable) the previouskey, and then delete the inactive key; if the necessary
argumements are passed.

Example:

    Help::
        $ python kms-key.py -h --help
    Create New Key::
        $ python kms-key.py -u [iam user]
    Disable Previous Key::
        $ python kms-key.py -k [access key] [--disable]
    Delete Previous Key::
        $ python kms-key.py -k [access key] [--delete]

Todo:
    * Allow for input file containing list of keys

'''

import argparse
import sys

import boto3
from botocore.exceptions import ClientError

script = sys.argv[0]
iam_client = boto3.client('iam')
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help=f'IAM username, e.g. {script} --username <username>')
parser.add_argument('-k', '--key', help=f'AWS access key, e.g. {script} --key <access_key>')
parser.add_argument('--disable', help=f'Disables the access key', action='store_true')
parser.add_argument('--delete', help=f'Deletes the access key', action='store_true')
args = parser.parse_args()
username = args.username
aws_access_key = args.key

def create_key(username):
    '''Create new KMS Key.

    Args:
        username: IAM username.

    Prints:
        The the Access Key and Secret Key to screen.

    '''

    if inactive_count + active_count >= 2:
        print(f'\n{username} already has 2 keys. You must first delete one of the keys before you can create another.')
        exit()
    access_key_metadata = iam_client.create_access_key(UserName=username)['AccessKey']
    access_key = access_key_metadata['AccessKeyId']
    secret_key = access_key_metadata['SecretAccessKey']
    print(f'Your new ACCESS key is {access_key}\n')
    print(f'Your new SECRET key is {secret_key}')
    access_key = ''
    secret_key = ''

def disable_key(access_key, username):
    '''Disables current active KMS Key.

    Args:
        access_key: Access key to be disabled.
        username: IAM username.

    Prints:
        Alerts user if key provided not found, else prints the the Access Key and Secret Key to screen.

    '''

    i = ''
    try:
        while i != 'Y' or 'N':
            i = input(f'Do you want to disable the access key {access_key} [Y/N]?')
            i = str.capitalize(i) # Ensure the response is always capitalized
            if i == 'Y':
                iam_client.update_access_key(UserName=username, AccessKeyId=access_key, Status="Inactive")
                print(f'{access_key} has been disabled.')
                exit()
            elif i == 'N':
                exit()

    except ClientError as e: # Error handling
        print(f'The access key of {access_key} cannot be found')

def delete_key(access_key, username):
    '''Prompts user for confirmation, then deletes current disabled KMS Key.

    Args:
        access_key: Access key to be disabled.
        username: An IAM username.

    Prints:
        Alerts user if key provided not found, else informs user the key has successfully been deleted.

    '''

    i = ''
    try:
        while i != 'Y' or 'N':
            i = input(f'Do you want to delete the access key {access_key} [Y/N]?')
            i = str.capitalize(i) # Ensure the response is always capitalized
            if i == 'Y':
                iam_client.delete_access_key(UserName=username, AccessKeyId=access_key)
                print(f'{access_key} has been deleted.')
                exit()
            elif i == 'N':
                exit()

    except ClientError as e: # Error handling
        print(f'The access key of {access_key} cannot be found')

def confirm(prompt=None, resp=True):
    '''Prompts for yes or no response from the user. Returns True for yes and
    False for no.

     Arg 'resp' should be set to the default value assumed when user simply hits [ENTER].

    confirm(prompt='Create Directory?', resp=True)
        Create Directory? [y]|n:
        >>> = True

    confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y:
        >>> = False

    confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y: y
        >>> = True

    Args:
        prompt: A string printed to the user.
        resp: Default value assumed if user hits [Enter].

    Returns:
        True or False.
    '''

    if prompt is None:
        prompt = f'\nOkay, Hold up!!! \nHave you already downloaded your Security Tokens?'
    if resp:
        prompt = f'{prompt} [y]|n: '
    else:
        prompt = f'{prompt} [n]|y: '
    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print(f'Please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return exit()

try:
    confirm() # Prompt for security tokens first.

    keys = iam_client.list_access_keys(UserName=username)
    inactive_count = 0
    active_count = 0

    # Count the umber of keys
    for key in keys['AccessKeyMetadata']:
        if key['Status']=='Inactive': inactive_count = inactive_count + 1
        elif key['Status']=='Active': active_count = active_count + 1
    print(f"{username} has {inactive_count} inactive keys and {active_count} active keys")
    # if user passes args in addition to username then execute function
    if args.disable:
        disable_key(aws_access_key, username) # Runs disable function if arg passed
    elif args.delete:
        delete_key(aws_access_key, username) # Runs delete function if arg passed
    else:
        create_key(username) # Default action of script

except ClientError as e: # Error handling
    print(f"The user with the name {username} cannot be found.")
