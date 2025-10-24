#!/bin/bash
root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -e

export CACHE_VOLUME="$root/storage_conan/conan_cache"
mkdir -p "$CACHE_VOLUME"

profile="$root/storage_conan/profiles/release.cfg"

storage="core.cache:storage_path=${CACHE_VOLUME}/conan2/0/packages"
build_type="Release"
build_dir="build"

if [ ! -f "$profile" ]; then
    echo "Profile \"${profile}\" not found, creating default profile..."
    conan profile detect -e --name "${profile##*/}"
    cp "$(conan profile path "${profile##*/}")" "$profile" || { echo "ERROR: Failed to create \"${profile}\""; exit 1; }
fi

cd "$root"

while [[ $# -gt 0 ]]; do
    case "$1" in
        clean)
            [[ -d "$build_dir" ]] && rm -r "$build_dir" && echo Folder \"$(pwd)/"$build_dir"\" deleted
            [[ -d "$CACHE_VOLUME" ]] && rm -r "$CACHE_VOLUME" && echo Folder \"$CACHE_VOLUME\" deleted
            exit 0
            ;;
        --clean-cache)
            shift
            conan remove '*' -cc "$storage"
            echo '*' removed from $CACHE_VOLUME
            ;;
        -d)
            shift
            build_type="Debug"
            ;;
        --help)
            echo Usage:
            echo "  $0 [--clean-cache] [-d]"
            echo "  $0 clean"
            exit 0
            ;;
        *)
            echo  "Unknown option: $1" >&2
            echo "Try: $0 --help" >&2
            exit 1
            ;;
    esac
done

[[ -d "$build_dir" ]] && rm -r "$build_dir"
mkdir -p "$build_dir"

[[ -d bin ]] && rm -r bin
mkdir bin

conan install . --profile:build="$profile" --profile:host="$profile" --build=missing --output-folder="$build_dir" -cc "$storage" -r conancenter

cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=$build_type -DCMAKE_TOOLCHAIN_FILE="$build_dir"/conan_toolchain.cmake
cmake --build "$build_dir" --parallel $(($(nproc) - 1)) --verbose

