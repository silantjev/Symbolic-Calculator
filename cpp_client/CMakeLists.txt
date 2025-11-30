cmake_minimum_required(VERSION 3.21)

# include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

project(cpp_client LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
option(CMAKE_BUILD_TYPE "build type" Debug)

find_package(Qt5 COMPONENTS Core Widgets Network REQUIRED)

file(GLOB SOURCE
    src/*.cpp
    src/requests/*.cpp
)
add_executable(${PROJECT_NAME} ${SOURCE})

# Устанавливаем RPATH для бинарника
set(RPATH_LIST
    "$ORIGIN"
    "$ORIGIN/lib"
    "$ORIGIN/../lib"
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    AUTOMOC ON # Включаем MOC автоматически
    CXX_STANDARD 17
)
option(FORMATTED_MSG "formatted log massages in cosole" ON)
if (FORMATTED_MSG)
    add_definitions(-DFORMATTED_MSG)
endif()

option(INSTALL_TO_BIN "install exqcutabe to bin/" OFF)
if (INSTALL_TO_BIN)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin
        INSTALL_RPATH_USE_LINK_PATH TRUE
        INSTALL_RPATH "${RPATH_LIST}"
        BUILD_WITH_INSTALL_RPATH TRUE
        SKIP_INSTALL_RPATH FALSE
    )
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE
    Qt5::Core 
    Qt5::Widgets 
    Qt5::Network 
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_definitions(${PROJECT_NAME} 
    PRIVATE QT_DEPRECATED_WARNINGS
)

#if (CMAKE_BUILD_TYPE STREQUAL "Release")
#    # Если нет флага "-g" удалим символы для оптимизации
#    string(FIND "${CMAKE_CXX_FLAGS} ${CMAKE_CXX_FLAGS_RELEASE}" "-g" HAS_DEBUG_FLAG)
#    if (HAS_DEBUG_FLAG EQUAL -1)
#        target_compile_options(${PROJECT_NAME} PRIVATE -ffunction-sections -fdata-sections)
#        target_link_options(${PROJECT_NAME} PRIVATE -Wl,--gc-sections,--strip-all)
#    endif()
#endif()

