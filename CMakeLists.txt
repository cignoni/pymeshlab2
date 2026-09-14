cmake_minimum_required(VERSION 3.25)
project(pymeshlab2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_AUTOMOC ON)
set(QT_NO_PRIVATE_MODULE_WARNING ON)

set(QMESH_REQUIRE_VCPKG_DEPS OFF)
set(QMESHLAB_BUILD_APP OFF)
set(QMESHLAB_BUILD_TESTS OFF)
set(QMESHLAB_MATH_HELP OFF)
set(QMESHLAB_PYTHON_CONSOLE OFF)
set(QMESH_PLUGIN_OBJ_RAPIDOBJ OFF)
set(QMESH_PLUGIN_E57 OFF)
set(QMESH_PLUGIN_GLTF OFF)
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/external/QMeshLab/external/meshfix/CMakeLists.txt")
    set(QMESH_PLUGIN_FILTER_MESHFIX OFF)
endif()
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/external/QMeshLab/external/qslim/mixkit/src/MxQSlim.h")
    set(QMESH_PLUGIN_FILTER_QSLIM OFF)
endif()
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/external/QMeshLab/external/quadwild-bimdf/quadwild/CMakeLists.txt")
    set(QMESH_PLUGIN_FILTER_QUADWILD OFF)
endif()
add_subdirectory(external/QMeshLab EXCLUDE_FROM_ALL)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

find_package(nanobind CONFIG QUIET)
if (NOT nanobind_FOUND)
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
        OUTPUT_VARIABLE _nanobind_cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _nanobind_cmake_result
    )
    if (_nanobind_cmake_result EQUAL 0 AND EXISTS "${_nanobind_cmake_dir}")
        find_package(nanobind CONFIG QUIET PATHS "${_nanobind_cmake_dir}" NO_DEFAULT_PATH)
    endif()
endif()
if (NOT nanobind_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        nanobind
        GIT_REPOSITORY https://github.com/wjakob/nanobind.git
        GIT_TAG v2.2.0
    )
    FetchContent_MakeAvailable(nanobind)
endif()

include(${CMAKE_CURRENT_SOURCE_DIR}/external/QMeshLab/src/python/bindings/sources.cmake)

nanobind_add_module(_qmeshlab NB_STATIC ${QMESHLAB_PYTHON_BINDING_SOURCES})

target_compile_definitions(_qmeshlab PRIVATE PYMESHLAB_STANDALONE=1)

target_include_directories(_qmeshlab
    PRIVATE
        external/QMeshLab/src/python/bindings
)

target_link_libraries(_qmeshlab
    PRIVATE
        QMeshLabPlugins
)

if (SKBUILD)
    install(TARGETS _qmeshlab LIBRARY DESTINATION pymeshlab2)
endif()
