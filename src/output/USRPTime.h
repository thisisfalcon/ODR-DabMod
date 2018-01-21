/*
   Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010 Her Majesty the
   Queen in Right of Canada (Communications Research Center Canada)

   Copyright (C) 2017
   Matthias P. Braendli, matthias.braendli@mpb.li

    http://opendigitalradio.org

DESCRIPTION:
   The part of the UHD output that takes care of the GPSDO and setting device
   time.
*/

/*
   This file is part of ODR-DabMod.

   ODR-DabMod is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   ODR-DabMod is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with ODR-DabMod.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#ifdef HAVE_CONFIG_H
#   include <config.h>
#endif

#ifdef HAVE_OUTPUT_UHD

#include <uhd/usrp/multi_usrp.hpp>
#include <chrono>
#include <memory>
#include <string>
#include <atomic>

#include "Log.h"
#include "output/SDR.h"
#include "TimestampDecoder.h"
#include "RemoteControl.h"
#include "ThreadsafeQueue.h"

#include <stdio.h>
#include <sys/types.h>

namespace Output {

class USRPTime {
    public:
        USRPTime( uhd::usrp::multi_usrp::sptr usrp,
                SDRDeviceConfig& conf);

        // Verifies the GPSDO state, that the device time is ok.
        // Returns true if all ok.
        // Should be called more often than the gps_fix_check_interval
        bool verify_time(void);

        // Wait time in seconds to get fix
        static const int initial_gps_fix_wait = 180;

        // Interval for checking the GPS at runtime
        static constexpr double gps_fix_check_interval = 10.0; // seconds

    private:
        enum class gps_state_e {
            /* At startup, the LEA-M8F GPSDO gets issued a hotstart request to
             * make sure we will not sync time on a PPS edge that is generated
             * while the GPSDO is in holdover. In the bootup state, we wait for
             * the first PPS after hotstart, and then sync time.
             */
            bootup,

            /* Once the system is up, we check lock every now and then. If the
             * fix is lost for too long, we crash.
             */
            monitor_fix,
        };

        void check_gps();

        uhd::usrp::multi_usrp::sptr m_usrp;
        SDRDeviceConfig& m_conf;

        gps_state_e gps_state = gps_state_e::bootup;
        int num_checks_without_gps_fix = 1;

        using timepoint_t = std::chrono::time_point<std::chrono::steady_clock>;
        timepoint_t time_last_check;

        boost::packaged_task<bool> gps_fix_pt;
        boost::unique_future<bool> gps_fix_future;
        boost::thread gps_fix_task;

        // Returns true if we want to check for the gps_timelock sensor
        bool gpsfix_needs_check(void) const;

        // Return true if the gpsdo is from ettus, false if it is the ODR
        // LEA-M8F board is used
        bool gpsdo_is_ettus(void) const;

        void set_usrp_time_from_localtime(void);
        void set_usrp_time_from_pps(void);
};

} // namespace Output

#endif // HAVE_OUTPUT_UHD