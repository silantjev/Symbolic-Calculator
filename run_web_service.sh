#!/bin/bash
dir="$(dirname -- "$0")"
dir="$(realpath -- "$dir")"

cd "$dir"

if [[ -z "$VIRTUAL_ENV" ]]; then
    VIRTUAL_ENV="$dir"/.venv
    if [[ -d "$VIRTUAL_ENV" ]];  then
        source "$VIRTUAL_ENV/bin/activate"
    else
        echo Warning: directory $VIRTUAL_ENV not found. Install virtual environment >&2
    fi
fi


if ! command -v uvicorn &> /dev/null; then
    echo "Module uvicorn not found. Install dependencies: 'pip install -r requirements.txt'"
    exit 1
fi

# host="127.0.0.1"
port="8000"
export CONSOLE_LOGGING="no"
export FILE_LOGGING="no"

help_stirng="Usage: $0 [-l] [-f] [-p CONFIG_PATH] [--host HOST] [--port PORT] [--reload] [<other uvicorn options: try 'uvicorn --help' for details>]"

# Обработка аргументов командной строки
while getopts ":-:p:hlf" opt; do
  case "$opt" in
    h)
        echo $help_stirng
        exit 0
    ;;
    l) export CONSOLE_LOGGING="yes" ;;
    f) export FILE_LOGGING="yes" ;;
    p) export CONF_PATH="${OPTARG}" ;; 
    -) 
        case $OPTARG in 
            # host=*) host="${OPTARG#*=}" ;;
            # host)
                # host="${!OPTIND}"
                # let OPTIND++
            # ;;
            port=*) port="${OPTARG#*=}" ;;
            port)
                port="${!OPTIND}"
                let OPTIND++
            ;;
            help)
                echo $help_stirng
                exit 0
            ;;
        esac
    ;;
    :) echo "Error: Option -$OPTARG requires an argument" >&2; exit 1 ;;
  esac
done

# Проверка корректности порта
if ! [[ "$port" =~ ^[0-9]+$ ]]; then
    echo "Error: port should be an integer"
    exit 1
fi

if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
    echo "Error: port should be in [1, 65535]"
    exit 1
fi

# Удаляем -l и -f
new_args=()
skip="no"
for arg in "$@"; do
    [[ $skip == "yes" ]] &&{ skip="no"; continue; }
    [[ $arg == "-l" || $arg == "-f" ]] && continue
    [[ $arg == "-p" ]] && { skip="yes"; continue; }
    new_args+=("$arg")
done

set -- "${new_args[@]}"

uvicorn web.api_service:app "$@"
