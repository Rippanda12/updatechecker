import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description="Checks if there are any outdated packages")
parser.add_argument('output_file', help="Output file that shows which packages are outdated.")

parser.add_argument('-r', '--repo', default="Reborn-OS", type=str, help="Specify the repo that you want to check for updates (Default Reborn-OS)")
parser.add_argument('-p', '--packages', default=0, help='')

args = parser.parse_args()

yay = "/usr/bin/yay -Si aur/"
pacman = "/usr/bin/pacman -Si " + args.repo + "/"
stripver = " | grep Version | sed 's/^.*: //'"
cmpver = "/usr/bin/vercmp"
def compareaur(outputfile, repo):
#    subprocess.check_output("rm " + outputfile, shell=True)
#    subprocess.check_output("pacman -Syy --noconfirm", shell=True)
    packageslist = subprocess.check_output("pacman -Slq " + repo, shell=True).strip().decode('utf8').split('\n')
    newer = ''
    older = ''
    for package in packageslist:
        package = package.strip()
        pacmanver = str(subprocess.check_output(pacman + package + stripver, shell=True).decode().strip())
        aurver = str(subprocess.check_output(yay + package + stripver, shell=True).decode().strip().split(":")[-1])
        # Check if it exists on aur
        # If it doesn't it will return an empty value
        if aurver == "":
            continue
        else:
            pass
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
            print("\u001b[41;1m" + "An error occured!" + "\u001b[0m")
    return
    with open(outputfile, "w") as out:
        os.system("touch " + outputfile)
        out.write("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )
    print("older packages are:"+ "\n" + older + "\n\n" + "newer packages are:"+ "\n" + newer )


compareaur(args.output_file, args.repo)

