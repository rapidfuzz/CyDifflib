cmake_minimum_required(VERSION 3.12.0)

cmake_policy(SET CMP0054 NEW)
set(SKBUILD_LINK_LIBRARIES_KEYWORD PRIVATE)

set(THREADS_PREFER_PTHREAD_FLAG ON)
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
  set(CMAKE_OSX_DEPLOYMENT_TARGET
      "10.9"
      CACHE STRING "Minimum OS X deployment version")
endif()

project(cydifflib LANGUAGES C CXX)

if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -pedantic)
endif()

find_package(PythonExtensions REQUIRED)
find_package(Python COMPONENTS Interpreter Development)
find_package(Cython REQUIRED)

add_subdirectory(src/cython)
