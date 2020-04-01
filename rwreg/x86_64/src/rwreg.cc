/*! \file rwreg.cc
 *  \brief This is a collection of basic RPC methods for FPGA registers access
 *  \author Mykhailo Dalchenko <mykhailo.dalchenko@cern.ch>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <xhal/extern/wiscrpcsvc.h>
#include <xhal/common/rpc/call.h>
#include <ctp7_modules/common/expert_tools.h>
#include <ctp7_modules/common/utils.h>

#define DLLEXPORT extern "C"

#define STANDARD_CATCH \
    catch (wisc::RPCSvc::NotConnectedException &e) { \
        printf("Caught NotConnectedException: %s\n", e.message.c_str()); \
        return 1; \
    } \
    catch (wisc::RPCSvc::RPCErrorException &e) { \
        printf("Caught RPCErrorException: %s\n", e.message.c_str()); \
        return 1; \
    } \
    catch (wisc::RPCSvc::RPCException &e) { \
        printf("Caught exception: %s\n", e.message.c_str()); \
        return 1; \
    } \
    catch (wisc::RPCMsg::BadKeyException &e) { \
        printf("Caught exception: %s\n", e.key.c_str()); \
        return 0xdeaddead; \
    } 

#define ASSERT(x) do { \
    if (!(x)) { \
        printf("Assertion Failed on line %u: %s\n", __LINE__, #x); \
        return 1; \
    } \
} while (0)

static wisc::RPCSvc conn;

/*! \fn uint32_t init(char * hostname)
 *  \brief Connect to the CTP7 and load the remote modules
 *
 *  Loaded modules:
 *      * memory
 *      * extras
 *
 *  \param hostname CTP7 card hostname
 */
DLLEXPORT uint32_t init(char * hostname)
{
    try {
        conn.connect(hostname);
    }
    catch (wisc::RPCSvc::ConnectionFailedException &e) {
        printf("Caught RPCErrorException: %s\n", e.message.c_str());
        return 1;
    }
    catch (wisc::RPCSvc::RPCException &e) {
        printf("Caught exception: %s\n", e.message.c_str());
        return 1;
    }

    try {
        ASSERT(conn.load_module("expert_tools", "expert_tools v1.0.1"));
        ASSERT(conn.load_module("utils", "utils v1.0.1"));
    }
    STANDARD_CATCH;

    return 0;
}

/*! \fn unsigned long getReg(unsigned int address)
 *  \brief Read register value
 *
 *  Returns `0xdeaddead` in case register is not accessible
 *
 *  \param address Register address
 */
DLLEXPORT unsigned long getReg(unsigned int address)
{
    try {
        return xhal::common::rpc::call<::expert::readRawAddress>(conn, address);
    } catch (...) {
        return 0xdeaddead;
    }
}

/*! \fn unsigned long putReg(unsigned int address, unsigned int value)
 *  \brief Write value to a register
 *
 *  Returns `0xdeaddead` in case register is not accessible. If writing was succesfull, returns written value.
 *
 *  \param address Register address
 *  \param value Value to write
 */
DLLEXPORT unsigned long putReg(unsigned int address, unsigned int value)
{
    try {
        xhal::common::rpc::call<::expert::writeRawAddress>(conn, address, value);
        return value;
    } catch (...) {
        return 0xdeaddead;
    }
}

/*!
 * \brief Update the LMDB address table on the back-end board
 *
 * \param path Path to the XML address table on the back-end board
 */
DLLEXPORT bool updateAddressTable(const char *path)
{
    try {
        xhal::common::rpc::call<::utils::update_address_table>(conn, path);
        return false;
    } catch (...) {
        return true;
    }
}
