cmake_minimum_required(VERSION 3.25)
project(pymeshlab2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_AUTOMOC ON)
set(QT_NO_PRIVATE_MODULE_WARNING ON)

find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui GuiPrivate)

set(QMESHLAB_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/external/QMeshLab)

set(QMESHLAB_COLORMAP_FILES
    external/QMeshLab/colormaps/rainbow.json
    external/QMeshLab/colormaps/viridis.json
    external/QMeshLab/colormaps/gray.json
    external/QMeshLab/colormaps/plasma.json
    external/QMeshLab/colormaps/cividis.json
    external/QMeshLab/colormaps/turbo.json
)

set(QMESHLAB_BASIC_FILTER_DESCRIPTOR external/QMeshLab/plugins/filter_basic/filters.json)

foreach(_colormap_file IN LISTS QMESHLAB_COLORMAP_FILES)
    get_filename_component(_colormap_name "${_colormap_file}" NAME)
    set_source_files_properties("${_colormap_file}" PROPERTIES QT_RESOURCE_ALIAS "colormaps/${_colormap_name}")
endforeach()

set_source_files_properties(
    ${QMESHLAB_BASIC_FILTER_DESCRIPTOR}
    PROPERTIES
        QT_RESOURCE_ALIAS "filters.json"
)

add_library(qmeshlab2_backend STATIC
    ${QMESHLAB_ROOT}/colormap.h
    ${QMESHLAB_ROOT}/colormap.cpp
    ${QMESHLAB_ROOT}/document.h
    ${QMESHLAB_ROOT}/document.cpp
    ${QMESHLAB_ROOT}/filterdescriptorloader.h
    ${QMESHLAB_ROOT}/filterdescriptorloader.cpp
    ${QMESHLAB_ROOT}/filterparam.h
    ${QMESHLAB_ROOT}/filterparam.cpp
    ${QMESHLAB_ROOT}/linerenderer.h
    ${QMESHLAB_ROOT}/linerenderer.cpp
    ${QMESHLAB_ROOT}/meshfilterplugin.h
    ${QMESHLAB_ROOT}/meshfilterplugin.cpp
    ${QMESHLAB_ROOT}/meshfilterpluginmanager.h
    ${QMESHLAB_ROOT}/meshfilterpluginmanager.cpp
    ${QMESHLAB_ROOT}/meshgpuresourcecache.h
    ${QMESHLAB_ROOT}/meshgpuresourcecache.cpp
    ${QMESHLAB_ROOT}/meshioplugin.h
    ${QMESHLAB_ROOT}/meshiopluginmanager.h
    ${QMESHLAB_ROOT}/meshiopluginmanager.cpp
    ${QMESHLAB_ROOT}/vcgmesh.h

    ${QMESHLAB_ROOT}/plugins/meshpluginregistry.h
    ${QMESHLAB_ROOT}/plugins/meshpluginregistry.cpp
    ${QMESHLAB_ROOT}/plugins/filterpluginregistry.h
    ${QMESHLAB_ROOT}/plugins/filterpluginregistry.cpp

    ${QMESHLAB_ROOT}/plugins/io_vcg/vcgimportplugin.h
    ${QMESHLAB_ROOT}/plugins/io_vcg/vcgimportplugin.cpp
    ${QMESHLAB_ROOT}/vcglib/wrap/ply/plylib.cpp

    ${QMESHLAB_ROOT}/plugins/filter_basic/basicfilterplugin.h
    ${QMESHLAB_ROOT}/plugins/filter_basic/basicfilterplugin.cpp
)

target_compile_definitions(qmeshlab2_backend
    PRIVATE
        QMESH_PLUGIN_IO_VCG_ENABLED=1
        QMESH_PLUGIN_FILTER_BASIC_ENABLED=1
)

target_include_directories(qmeshlab2_backend
    PUBLIC
        ${QMESHLAB_ROOT}
        ${QMESHLAB_ROOT}/vcglib
        ${QMESHLAB_ROOT}/vcglib/eigenlib
)

target_link_libraries(qmeshlab2_backend
    PUBLIC
        Qt6::Core
        Qt6::Gui
        Qt6::GuiPrivate
)

qt_add_resources(qmeshlab2_backend "qmeshlab2_colormaps"
    PREFIX "/"
    FILES
    ${QMESHLAB_COLORMAP_FILES}
)

qt_add_resources(qmeshlab2_backend "qmeshlab2_filter_basic_descriptors"
    PREFIX "/filters/qmeshlab.filter.basic"
    FILES
    ${QMESHLAB_BASIC_FILTER_DESCRIPTOR}
)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

find_package(nanobind CONFIG QUIET)
if (NOT nanobind_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        nanobind
        GIT_REPOSITORY https://github.com/wjakob/nanobind.git
        GIT_TAG v2.2.0
    )
    FetchContent_MakeAvailable(nanobind)
endif()

nanobind_add_module(_pymeshlab2
    NB_STATIC
    src/cpp/module.cpp
    src/cpp/meshset_core.cpp
)

target_include_directories(_pymeshlab2
    PRIVATE
        src/cpp
)

target_link_libraries(_pymeshlab2
    PRIVATE
    qmeshlab2_backend
)

if (SKBUILD)
    install(TARGETS _pymeshlab2 LIBRARY DESTINATION pymeshlab2)
endif()
