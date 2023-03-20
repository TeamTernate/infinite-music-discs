#!/bin/bash
#Linux build script by GEROGIANNIS and lefterisgar

COL_NC='\e[0m' # No Color
COL_LIGHT_RED='\e[1;31m'
COL_LIGHT_GREEN='\e[1;32m'
COL_LIGHT_BLUE='\e[1;94m'
COL_LIGHT_YELLOW='\e[1;93m'
TICK="${COL_NC}[${COL_LIGHT_GREEN}✓${COL_NC}]"
CROSS="${COL_NC}[${COL_LIGHT_RED}✗${COL_NC}]"
INFO="${COL_NC}[${COL_LIGHT_YELLOW}i${COL_NC}]"
QUESTION="${COL_NC}[${COL_LIGHT_BLUE}?${COL_NC}]"

#Include ascii file
. build/ascii

#Print ASCII logo and branding
printf "$IMD_GUI_LOGO"
printf "$IMD_GUI_BRANDING"
printf "$IMD_GUI_DESCRIPTION"

requestSudo() {
    #Request sudo privileges
    if [[ $(/usr/bin/id -u) -ne 0 ]]; then
        printf "The script is not running as root.\n"
        printf "Requesting sudo privileges..."
        printf "\n"
    fi
}

#Install dev dependencies
if ! [ -f .environment_setup_complete ]; then
    printf "%b %bSetting up build environment...%b\\n" "${INFO}"
    printf "%b %bChecking Python version...%b\\n" "${INFO}"

    #Check if python3 is installed
    if hash python3 2>/dev/null; then
        printf "%b %b$(python3 -V)%b\\n" "${TICK}" "${COL_LIGHT_GREEN}" "${COL_NC}"
    else
        printf "%b %bPython 3 is not installed (could not find python3)!%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"
        exit 22
    fi

    printf "%b %bChecking pip version...%b\\n" "${INFO}"

    #Check if pip3 is installed
    if ! hash pip3 2>/dev/null; then
        printf "%b %bpip3 is not installed!%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"

        #Ask the user if he wants to install it
        printf "%b %bDo you want to install it? (y/n) %b" "${QUESTION}"
        read -n 1 -r
        printf "\n"

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            printf "%b %bInstalling pip...%b\\n" "${INFO}"

            #Check Linux distribution
            . /etc/os-release

            if [ $ID_LIKE == 'debian' ] || [ $ID_LIKE == 'ubuntu' ] || [ $ID == 'debian' ]; then
                #Request sudo privileges
                requestSudo
                #Install pip using APT
                sudo apt-get install -y python3-pip > /dev/null
            elif [ $ID == 'fedora' ] || [ $ID_LIKE == 'rhel fedora' ]; then
                #Request sudo privileges
                requestSudo
                #Install pip using DNF
                sudo dnf install -y python3-pip > /dev/null
            elif [ $ID_LIKE == 'arch' ] || [ $ID_LIKE == 'archlinux' ]; then
                #Request sudo privileges
                requestSudo
                #Install pip using pacman
                sudo pacman -S --noconfirm python-pip > /dev/null
            else
                #Distro-agnostic way to install pip
                #Official documentation: https://pip.pypa.io/en/stable/installation/
                printf "%b %bYour distribution is not supported!%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"
                printf "%b %bInstalling pip via alternative method...%b\\n" "${INFO}"

                #Download get-pip.py only if it doesn't exist
                if ! [ -f tmp/get-pip.py ]; then
                    wget -q --show-progress -P tmp/ https://bootstrap.pypa.io/get-pip.py
                fi

                #Install pip using the official script
                python3 tmp/get-pip.py
            fi

            #Verify that pip has been installed
            if hash pip3 2>/dev/null; then
                printf "%b %bDone!%b\\n" "${INFO}"
            else
                printf "%b %bFailed to install pip.%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"
                exit 22;
            fi
        else
            printf "%b %bOperation cancelled by the user. Aborting.%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"
            exit 125;
        fi
    fi

    #Print pip version
    printf "%b %bpip $(pip3 -V | awk '{print $2;}')%b\\n" "${TICK}" "${COL_LIGHT_GREEN}" "${COL_NC}"

    #Install dev dependencies
    printf "%b %bInstalling dependencies...%b\\n" "${INFO}"
    pip3 install -r requirements.rc > /dev/null

    #Check if pyinstaller is installed
    if ! hash pyinstaller 2>/dev/null; then
        printf "%b %bRestart your computer for the changes to be applied.!%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"
        exit 22
    fi

    #Create an empty file so that environment setup does not happen again
    touch .environment_setup_complete

    printf "%b %bDone installing dependencies!%b\\n" "${TICK}" "${COL_LIGHT_GREEN}" "${COL_NC}"
fi

printf "%b %bBuilding package...%b\\n" "${INFO}" "${COL_LIGHT_YELLOW}"

#Build the package, using the official instructions
#Log pyinstaller output to both console and a logfile with tee
python3 ./build/build.py 2>&1 | tee build/latest.log

#Determine if build has succeeded or failed
if tail -1 build/latest.log | grep successfully >/dev/null; then
    printf "%b %bBuild succeeded!%b\\n" "${TICK}" "${COL_LIGHT_GREEN}" "${COL_NC}"
else
    printf "%b %bBuild failed!%b\\n" "${CROSS}" "${COL_LIGHT_RED}" "${COL_NC}"

    #Silently remove .environment_setup_complete to force dependency checks next time, in case of failure
    #Does not occur when it has been aborted by the user
    if ! tail -1 latest.log | grep user >/dev/null; then
        rm .environment_setup_complete
    fi
fi
