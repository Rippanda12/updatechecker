# Repo update checker
pacman/archlinux repo update checker
# Prerequisites:
```
sudo pacman -Sy python python-{pip,click,requests,lxml,html2text} nano nano--syntax-highlighting nano
yay -S python3-aur
pip install argsparse
```
# How to use:
```
git clone https://github.com/Rippanda12/updatechecker.git
cd updatechecker
python packages.py /home/foo/out.txt -r bred -e .db.tar.xz -u True -f '/home/foo/Projeckts/bred-repo/' 
```
```
usage: packages.py [-h] [-t TMPFOLDER] [-r REPO] [-p PACKAGES] [-u UPDATEREPO] [-f REPOFOLDER] [-e EXTENSION] [-b BUILTFOLDER] output_file

Checks if there are any outdated packages

positional arguments:
  output_file           Output file that shows which packages are outdated.

options:
  -h, --help            show this help message and exit
  -t TMPFOLDER, --tmpfolder TMPFOLDER
                        Specify in which folder pkgbuilds will be cloned into
  -r REPO, --repo REPO  Specify the repo that you want to check for updates (Default Reborn-OS)
  -p PACKAGES, --packages PACKAGES
  -u UPDATEREPO, --updaterepo UPDATEREPO
                        specify whether to update repo(True or False)
  -f REPOFOLDER, --repofolder REPOFOLDER
                        Specify where the repo folder is (Example /home/foo/foorepo/x86_64/)
  -e EXTENSION, --extension EXTENSION
                        Specify what the repos db file extention is (Default .db.tar.xz
  -b BUILTFOLDER, --builtfolder BUILTFOLDER
                        Folder where built tarballs are put (Default /tmp/packages/built)
```
