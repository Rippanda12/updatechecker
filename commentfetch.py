#!/usr/bin/env python
#Forked from https://github.com/mortbauer/aur-comment-fetcher/
import AUR.RPC
import click
import requests
import textwrap
from bs4 import BeautifulSoup

BASE_URL = 'https://aur.archlinux.org/packages/'

class Comment(object):
    def __init__(self,author,timestamp,content,pinned):
        self.author = author
        self.timestamp = timestamp
        self.content = content
        self.pinned = pinned


def query(name):
    found = []
    for i,result in enumerate(AUR.RPC.aur_query('search',name)):
        # test if the exact name is under the found then we won't ask
        if name == result['Name']:
            return name
        found.append(result)
    if found:
        for i,x in enumerate(found):
            print('\033[33m\033[1m{0}\033[0m: \033[33m{1} \033[32m{2}'
                  .format(i,x['Name'],x['Version']))
            print('\t\033[0m{0}'.format(x['Description']))
        number = click.prompt('\nspecify the number of the package', type=int)
        return found[number]['Name']
    else:
        raise click.ClickException('couldn\'t find any package with name "{0}"'
                        .format(name))

def get(package):
    res = requests.get(BASE_URL+package+'/?comments=all',verify=True)
    if res.status_code != 200:
        res = requests.get(BASE_URL+query(package)+'/?comments=all',verify=True)
        if res.status_code != 200:
            raise click.ClickException('couldn\'t fetch comments for package "{0}"'
                            .format(package))
    return res

def fetch_comments(package,number=5):
    res = get(package)
    soup = BeautifulSoup(res.content, 'lxml')
    # find only next element 
    current = soup.find('div',attrs={'class':'comments'}) 
    results = []
    i = 0
    while i < number:
        head = current.find_next(attrs={'class':'comment-header'})
        if head is None: 
            break
        comment = current.find_next(attrs={'class':'article-content'})
        is_pinned = comment.attrs['id'].startswith('pinned')
        author = head.text.split('commented')[0].strip()
        timestamp = head.find('a').text
        results.append(Comment(author,timestamp,comment.text,is_pinned))
        current = comment
        i += 1
    return package,results

def main(package,get_all,number,reverse_order):
    package,comments = fetch_comments(package,number=number)
    if len(comments) == 0:
        print('\033[31m\nno comments available for package "{0}"\n full info at {1}\n\033[0m'
            .format(package,BASE_URL+package))
        return
    else:
        print('\033[35m\n{4} {1} comments for package "{0}"{3}:\n full info at {2}\n\033[0m'
            .format(package,len(comments),BASE_URL+package,' (most recent last)' if reverse_order else '','Last' if get_all else 'Last'))
    for comment in (reversed(comments) if reverse_order else comments):
        if comment.pinned and reverse_order:
            print()
        print('\033[33m{0}:{2} Comment\033[33m by {1}\033[0m'
            .format(comment.timestamp,comment.author,'\033[36m Pinned' if comment.pinned else ''))
        print(textwrap.fill(comment.content,initial_indent='  ',subsequent_indent='  '))
        if comment.pinned and not reverse_order:
            print()


if __name__ == '__main__':
    main()
