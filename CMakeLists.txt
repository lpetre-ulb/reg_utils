cmake_minimum_required(VERSION 2.8.12 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Prevent in-source builds
include(PreventInSourceBuilds)

project(reg_utils)

# Choose the sources depending of the target system
if("${CMAKE_SYSTEM_PROCESSOR}" STREQUAL "x86_64")
  add_subdirectory(rwreg/x86_64)
elseif("${CMAKE_SYSTEM_PROCESSOR}" STREQUAL "arm")
  add_subdirectory(rwreg/arm)
endif()

