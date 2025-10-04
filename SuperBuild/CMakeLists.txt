cmake_minimum_required(VERSION 3.1)

project(ODM-SuperBuild)

# Setup SuperBuild root location
set(SB_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})

if (NOT CMAKE_BUILD_TYPE)
    message(STATUS "No build type selected, default to Release")
    set(CMAKE_BUILD_TYPE "Release")
endif()

if (APPLE)
    find_program(HOMEBREW_EXECUTABLE brew)
    mark_as_advanced(FORCE HOMEBREW_EXECUTABLE)
    if (HOMEBREW_EXECUTABLE)
        # Detected a Homebrew install, query for its install prefix.
        execute_process(COMMAND ${HOMEBREW_EXECUTABLE} --prefix
            OUTPUT_VARIABLE HOMEBREW_INSTALL_PREFIX
            OUTPUT_STRIP_TRAILING_WHITESPACE)
        message(STATUS "Detected Homebrew with install prefix: "
            "${HOMEBREW_INSTALL_PREFIX}, adding to CMake search paths.")
        list(APPEND CMAKE_PREFIX_PATH "${HOMEBREW_INSTALL_PREFIX}")
    endif()

    # Use homebrew's clang compiler since Apple
    # does not allow us to link to libomp
    set(CXX_PATH ${HOMEBREW_INSTALL_PREFIX}/bin/c++-12)
    set(APPLE_CMAKE_ARGS "")
    
    message("Checking for ${CXX_PATH}...")
    if(EXISTS "${CXX_PATH}")
        message("Found Homebrew's C++ compiler: ${CXX_PATH}")
        set(CMAKE_CXX_COMPILER ${CXX_PATH})
        list(APPEND APPLE_CMAKE_ARGS "-DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}")
    endif()

    set(C_PATH ${HOMEBREW_INSTALL_PREFIX}/bin/gcc-12)
    message("Checking for ${C_PATH}...")
    if(EXISTS "${C_PATH}")
        message("Found Homebrew's C compiler: ${C_PATH}")
        set(CMAKE_C_COMPILER ${C_PATH})
        list(APPEND APPLE_CMAKE_ARGS "-DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}")
    endif()

    if (NOT APPLE_CMAKE_ARGS)
        message(WARNING "Cannot find Homebrew's compiler, compilation might fail...")
    endif()
endif()

################################
# Setup SuperBuild directories #
################################

# Setup location where source tar-balls are downloaded
set(SB_DOWNLOAD_DIR "${SB_ROOT_DIR}/download"
    CACHE PATH "Location where source tar-balls are (to be) downloaded.")
mark_as_advanced(SB_DOWNLOAD_DIR)

message(STATUS "SuperBuild files will be downloaded to: ${SB_DOWNLOAD_DIR}")


# Setup location where source tar-balls are located
set(SB_SOURCE_DIR "${SB_ROOT_DIR}/src"
    CACHE PATH "Location where source tar-balls are (will be).")
mark_as_advanced(SB_SOURCE_DIR)
set(SB_BUILD_DIR "${SB_ROOT_DIR}/build")

message(STATUS "SuperBuild source files will be extracted to: ${SB_SOURCE_DIR}")


# Setup location where source tar-balls are located
set(SB_INSTALL_DIR "${SB_ROOT_DIR}/install"
    CACHE PATH "Location where source tar-balls are (will be) installed.")
mark_as_advanced(SB_SOURCE_DIR)

message(STATUS "SuperBuild source files will be installed to: ${SB_INSTALL_DIR}")


# Setup location where binary files are located
set(SB_BINARY_DIR "${SB_ROOT_DIR}/build"
    CACHE PATH "Location where files are (will be) located.")
mark_as_advanced(SB_BINARY_DIR)

message(STATUS "SuperBuild binary files will be located to: ${SB_BINARY_DIR}")

if (WIN32)
  if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    message(FATAL_ERROR "CMAKE_TOOLCHAIN_FILE not set. You need to set it to the path of vcpkg.cmake")
  endif()
  get_filename_component(CMAKE_TOOLCHAIN_DIR ${CMAKE_TOOLCHAIN_FILE} DIRECTORY)
  get_filename_component(VCPKG_ROOT "${CMAKE_TOOLCHAIN_DIR}/../../" ABSOLUTE)
  set(WIN32_CMAKE_ARGS "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}")
  set(PYTHON_HOME "${SB_ROOT_DIR}/../venv")
  set(PYTHON_EXE_PATH "${PYTHON_HOME}/Scripts/python")

  # Use the GDAL version that comes with pip
  set(GDAL_ROOT "${PYTHON_HOME}/Lib/site-packages/osgeo")
  set(GDAL_LIBRARY "${GDAL_ROOT}/gdal.lib")
  set(GDAL_INCLUDE_DIR "${GDAL_ROOT}/include/gdal")

  message("Copying VCPKG DLLs...")
  file(GLOB COPY_DLLS "${VCPKG_ROOT}/installed/x64-windows/bin/*.dll")
  file(COPY ${COPY_DLLS} DESTINATION "${SB_INSTALL_DIR}/bin")

  message("Copying CUDA DLLs...")
  file(GLOB CUDA_DLLS "$ENV{CUDA_PATH}/bin/cudart64*.dll")
  file(COPY ${CUDA_DLLS} DESTINATION "${SB_INSTALL_DIR}/bin")

  set(WIN32_GDAL_ARGS -DGDAL_FOUND=TRUE -DGDAL_LIBRARY=${GDAL_LIBRARY} -DGDAL_INCLUDE_DIR=${GDAL_INCLUDE_DIR})
elseif(APPLE)
    set(PYTHON_HOME "${SB_ROOT_DIR}/../venv")
    set(PYTHON_EXE_PATH "${PYTHON_HOME}/bin/python")
else()
  set(PYTHON_HOME "${SB_ROOT_DIR}/../venv")
  set(PYTHON_EXE_PATH "${PYTHON_HOME}/bin/python3")
endif()

# Path to additional CMake modules
set(CMAKE_MODULE_PATH ${SB_ROOT_DIR}/cmake)

include(ExternalProject)
include(ExternalProject-Setup)

#########################################
# Download and install third party libs #
#########################################

# ---------------------------------------------------------------------------------------------
# Open Source Computer Vision (OpenCV)
#
set(ODM_OpenCV_Version 4.12.0)
option(ODM_BUILD_OpenCV "Force to build OpenCV library" OFF)

SETUP_EXTERNAL_PROJECT(OpenCV ${ODM_OpenCV_Version} ${ODM_BUILD_OpenCV})


# ---------------------------------------------------------------------------------------------
# Google Flags library (GFlags)
#
set(ODM_GFlags_Version 2.2.2)
option(ODM_BUILD_GFlags "Force to build GFlags library" OFF)

SETUP_EXTERNAL_PROJECT(GFlags ${ODM_GFlags_Version} ${ODM_BUILD_GFlags})


# ---------------------------------------------------------------------------------------------
# Ceres Solver
#
set(ODM_Ceres_Version 2.0.0)
option(ODM_BUILD_Ceres "Force to build Ceres library" OFF)

SETUP_EXTERNAL_PROJECT(Ceres ${ODM_Ceres_Version} ${ODM_BUILD_Ceres})


# ---------------------------------------------------------------------------------------------
# Hexer
#
SETUP_EXTERNAL_PROJECT(Hexer 1.5 ON)

# ---------------------------------------------------------------------------------------------
# Open Structure from Motion (OpenSfM)
#

set(custom_libs OpenSfM
				LASzip
				PDAL
				PDALPython
				FPCFilter
				PyPopsift
				RenderDEM
)

foreach(lib ${custom_libs})
	SETUP_EXTERNAL_PROJECT_CUSTOM(${lib})
endforeach()

include(ProcessorCount)
ProcessorCount(nproc)

externalproject_add(dem2mosaic
    DEPENDS           opencv 
    GIT_REPOSITORY    https://github.com/NathanMOlson/dem2mosaic
    GIT_TAG           main
    PREFIX            ${SB_BINARY_DIR}/dem2mosaic
    SOURCE_DIR        ${SB_SOURCE_DIR}/dem2mosaic
    CMAKE_ARGS        -DCMAKE_INSTALL_PREFIX:PATH=${SB_INSTALL_DIR} 
                      ${WIN32_CMAKE_ARGS}
)

externalproject_add(fastrasterfilter
    GIT_REPOSITORY    https://github.com/OpenDroneMap/FastRasterFilter.git
    GIT_TAG           main
    PREFIX            ${SB_BINARY_DIR}/fastrasterfilter
    SOURCE_DIR        ${SB_SOURCE_DIR}/fastrasterfilter
    CMAKE_ARGS        -DCMAKE_INSTALL_PREFIX:PATH=${SB_INSTALL_DIR}
                      ${WIN32_CMAKE_ARGS} ${WIN32_GDAL_ARGS}
)
