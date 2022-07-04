import argparse
import subprocess
import os
import os.path
import commentfetch as cf

parser = argparse.ArgumentParser(description="Checks if there are any outdated packages")
parser.add_argument('output_file', help="Output file that shows which packages are outdated.")
parser.add_argument('-t', '--tmpfolder', default="/tmp/packages", help="Specify in which folder pkgbuilds will be cloned into")
parser.add_argument('-r', '--repo', default="bred", type=str, help="Specify the repo that you want to check for updates (Default Reborn-OS)")
parser.add_argument('-p', '--packages', default=0, help='')
parser.add_argument('-u', '--updaterepo', default=False, help='specify whether to update repo(True or False)')
parser.add_argument('-f', '--repofolder', help='Specify where the repo folder is (Example /home/foo/foorepo/x86_64/)')
parser.add_argument('-e', '--extension',default='.db.tar.xz', help='Specify what the repos db file extention is (Default .db.tar.xz')
parser.add_argument('-b', '--builtfolder',default='/tmp/packages/built',help='Folder where built tarballs are put (Default /tmp/packages/built')
parser.add_argument('--checkonly', default=True, help="")
args = parser.parse_args()

scriptpath = os.getcwd()
yay = "/usr/bin/yay -Si aur/"
pacman = "/usr/bin/pacman -Si " + args.repo + "/"
stripver = " | grep Version | sed 's/^.*: //'"
cmpver = "/usr/bin/vercmp"
packagesupdated = []
def compareaur(outputfile, repo, tmpfolder):
    os.system("touch " + outputfile)
    if os.path.exists(outputfile) == True:
        subprocess.run("rm " + outputfile, shell=True)
        os.system("touch " + outputfile)
    else:
        return
    subprocess.run("sudo pacman -Sy --noconfirm", shell=True)
    packageslist = subprocess.check_output("pacman -Slq " + repo, shell=True).strip().decode('utf8').split('\n')
    newer = ''
    older = ''
    for package in packageslist:
        package = package.strip()
        packagefolder=tmpfolder + "/" + package
        aurver = str(subprocess.check_output(yay + package + stripver, shell=True).decode().strip().split(":")[-1])
        if aurver == "":
            continue
        else:
        # Check if it exists on aur
        # If it doesn't it will return an empty value
            pass
        pacmanver = str(subprocess.check_output(pacman + package + stripver, shell=True).decode().strip())
        try:
            compare = subprocess.check_output(cmpver + " " + aurver + " " + pacmanver, shell=True).decode().strip()
            # Compare package version numbers using pacman's version comparison logic.
            # Output values:
            #  < 0 : if aur < repo
            #    0 : if aur == repo
            #  > 0 : if aur > repo
            # Printing package details
            print(package)
            print("aur: " + aurver + "\n" + "repo: " + pacmanver + "\n")
            print(compare)
            if int(compare) == int(0):
                print("Package is the same version!")
            elif int(compare) > int(0):
                print("Package outdated!")
                # Write to list if the package is outdated
                older = older + package + " is outdated in repo aur: " + aurver + " repo: " + pacmanver + "\n"
                if args.checkonly.lower() == "false":
                    answer = input("Do you want to build the package (y/n): ").lower() 
                    if answer == "yes" or answer == "y":
                        packagesupdated.append(package)
                        cf.main(package,"0",int("5"),"false")
                        print("\n\n\u001b[34mPlease read the comments to see if there are issues with the package!!!")
                        input("\u001b[34mWhen you've read them please Enter to continue...\u001b[0m\n")
                        pullpackage(package, packagefolder)
                    elif answer == "no" or answer == "n": 
                        continue 
                    else: 
                        print("Please enter yes/y or no/n.")
                else:
                    print("something happened")
            elif int(compare) < int(0):
                print("Package is newer on repo?")
                # Write to list if the package is newer or it doesnt exist
                newer = newer + package + " is newer in repo aur: " + aurver + " repo: " + pacmanver + "\n"
            else:
                return
            print("EOF" + "\n" + "\n")
        except:
            print(package)
            print("aur: " + aurver)
            print("repo: " + pacmanver)
            print("\u001b[41;1m" + "An error occured! Please go yell at Panda!" + "\u001b[0m")
    print("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )
    with open(outputfile, "w") as out:
        os.system("touch " + outputfile)
        out.write("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )
    
    
def pullpackage(package, folder):
    subprocess.run("git clone " + "https://aur.archlinux.org/" + package + ".git " + folder, shell=True)
    os.chdir(folder)
    print("Running nano on " + folder + "/PKGBUILD")
    subprocess.run("nano --rcfile=/usr/share/nano-syntax-highlighting/pkgbuild.nanorc " + folder + "/PKGBUILD", shell=True)
    subprocess.run("makepkg --rmdeps --syncdeps --cleanbuild --clean PKGDEST=" + "\"" + args.builtfolder + "\"" , shell=True)
    print("\n")

def updaterepo(updpkg,repofolder,extension,repo,buildfolder):
    try:
        print("Updating repo!")
        print("Changing folder to: " + repofolder)
        os.chdir(repofolder)
        print("Removing old packages from repository.")
        print("Packages to be removed: " + ' '.join(updpkg))
        subprocess.run("repo-remove "+ repofolder + "/" + repo + extension + " " + ' '.join(updpkg), shell=True)
        print("Removing tarballs.")
        subprocess.run("rm -vi " + ' '.join(updpkg)+ '*.pkg.tar.zst*', shell=True)
        print("Adding updated packages.")
        subprocess.run("repo-add " + repofolder + "/" + repo + extension + " " + buildfolder + "/" + "*.pkg.tar.zst", shell=True)
        print("Copying tarballs.")
        subprocess.run("cp -v " + buildfolder + "/*.pkg.tar.zst* " + repofolder, shell=True)
    except:
        print("something happened")

compareaur(args.output_file, args.repo, args.tmpfolder)
if args.updaterepo == "True":
    updaterepo(packagesupdated, args.repofolder, args.extension, args.repo, args.builtfolder)
else:
    print("stuff")
#print("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )