#!/bin/bash
root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -e

export CACHE_VOLUME="$root/resources/conan_cache"
mkdir -p "$CACHE_VOLUME"

profile="$root/resources/profiles/release.cfg"
storage="-cc core.cache:storage_path=${CACHE_VOLUME}/conan2/0/packages"

if [ ! -f "$profile" ]; then
    echo "Profile \"${profile}\" not found, creating default profile..."
    conan profile detect -e --name "${profile##*/}"
    cp "$(conan profile path "${profile##*/}")" "$profile" || { echo "ERROR: Failed to create \"${profile}\""; exit 1; }
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean)
            # conan remove '*' $storage
            exit 1
            shift
            echo '*' removed from $CACHE_VOLUME
            ;;
        --help)
            echo Usage $0 [--clean]
            exit 0
            ;;
        *)
            echo  "Unknown option: $1" >&2
            echo Usage $0 [--clean] >&2
            exit 1
            ;;
    esac
done

cd "$root"
[[ -d build ]] && rm -r build/

[[ -d bin ]] && rm -r bin
mkdir bin

conan install . --profile:build="$profile" --profile:host="$profile" --build=missing --output-folder=build $storage -r conancenter

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 7 --verbose

# копирование в bin:

# cp build/cpp_client bin/
# cd bin
# ldd cpp_client | grep "=> /" | awk '{print $3}' | xargs -I {} cp -L {} .
# cd ..
# 
# echo "Deployed! Run: ./bin/cpp_client"
