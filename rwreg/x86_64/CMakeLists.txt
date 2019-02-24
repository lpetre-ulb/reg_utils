add_library(rwreg SHARED
  src/rwreg.cc)

target_include_directories(rwreg PRIVATE include)

# TODO: use find_package
target_link_libraries(rwreg PRIVATE /opt/wiscrpcsvc/lib/libwiscrpcsvc.so)

install(TARGETS rwreg
  LIBRARY DESTINATION lib)

