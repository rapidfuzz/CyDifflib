function(create_cython_target _name)
  if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/${_name}.cxx)
    set(${_name}
        ${CMAKE_CURRENT_LIST_DIR}/${_name}.cxx
        PARENT_SCOPE)
  else()
    add_custom_command(
      OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${_name}.cxx"
      MAIN_DEPENDENCY "${CMAKE_CURRENT_LIST_DIR}/${_name}.pyx"
      VERBATIM
      COMMAND
        Python::Interpreter -m cython "${CMAKE_CURRENT_LIST_DIR}/${_name}.pyx"
        --cplus --output-file "${CMAKE_CURRENT_BINARY_DIR}/${_name}.cxx")

    set(${_name}
        ${CMAKE_CURRENT_BINARY_DIR}/${_name}.cxx
        PARENT_SCOPE)
  endif()
endfunction(create_cython_target)

function(rf_add_library name)
  if(CMAKE_VERSION VERSION_LESS 3.17)
    python_add_library(${name} MODULE ${ARGV})
    get_property(
      suffix
      TARGET ${name}
      PROPERTY SUFFIX)
    if(NOT suffix)
      set(suffix "${CMAKE_SHARED_MODULE_SUFFIX}")
    endif()
    set_property(TARGET ${name} PROPERTY SUFFIX ".${Python_SOABI}${suffix}")
  else()
    python_add_library(${name} MODULE WITH_SOABI ${ARGV})
  endif()
endfunction(rf_add_library)

create_cython_target(_initialize)
rf_add_library(_initialize ${_initialize})
target_compile_features(_initialize PUBLIC cxx_std_17)
install(TARGETS _initialize DESTINATION cydifflib/)
