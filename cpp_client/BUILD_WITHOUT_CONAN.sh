#!/bin/bash
root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -e

build_type="Release"
build_dir="build"

cd "$root"

while [[ $# -gt 0 ]]; do
    case "$1" in
        clean)
            [[ -d "$build_dir" ]] && rm -r "$build_dir" && echo Folder \"$(pwd)/"$build_dir"\" deleted
            exit 0
            ;;
        -d)
            shift
            build_type="Debug"
            ;;
        --help)
            echo Usage:
            echo "  $0 [-d]"
            echo "  $0 clean"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Try: $0 --help" >&2
            exit 1
            ;;
    esac
done

[[ -d "$build_dir" ]] && rm -r "$build_dir"
mkdir -p "$build_dir"

[[ -d bin ]] && rm -r bin
mkdir bin

cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=$build_type -DINSTALL_TO_BIN=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build "$build_dir" --parallel $(($(nproc) - 1)) --verbose
