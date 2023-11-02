#!/bin/bash

# Metadata
CODE_GEN_VERSION=1.1.4

# Helper Functions
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

# Docker Python Version
function build_from_remote {
	$CODE_GEN $PROTOCOL://$API_KEY@$SERVICE_TEMPLATE --no-input --config-file $CONFIG_PATH -o ./output/$OUT_PATH -f
}

function build_from_local {
	$CODE_GEN $LOCAL_TEMPLATE --no-input --config-file $CONFIG_PATH -o ./output/$OUT_PATH -f
}

function clean_build {
	:
}

apt-get install dos2unix
dos2unix -n input/config.yaml input/config_lf.yaml

# Default parameters
CONFIG_PATH=input/config_lf.yaml
CODE_GEN=cookiecutter
GEN_MODE=readonly
SERVICE_VENV=false
OUT_PATH=.

# Build Config
BACKEND_COOKIECUTTER=$(cookiecutter --version)
BACKEND_PROTOC=$(protoc --version)
BACKEND_LINT=black

# Git Config
PROTOCOL=https
API_KEY=

# Remote Template
SERVICE_TEMPLATE=

# Local Template
LOCAL_TEMPLATE=.

# Logging
EC='\033[0;31m'
WC='\033[0;33m'
PC='\033[1;32m'
IC='\033[0;34m'
BC='\033[1m'
NC='\033[0m'

# Optional command line argument parsing
echo -e "${IC}INFO${NC}: DOTS Service Generator v$CODE_GEN_VERSION"
cd; cd ~- # Remount CWD (volume reservation workaround)

while getopts ":c:k:m:" arg; do
	case "${arg}" in
		m)
			GEN_MODE=$OPTARG
			;;			
		h | \?)
			echo "${EC}ERROR${NC}: Invalid argument $OPTARG 
			Usage:
			-m: Generation mode (optional, [readonly, overwrite], default: readonly)" >&2
			exit
			;;
	esac
done

# Detect host type and set env accordingly
case "$OSTYPE" in
	linux*|linux-gnu*|bsd*|darwin*|solaris*)   
		VENV_BIN=bin
		ROOT_DIR=$(pwd)
		;;
	msys*|cygwin*)    
		VENV_BIN=Scripts
		ROOT_DIR=//${PWD}
		;;
	*)        
		echo -e "${EC}ERROR${NC}: OS of type $OSTYPE is not supported$"
		exit
		;;
esac

# Check if root dir contains space
if [[ $ROOT_DIR =~ " " ]]; then
    echo -e "${EC}ERROR${NC}: invalid path %ROOT_DIR (contains spaces), run the script in a path without spaces"
	exit
fi

# Automatically detect Python/Python3 if no binary selected
if [[ -z ${ROOT_PYTHON_PATH} ]]; then
	ROOT_PYTHON_PATH=$(command -v python3.9)
fi
if [[ -z ${ROOT_PYTHON_PATH} ]]; then
	ROOT_PYTHON_PATH=$(command -v python3)
fi
if [[ -z ${ROOT_PYTHON_PATH} ]]; then
	ROOT_PYTHON_PATH=$(command -v python)
fi

# Select generator compability for OS backend
CODE_GEN="$ROOT_PYTHON_PATH -m cookiecutter "


# Check if Python binary was found
if [[ -z ${ROOT_PYTHON_PATH} ]]; then
	echo -e "${WC}WARNING${NC}: Python is not installed, install python [sudo apt install python] and try again"
	exit
else
	PYTHON_VERSION=$($ROOT_PYTHON_PATH --version | grep -Po '(?<=Python )(.+)')
	PYTHON_VERSION_ARR=(${PYTHON_VERSION//./ })
	PYTHON_MAJOR_VERSION=${PYTHON_VERSION_ARR[0]}
	PYTHON_MINOR_VERSION=${PYTHON_VERSION_ARR[1]}
	echo -e "${IC}INFO${NC}: using Python $PYTHON_VERSION at $ROOT_PYTHON_PATH" 
fi

# Check for Pip
PIP_PATH=$(command -v pip)
if [[ -z ${PIP_PATH} ]]; then
	echo -e "${WC}WARNING${NC}: pip is not installed, install pip [sudo apt install pip] and try again"
	exit
else
	PIP_VERSION=$($ROOT_PYTHON_PATH -m pip --version)
	echo -e "${IC}INFO${NC}: using $PIP_VERSION at $PIP_PATH" 
fi

# Check if valid CLA
if [ -z "$CONFIG_PATH" ]; then
        echo -e "${EC}ERROR${NC}: valid config file must be specified with argument -c <path>." >&2
        exit 1
fi

# Evaluate config.yaml (needs to use LF line endings)
$ROOT_PYTHON_PATH -c 'import yaml, sys; yaml.safe_load(sys.stdin)' < $CONFIG_PATH
if [ $? -eq 0 ]; then
	eval $(parse_yaml $CONFIG_PATH)
	PROJECT_NAME=$default_context__service_name
	SERVICE_NAME=$default_context__service_name
else
	echo -e "${EC}ERROR${NC}: $CONFIG_PATH is not a valid .yaml file"
	exit
fi

# Generate template from virtual environment
if [[ -d $PROJECT_NAME ]] 
then
	if [[ "$GEN_MODE" = "overwrite" ]]
	then
		echo -e -n "${WC}WARNING${NC}: "
		read -p "you are about to overwrite folder $PROJECT_NAME in directory $OUT_PATH, continue? (y/n) " yn
		case $yn in 
			[yY]) 
				echo -e "${IC}INFO${NC}: building service environment using $BACKEND_COOKIECUTTER"
				build_from_local $ROOT_PYTHON_PATH
				if [ $? -eq 0 ]; then
					:
				else
          echo -e -n "${EC}ERROR${NC}: Build service returned an abort code, "
          echo -e "check the integrity of your $BACKEND_COOKIECUTTER installation."
          exit
				fi
				;;
			[nN]) 
				exit
				;;
		esac
	else
		echo -e "${EC}ERROR${NC}: directory $PROJECT_NAME already exists"
		exit
	fi
else
	echo -e "${IC}INFO${NC}: building service environment using $BACKEND_COOKIECUTTER"
	build_from_local $ROOT_PYTHON_PATH
				if [ $? -eq 0 ]; then
					:
				else
          echo -e -n "${EC}ERROR${NC}: Build service returned an abort code, "
          echo -e "check the integrity of your $BACKEND_COOKIECUTTER installation."
          exit
				fi
fi

# Compile protobuf files
echo -e "${IC}INFO${NC}: compiling protocol buffers using $BACKEND_PROTOC"
cd output/$OUT_PATH/$PROJECT_NAME/
protoc -I ./message_definitions/ --python_out ./model/io/messages/ ./message_definitions/*.proto

# Lint entire project structure with Black
echo -e "${IC}INFO${NC}: linting project files using $BACKEND_LINT"
cd $ROOT_DIR/output/
$ROOT_PYTHON_PATH -m $BACKEND_LINT $OUT_PATH/$PROJECT_NAME/ --quiet

# Copy local environment file
cp $OUT_PATH/$PROJECT_NAME/.env.template $OUT_PATH/$PROJECT_NAME/.env

echo -e "${IC}INFO${NC}: generated calculation service template is available at: ${BC}$OUT_PATH/$PROJECT_NAME${NC}"
exit