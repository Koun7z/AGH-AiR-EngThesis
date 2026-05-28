#!/usr/bin/env bash

if [[ -t 1 ]]; then
  C_RESET='\e[0m'
  C_BOLD='\e[1m'
  C_DIM='\e[2m'
  C_UNDER='\e[4m'

  C_RED='\e[31m'
  C_GRN='\e[32m'
  C_YEL='\e[33m'
  C_BLU='\e[34m'
  C_MAG='\e[35m'
  C_CYN='\e[36m'
  C_WHT='\e[37m'
else
  C_RESET= C_BOLD= C_DIM= C_UNDER= C_RED= C_GRN= C_YEL= C_BLU= C_MAG= C_CYN= C_WHT=
fi

log_info()    { printf "${C_BLU}%s${C_RESET}\n" "$*"; }
log_ok()      { printf "${C_GRN}%s${C_RESET}\n" "$*"; }
log_warn()    { printf "${C_YEL}%s${C_RESET}\n" "$*"; }
log_error()   { printf "${C_RED}%s${C_RESET}\n" "$*"; }


# Make all paths relative to script location
cd "$(dirname "$(realpath "$0")")"

# Script configuration

# Edit if this file is not in the project root directory
PROJECT_ROOT_DIR="." 
# Edit to use CMakeLists.txt from location other then project root
CMAKE_LISTS_LOCATION="${PROJECT_ROOT_DIR}/CMakeLists.txt"
OPENOCD_CONFIG_FILE="${PROJECT_ROOT_DIR}/openocd.cfg"
TARGET_BINARY_NAME="NucleoIKS01A3.elf"

# Edit if this file is not in the project root directory
PROJECT_ROOT_DIR="$(realpath ".")" 
# Edit to use CMakeLists.txt from location other then project root
CMAKE_LISTS_LOCATION="${PROJECT_ROOT_DIR}/CMakeLists.txt"
OPENOCD_CONFIG_FILE="${PROJECT_ROOT_DIR}/openocd.cfg"
TARGET_BINARY_NAME="NucleoIKS01A3.elf"
CONFIG_FILE="${PROJECT_ROOT_DIR}/software/Inc/Config.h"

DEFAULT_BUILD_TYPE="Debug"

usage() {
  echo "Usage: $0 [options...]" >&2
  echo "   -c     Remove build files (Clean)"
  echo "   -t     Build type: <Debug/Release>"
  echo "   -p     Prepare CMake files for Ninja and run CMake. Running this option multiple times will mostly reconfigure the project
          but some cached option (e.g. used compiler) may not be changed. To clear all caches run build.sh -c first"
  echo "   -b     Build binary files"
  echo "   -f     Flash the firmware"
}

clean() {
  if [[ -d "${PROJECT_ROOT_DIR}/build" ]]; then
    log_info "Removing build files from build folder"
    rm -rf "${PROJECT_ROOT_DIR}/build"
  else
    log_warn "Directory doesn't exist: ${PROJECT_ROOT_DIR}/build"
  fi
}

read_version() {
  if [ -f "$CONFIG_FILE" ]; then
    major=$(grep "#define FIRMWARE_VERSION_MAJOR" "$CONFIG_FILE" | awk '{print $3}')
    minor=$(grep "#define FIRMWARE_VERSION_MINOR" "$CONFIG_FILE" | awk '{print $3}')
    patch=$(grep "#define FIRMWARE_VERSION_PATCH" "$CONFIG_FILE" | awk '{print $3}')
    version="$major.$minor.$patch"
    log_info "Build version: $version"
    echo "$version" > "${PROJECT_ROOT_DIR}/build/version.txt"
  else
    log_warn "Could't read build version: "
    log_warn "File doesn't exist: ${CONFIG_FILE}"
  fi
}

if [[ -z "$1" ]]; then
  usage
  exit 1
fi

mkdir -p ${PROJECT_ROOT_DIR}/build
while getopts ":ct:pbf" o; do
  case "${o}" in
  c)
    clean
    exit
    ;;
  t)
    BUILD_TYPE=${OPTARG}

    if [[ "$BUILD_TYPE" != "Debug" && "$BUILD_TYPE" != "Release" ]]; then
      log_error "${BUILD_TYPE} is not a valid build type."
      exit 1
    fi

    if [[ -f "${PROJECT_ROOT_DIR}/build/build.cfg" ]]; then
      OLD_TYPE=$(< "${PROJECT_ROOT_DIR}/build/build.cfg")

      if [[ "$OLD_TYPE" != "$BUILD_TYPE" ]]; then
        log_info "Build type changed from ${OLD_TYPE} to ${BUILD_TYPE}, rerunning cmake."
        PREPARE=true
      fi

    fi
    
    echo ${BUILD_TYPE} > "${PROJECT_ROOT_DIR}/build/build.cfg"

    ;;
  p)
    PREPARE=true
    ;;
  b)
    BUILD=true
    ;;
  f)
    FLASH=true
    ;;
  *)
    usage
    exit 0
    ;;
  esac
done

read_version

if [[ ! -f "${PROJECT_ROOT_DIR}/build/build.cfg" ]]; then
  log_info "Build config file not found, creating with default value: ${DEFAULT_BUILD_TYPE}"
  log_info "Run build.sh -t <Debug/Release> to change"
  echo "${DEFAULT_BUILD_TYPE}" > "${PROJECT_ROOT_DIR}/build/build.cfg"
fi

BUILD_TYPE=$(< "${PROJECT_ROOT_DIR}/build/build.cfg")
log_info "Build type: ${BUILD_TYPE}."
if [[ "$BUILD_TYPE" != "Debug" && "$BUILD_TYPE" != "Release" ]]; then
  log_error "Build config file corrupted"
  log_error "${BUILD_TYPE} is not a valid build type"
  log_info "Run build.sh -t <Debug/Release> to fix"
  exit 1
fi

if [[ "$PREPARE" ]]; then
  if [[ ! -f ${PROJECT_ROOT_DIR}/CMakeLists.txt ]]; then
      echo "Using CMakeLists.txt from ${CMAKE_LISTS_LOCATION}"
      ln -s ${CMAKE_LISTS_LOCATION} ${PROJECT_ROOT_DIR}/CMakeLists.txt
  fi

  echo "Preparing CMake configuration."
  mkdir -p ${PROJECT_ROOT_DIR}/build/${BUILD_TYPE}
  cmake --log-level=DEBUG \
         -S ${PROJECT_ROOT_DIR} -B ${PROJECT_ROOT_DIR}/build/${BUILD_TYPE} -G Ninja \
         -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
         -DCMAKE_VERBOSE_MAKEFILE=ON \
         -DCMAKE_BUILD_TYPE=${BUILD_TYPE}

  echo "Using compile_commands.json from ${BUILD_TYPE} build."
  ln -sf "$(realpath "${PROJECT_ROOT_DIR}/build/${BUILD_TYPE}/compile_commands.json")"  "${PROJECT_ROOT_DIR}/build/compile_commands.json"
fi

if [[ "$BUILD" ]]; then
  echo "Building project (${BUILD_TYPE})."
  ninja -C "${PROJECT_ROOT_DIR}/build/${BUILD_TYPE}"

  if [[ $? -ne 0 ]]; then
    log_error "Build failed"
    exit 1
  fi

fi


if [[ "$FLASH" ]]; then
  log_info "Flashing STM32 firmware: ${PROJECT_ROOT_DIR}/build/${BUILD_TYPE}/${TARGET_BINARY_NAME}."
  openocd -f ${OPENOCD_CONFIG_FILE} -c "program ${PROJECT_ROOT_DIR}/build/${BUILD_TYPE}/${TARGET_BINARY_NAME} verify reset exit"
fi