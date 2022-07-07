#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, os, os.path, subprocess

from pyrsistent import s
import commentfetch as cf

parser = argparse.ArgumentParser(description="Checks if there are any outdated packages")
parser.add_argument('output_file', help="Output file that shows which packages are outdated.")
parser.add_argument('-t', '--tmpfolder', default="/tmp/packages", help="Specify in which folder pkgbuilds will be cloned into. (default: /tmp/packages)")
parser.add_argument('-r', '--repo', default="Reborn-OS", type=str, help="Specify the repo that you want to check for updates. (Default Reborn-OS)")
parser.add_argument('-a', '--addpackages',type=str, help='Build, fetch and add packages to repo from AUR.')
parser.add_argument('-R', '--removepackages',type=str, help='Remove packages from repo.')
parser.add_argument('-u', '--updaterepo', action='store_true', help='specify whether to update repo.' )
parser.add_argument('-f', '--repofolder', help='Specify where the repo folder is. (Example /home/foo/foorepo/x86_64/)')
parser.add_argument('-e', '--extension',default='.db.tar.xz', help='Specify what the repos db file extention is. (Default .db.tar.xz')
parser.add_argument('-b', '--builtfolder',default='/tmp/packages/built',help='Folder where built tarballs are put (Default /tmp/packages/built')
parser.add_argument('-g', '--checkgit',action='store_true', help='specify whether to check for git updates.')
args = parser.parse_args()

scriptpath = os.getcwd()
yay = "/usr/bin/yay -Si aur/"
pacman = "/usr/bin/pacman -Si " + args.repo + "/"
stripver = " | grep Version | sed 's/^.*: //'"
cmpver = "/usr/bin/vercmp"
packagesupdated = []
def compareaur(outputfile, repo, tmpfolder, builtfolder):
    if os.path.exists(outputfile):
        os.remove(outputfile)
    print("Updating package databases!")
    subprocess.run("sudo pacman -Sy --noconfirm", shell=True)
    print("Checking for outdated packages!")
    packageslist = subprocess.check_output("pacman -Slq " + repo, shell=True).strip().decode('utf8').split('\n') # Get list of packages
    newer = ''
    older = ''
    for package in packageslist:
        package = package.strip()
        packagefolder=tmpfolder + "/" + package
        aurver = checkaur(package,repo)
        if aurver == "":
            continue
        # Check if it exists on aur
        # If it doesn't it will return an empty value
        repover = checkrepo(package)
        try:
            compare = subprocess.check_output(cmpver + " " + aurver + " " + repover, shell=True).decode().strip() # Compare aur and repo
            # Compare package version numbers using pacman's version comparison logic.
            # Output values:
            #  < 0 : if aur < repo
            #    0 : if aur == repo
            #  > 0 : if aur > repo
            # Printing package details
            print(package)
            print("aur: " + aurver + "\n" + "repo: " + repover + "\n")
            print(compare)
            if int(compare) == int(0):
                print("Package is the same version!")
            elif int(compare) > int(0):
                print("Package outdated!")
                # Write to list if the package is outdated
                older = older + package + " is outdated in repo aur: " + aurver + " repo: " + repover + "\n"
                if args.updaterepo:
                    answer = input("Do you want to build the package (y/n): ").lower() 
                    if answer == "yes" or answer == "y":
                        packagesupdated.append(package)
                        cf.main(package,"0",int("5"),"false")
                        print("\n\n\u001b[34mPlease read the comments to see if there are issues with the package!!!")
                        input("\u001b[34mWhen you've read them please Enter to continue...\u001b[0m\n")
                        fetchpackage(package, packagefolder) # Fetch the package from AUR
                        buildpackage(package, packagefolder, builtfolder) # Build the package 
                    elif answer == "no" or answer == "n": 
                        continue 
                    else: 
                        print("Please enter yes/y or no/n.")
            elif int(compare) < int(0):
                print("Package is newer on repo?")
                # Write to list if the package is newer or it doesnt exist
                newer = newer + package + " is newer in repo aur: " + aurver + " repo: " + repover + "\n"
            else:
                return
            print("EOF" + "\n" + "\n")
        except:
            print(package)
            print("aur: " + aurver)
            print("repo: " + repover)
            print("\u001b[41;1mAn error occured! Please go yell at Panda!\u001b[0m")
    print("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )
    with open(outputfile, "w") as out:
        os.system("touch " + outputfile)
        out.write("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )

def checkgitpackages(outputfile, repo, tmpfolder):
    if os.path.exists(outputfile):
        os.remove(outputfile)
    packageslist = subprocess.check_output("pacman -Slq " + repo, shell=True).strip().decode('utf8').split('\n')
    packageslist = [x for x in packageslist if '-git' in x] 
    for package in packageslist:
        package=package.strip()
        print("Package: " + package)
        repover = checkrepo(package)
        packagefolder = tmpfolder + "/" + package
        fetchpackage(package, packagefolder) # Fetch the package from AUR
        os.chdir(packagefolder) # Change to package folder
        subprocess.run("makepkg --nodeps --nobuild", shell=True)
        different = ''
        try:
            pkgrel = subprocess.check_output("source "+ "\"" + packagefolder + "/PKGBUILD" + "\""+ " && echo $pkgrel", shell=True).decode().strip()
            gitver = subprocess.check_output("source "+ "\"" + packagefolder + "/PKGBUILD" + "\""+ " && srcdir="+ "\"" + packagefolder + "/" +"\"" + " pkgver", shell=True).decode().strip() # Get pkgver
            ver=  str(gitver) + "-" + str(pkgrel)
        except:
            print("Package " + package + " is not a git package")
            print("Checking AUR for package")
            ver = checkaur(package, repo) # Get pkgver from AUR
        print(package)
        print("aur: " + ver)
        print("repo: " + repover)
        if repover != ver:
            print("Package may be outdated!")
            with open(outputfile, "w") as out:
                os.system("touch " + outputfile)
                different = different + package + " is outdated in repo aur: " + ver + " repo: " + repover + "\n"
                out.write(package + " is different in repo aur: " + repover + " repo: " + ver + "\n")
            if args.updaterepo:
                answer = input("Do you want to build the package (y/n): ").lower() 
                if answer == "yes" or answer == "y":
                    packagesupdated.append(package)
                    cf.main(package,"0",int("5"),"false")
                    print("\n\n\u001b[34mPlease read the comments to see if there are issues with the package!!!")
                    input("\u001b[34mWhen you've read them please Enter to continue...\u001b[0m\n")
                    fetchpackage(package, packagefolder)
                    buildpackage(package, packagefolder, )
                elif answer == "no" or answer == "n":
                    continue
            print("different" + different)
       
def checkaur(package,repo):
    aurver = str(subprocess.check_output(yay + package + stripver, shell=True).decode().strip()) # Get pkgver from AUR
    if repo == "Reborn-OS":
        aurver = aurver.split(":")[-1]       
    return aurver    

def checkrepo(package):
    repover = str(subprocess.check_output(pacman + package + stripver, shell=True).decode().strip()) # Get pkgver from repo
    return repover

def buildpackage(package, folder, builtfolder):
    print("Running editor on " + folder + "/PKGBUILD")
    subprocess.run("nano --rcfile=/usr/share/nano-syntax-highlighting/pkgbuild.nanorc " + folder + "/PKGBUILD", shell=True) # Review PKGBUILD with nano
    os.chdir(folder)
    print("Building package " + package)
    subprocess.run("makepkg --rmdeps --syncdeps --cleanbuild --clean PKGDEST=" + "\"" + builtfolder + "\"" , shell=True) # Build the package
    print("\n")

def fetchpackage(package,folder):
    print("Fetching package " + package)
    subprocess.run("git clone " + "https://aur.archlinux.org/" + package + ".git " + folder, shell=True) # Clone the package from AUR
    print("\n")

def addpackage(pkgsadd, builtfolder,tmpfolder):
    pkgsadd=pkgsadd.split(",")
    for package in pkgsadd:
        packagefolder = tmpfolder + "/" + package
        print("Package: " + package)
        packagesupdated.append(package)
        cf.main(package,"0",int("5"),"false")
        print("\n\n\u001b[34mPlease read the comments to see if there are issues with the package!!!")
        input("\u001b[34mWhen you've read them please Enter to continue...\u001b[0m\n")
        fetchpackage(package, packagefolder)
        buildpackage(package, packagefolder, builtfolder)

def pushpkgbuild(package, folder):
    print("Pushing package " + package)
    os.chdir(folder)
    subprocess.run("git add PKGBUILD", shell=True)
    subprocess.run("git commit -m \"Update PKGBUILD\"", shell=True)
    subprocess.run("git push", shell=True)
    print("\n")

def repoadd(updpkg,repofolder,extension,repo,buildfolder):
    if extension == '.db.tar.xz':
        files= '.files.tar.xz'
    elif extension == '.db.tar.gz':
        files= '.files.tar.gz'
    print("Updating repo!")
    print("Changing folder to: " + repofolder)
    os.chdir(repofolder)
    print("Updated packages: " + updpkg)
    print("Adding updated packages.")
    subprocess.run("repo-add " + repofolder + "/" + repo + extension + " " + buildfolder + "/" + "*.pkg.tar.zst", shell=True)
    print("Copying tarballs.")
    subprocess.run("cp -v " + buildfolder + "/*.pkg.tar.zst* " + repofolder, shell=True)
    print("\n")

def reporemove(updpkg,repofolder,extension,repo):
    if extension == '.db.tar.xz':
        files= '.files.tar.xz'
    elif extension == '.db.tar.gz':
        files= '.files.tar.gz'
    print("Removing packages from repo!")
    print("Changing folder to: " + repofolder)
    os.chdir(repofolder)
    print("Packages to be removed: " + ' '.join(updpkg))
    subprocess.run("repo-remove "+ repofolder + "/" + repo + extension + " " + ' '.join(updpkg), shell=True)
    subprocess.run("rm " + repo + ".db " + repo +".files", shell=True)
    subprocess.run("cp -v  "+ repo + extension + " " + repo +".db", shell=True)
    subprocess.run("cp -v  "+ repo + files + " " + repo +".files", shell=True)
    print("Removing tarballs.")
    for package in updpkg:
        subprocess.run("rm -vi " + repofolder + "/" + package + "*.pkg.tar.zst*", shell=True)

def main():
    if args.removepackages:
        args.removepackages = args.removepackages.split(",")
        reporemove(args.removepackages, args.repofolder, args.extension, args.repo)
    elif args.addpackages:
        addpackage(args.addpackages, args.builtfolder,args.tmpfolder)
        repoadd(args.addpackages, args.repofolder, args.extension, args.repo, args.builtfolder)
    else:
        if args.checkgit:
            checkgitpackages(args.output_file, args.repo, args.tmpfolder)
        else:
            compareaur(args.output_file, args.repo, args.tmpfolder, args.builtfolder)
        if args.updaterepo:
            print("Updating repo!")
            reporemove(packagesupdated, args.repofolder, args.extension, args.repo)
            repoadd(packagesupdated, args.repofolder, args.extension, args.repo, args.builtfolder)
            print("Repo updated!")
            print("\n")

if __name__ == '__main__':
    main()
