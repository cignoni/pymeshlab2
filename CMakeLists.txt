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
    ${QMESHLAB_ROOT}/src/render/colormap.h
    ${QMESHLAB_ROOT}/src/render/colormap.cpp
    ${QMESHLAB_ROOT}/src/core/document.h
    ${QMESHLAB_ROOT}/src/core/document.cpp
    ${QMESHLAB_ROOT}/src/core/camerashot.h
    ${QMESHLAB_ROOT}/src/core/camerashot.cpp
    ${QMESHLAB_ROOT}/src/plugins/filterdescriptorloader.h
    ${QMESHLAB_ROOT}/src/plugins/filterdescriptorloader.cpp
    ${QMESHLAB_ROOT}/src/core/filterparam.h
    ${QMESHLAB_ROOT}/src/core/filterparam.cpp
    ${QMESHLAB_ROOT}/src/render/linerenderer.h
    ${QMESHLAB_ROOT}/src/render/linerenderer.cpp
    ${QMESHLAB_ROOT}/src/plugins/meshfilterplugin.h
    ${QMESHLAB_ROOT}/src/plugins/meshfilterplugin.cpp
    ${QMESHLAB_ROOT}/src/plugins/meshfilterpluginmanager.h
    ${QMESHLAB_ROOT}/src/plugins/meshfilterpluginmanager.cpp
    ${QMESHLAB_ROOT}/src/render/meshgpuresourcecache.h
    ${QMESHLAB_ROOT}/src/render/meshgpuresourcecache.cpp
    ${QMESHLAB_ROOT}/src/plugins/meshioplugin.h
    ${QMESHLAB_ROOT}/src/plugins/meshiopluginmanager.h
    ${QMESHLAB_ROOT}/src/plugins/meshiopluginmanager.cpp
    ${QMESHLAB_ROOT}/src/core/vcgmesh.h

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
    ${QMESHLAB_ROOT}/src/core
    ${QMESHLAB_ROOT}/src/render
    ${QMESHLAB_ROOT}/src/plugins
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

nanobind_add_module(_qmeshlab
    NB_STATIC
    external/QMeshLab/src/python/bindings/module.cpp
    external/QMeshLab/src/python/bindings/meshset_core.cpp
)

target_include_directories(_qmeshlab
    PRIVATE
        external/QMeshLab/src/python/bindings
)

target_link_libraries(_qmeshlab
    PRIVATE
    qmeshlab2_backend
)

if (SKBUILD)
    install(TARGETS _qmeshlab LIBRARY DESTINATION pymeshlab2)
endif()
