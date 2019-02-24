add_library(rwreg SHARED
  src/rwreg.cc
  src/libmemsvc.c)

set_property(TARGET rwreg PROPERTY C_STANDARD 11)
set_property(TARGET rwreg PROPERTY CXX_STANDARD 11)

target_include_directories(rwreg PRIVATE include)

install(TARGETS rwreg
  LIBRARY DESTINATION lib)

