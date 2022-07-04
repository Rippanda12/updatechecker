# Repo update checker
pacman/archlinux repo update checker
# Prerequisites:
```
sudo pacman -Sy python python-{pip,click,requests,lxml,html2text}
yay -S python3-aur
pip install argsparse
```
# How to use:
```
git clone https://github.com/Rippanda12/updatechecker.git
cd updatechecker
python packages.py ./out.txt
```
