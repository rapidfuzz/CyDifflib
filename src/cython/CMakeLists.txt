function(create_cython_target _name)
  if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/${_name}.cxx)
    set(${_name}
        ${CMAKE_CURRENT_LIST_DIR}/${_name}.cxx
        PARENT_SCOPE)
  else()
    find_package(Cython REQUIRED)
    add_cython_target(${_name} CXX)
    set(${_name}
        ${_name}
        PARENT_SCOPE)
  endif()
endfunction(create_cython_target)

create_cython_target(_initialize)
add_library(_initialize MODULE ${_initialize})
target_compile_features(_initialize PUBLIC cxx_std_11)
python_extension_module(_initialize)
install(TARGETS _initialize LIBRARY DESTINATION src/cydifflib)
