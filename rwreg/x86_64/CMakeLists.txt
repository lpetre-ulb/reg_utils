find_package(wiscrpcsvc REQUIRED)

add_library(rwreg SHARED
  src/rwreg.cc)

target_include_directories(rwreg PRIVATE include)

target_link_libraries(rwreg PRIVATE wiscrpcsvc::wiscrpcsvc)

install(TARGETS rwreg
  LIBRARY DESTINATION lib)

