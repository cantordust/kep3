// Copyright 2023, 2024 Dario Izzo (dario.izzo@gmail.com), Francesco Biscani
// (bluescarni@gmail.com)
//
// This file is part of the kep3 library.
//
// This Source Code Form is subject to the terms of the Mozilla
// Public License v. 2.0. If a copy of the MPL was not distributed
// with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

#ifndef kep3_EPOCH_HPP
#define kep3_EPOCH_HPP

#include <iostream>

#include <chrono>
#include <ctime>
#include <fmt/ostream.h>

#include <kep3/detail/s11n.hpp>
#include <kep3/detail/visibility.hpp>
#include <ratio>
#include <type_traits>

/// Keplerian Toolbox
/**
 * This namespace contains astrodynamics and space flight mechanics routines
 * that are related to keplerian motions or models.
 */
using namespace std::literals;
namespace chr = std::chrono;
using lint = long int;
using llint = long long int;
template <lint Num, lint Den>
using dur = chr::duration<lint, std::ratio<Num, Den>>;

namespace kep3
{

    struct kep_clock : public chr::system_clock
    {
        using rep = int_fast64_t;
        using period = std::ratio<1, 1'000'000>;
        using duration = chr::duration<rep, period>;
        using time_point = chr::time_point<kep_clock, duration>;
        static constexpr bool is_steady = false;
        static constexpr chr::seconds y2k_offset{ 946684800s };

        static constexpr time_point ref_epoch{ kep_clock::time_point{} + y2k_offset };

        static std::time_t to_time_t( const time_point& t ) noexcept
        {
            return static_cast<std::time_t>(
                chr::duration_cast<chr::seconds>( t.time_since_epoch() + y2k_offset )
                    .count() );
        }

        static time_point from_time_t( std::time_t t ) noexcept
        {
            return chr::time_point_cast<duration>(
                time_point( chr::seconds( t ) - y2k_offset ) );
        }
    };

    /// epoch class.
    /**
     * This class defines and contains a non-gregorian date (i.e. a date expressed
     * in julian form). It also provides the user with an interface to boost
     * gregorian dates (see boost documentation at
     * http://www.boost.org/doc/libs/1_42_0/doc/html/date_time.html)
     * using the posix time.
     * The date is defined in MJD2000 (double) as a
     * private member
     *
     * @author Dario Izzo (dario.izzo _AT_ googlemail.com)
     */
    class kep3_DLL_PUBLIC epoch
    {
      public:
        /** Types of non gregorian dates supported. Julian Date (JD) is the number of
         * days passed since January 1, 4713 BC at noon. Modified Julian Date (MJD) is
         * the number of days passed since November 17, 1858 at 00:00 am. The Modified
         * Julian Date 2000 (MJD2000) is the number of days passed since Juanuary 1,
         * 2000 at 00:00am.
         */
        enum class julian_type
        {
            MJD2000,
            MJD,
            JD
        };

        /** Constructors */
        epoch( const double epoch_in = 0.0,
               const julian_type epoch_type = julian_type::MJD2000 );

        template <lint Num, lint Den>
        epoch( const dur<Num, Den>& duration )
            : tp{ kep_clock::time_point{} + duration }
        {
            std::cout << "Constructor const & \n";
        }

        template <lint Num, lint Den>
        epoch( dur<Num, Den>&& duration )
            : tp{ kep_clock::time_point{} + duration }
        {
            std::cout << "Constructor && \n";
        }

        epoch( const kep_clock::time_point& time_point );
        epoch( kep_clock::time_point&& time_point );

        epoch( const int yr, const int mon, const int day, const int hr = 0, const int min = 0, const int s = 0, const int ms = 0, const int us = 0 );

        /** Computing non-gregorian dates */
        [[nodiscard]] kep_clock::time_point mjd2000() const;
        [[nodiscard]] kep_clock::time_point jd() const;
        [[nodiscard]] kep_clock::time_point mjd() const;

        /** Interface to boost::posix_time::ptime */
        //  [[nodiscard]] boost::posix_time::ptime get_posix_time() const;

        static constexpr kep_clock::time_point make_tp( const int yr, const int mon, const int day, const int hr = 0, const int min = 0, const int s = 0, const int ms = 0, const int us = 0 );
        static constexpr kep_clock::time_point make_tp( const double epoch_in, const julian_type epoch_type );

        // Conversions
        // double tp_from_seconds(const double seconds) const;
        static constexpr kep_clock::time_point tp_from_days( const double days );
        //        void set_tp_mjd2000( const double epoch_in );
        //        void set_tp_mjd( const double epoch_in );
        //        void set_tp_jd( const double epoch_in );

        // Duration conversions
        static constexpr double as_sec( kep_clock::duration d )
        {
            return std::chrono::duration<double, std::chrono::seconds::period>( d )
                .count();
        }
        //   double as_days();

        // Printing
        static const char* as_utc_string( const kep_clock::time_point& );
        //   static std::time_t as_gmtime(const kep_clock::time_point &);

        /** operator overloads for sum and diff (epoch-days) and comparison
         * operators
         * **/

        //   std::chrono::seconds day2sec(const double days) const;
        //   kep3_DLL_PUBLIC epoch epoch_from_string(const std::string &date);
        //   kep3_DLL_PUBLIC epoch epoch_from_iso_string(const std::string &date);

        kep3_DLL_PUBLIC friend std::ostream& operator<<( std::ostream& s,
                                                         epoch const& epoch_in );
        template <lint Num, lint Den>
        kep3_DLL_PUBLIC epoch& operator+=( dur<Num, Den>&& duration )
        {
            /* addition of rhs to *this takes place here */
            tp += chr::duration_cast<kep_clock::duration>( duration );
            return *this;
        }
        template <lint Num, lint Den>
        kep3_DLL_PUBLIC epoch& operator-=( dur<Num, Den>&& duration )
        {
            /* addition of rhs to *this takes place here */
            tp -= chr::duration_cast<kep_clock::duration>( duration );
            return *this;
        }

        kep3_DLL_PUBLIC friend bool operator>( const epoch& c1, const epoch& c2 );
        kep3_DLL_PUBLIC friend bool operator<( const epoch& c1, const epoch& c2 );
        kep3_DLL_PUBLIC friend bool operator>=( const epoch& c1, const epoch& c2 );
        kep3_DLL_PUBLIC friend bool operator<=( const epoch& c1, const epoch& c2 );
        kep3_DLL_PUBLIC friend bool operator==( const epoch& c1, const epoch& c2 );
        kep3_DLL_PUBLIC friend bool operator!=( const epoch& c1, const epoch& c2 );
        //        template <lint Num, lint Den>
        //        kep3_DLL_PUBLIC friend epoch operator+( const epoch& lhs, dur<Num, Den>&& rhs );
        //        template <lint Num, lint Den>
        //        kep3_DLL_PUBLIC friend epoch operator-( const epoch& lhs, dur<Num, Den>&& rhs );

        template <lint Num, lint Den>
        kep3_DLL_PUBLIC epoch operator+( dur<Num, Den>&& duration )
        {
            return epoch( tp + chr::duration_cast<kep_clock::duration>( duration ) );
        }
        template <lint Num, lint Den>
        kep3_DLL_PUBLIC epoch operator-( dur<Num, Den>&& duration )
        {
            std::cout << "operator-()\n";
            return epoch( tp - chr::duration_cast<kep_clock::duration>( duration ) );
        }

        kep3_DLL_PUBLIC friend kep_clock::duration operator-( const epoch lhs, const epoch rhs );

        kep3_DLL_PUBLIC epoch operator=( const epoch& ep )
        {
            std::cout << "operator=()\n";
            return { ep.tp };
        }
        //        kep3_DLL_PUBLIC friend epoch& operator=( epoch&& ep );

      private:
        // Serialization code
        friend class boost::serialization::access;
        template <class Archive>
        void serialize( Archive& ar, const unsigned int )
        {
            ar&( *this );
        }
        // Serialization code (END)

        /// the modified julian date 2000 stored in a double
        //        double m_mjd2000;
        kep_clock::time_point tp;
    };

} // end of namespace kep3

template <>
struct fmt::formatter<kep3::epoch> : fmt::ostream_formatter
{
};

#endif // kep3_EPOCH_HPP
