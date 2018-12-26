# -*- coding: utf-8 -*-
'''
A library of miscellaneous functions for meteorological data processing.
    
Miscellaneous functions
-----------------------

    - event2time: Convert (event) based measurements into equidistant\
    time spaced data for a selected interval
    - date2doy: Calculates day of year from day, month and year data.

The module requires and imports scipy and datetime modules.
Tested for compatibility with Python 2.7.3.

Function descriptions
=====================

'''

__author__ = "Maarten J. Waterloo <maarten.waterloo@acaciawater.com> and\
 J. Delsman"
__version__ = "1.0"
__release__ = "1.0.1"
__date__ = "November 2014"

import datetime
import scipy


def date2doy(dd=scipy.array([]),\
    mm=scipy.array([]),\
    yyyy=scipy.array([])):
    '''
    Function to calculate the julian day (day of year) from day,
    month and year.
        
    Parameters:
        - dd: (array of) day of month
        - mm: (array of) month
        - yyyy: (array of) year
        
    Returns:
        - jd: (array of) julian day of year
        
    Examples
    --------
    
        >>> date2doy(04,11,2006)
        308
        >>> date2doy(04,11,2008)
        309
        >>> day=[10,10,10]
        >>> month=[1,2,3]
        >>> year=[2007,2008,2009]
        >>> date2doy(day,month,year)
        array([ 10.,  41.,  69.])
        >>>
        
    '''
    # Determine length of array
    n = scipy.size(dd)
    if n < 2:   # Dealing with single value...date2doy
        # Determine julian day     
        doy = scipy.floor(275 * mm / 9 - 30 + dd) - 2
        if mm < 3:
            doy = doy + 2
        # Correct for leap years
        if (scipy.mod(yyyy / 4.0, 1) == 0.0 and scipy.mod(yyyy / 100.0, 1) != 0.0)\
        or scipy.mod(yyyy / 400.0, 1) == 0.0:
            if mm > 2:
                doy = doy + 1
        doy = int(doy)
    else:   # Dealing with an array
        # Initiate the output array  
        doy = scipy.zeros(n)
        # Calculate julian days   
        for i in range(0, n):
            doy[i] = scipy.floor(275 * mm[i] / 9 - 30 + dd[i]) - 2
            if mm[i] < 3:
                doy[i] = doy[i] + 2
            # Correct for leap years
            if (scipy.mod(yyyy[i] / 4.0, 1) == 0.0 and scipy.mod(yyyy[i] / 100.0, 1)\
            != 0.0) or scipy.mod(yyyy[i] / 400.0, 1) == 0.0:
                if mm[i] > 2:
                    doy[i] = doy[i] + 1
            doy[i] = int(doy[i])
    return doy # Julian day [integer]


def event2time(yyyy=scipy.array([]), doytime=scipy.array([]), \
               X=scipy.array([]), method=str, interval=None):
    '''
    Function to convert (event-based) time series data to equidistant time
    spaced data at a specified interval.

    The maximum interval for processing is 86400 s, resulting in daily
    values. You can choose to sum (e.g. for event-based rainfall
    measurements) or average the input data over a given time interval.
    If you choose to average, a -9999 value (missing value) will be output
    if there are no data in the specified interval. For summation, a zero
    will be output, as required for event-based rainfall measurements.

    Parameters:
        - yyyy: Array of year values (e.g. 2008)
        - doytime: Array of day of year (doy, 1-366) with decimal time\
        values (0-1) (e.g. 133.4375).
        - X: Array of data values (e.g. 0.2). for event-based\
        precipitation data, data should be zero at start and end\
        times of the event data record.
        - method: Enter `sum` to sum data (e.g. precipitation), and\
        `avg` to average data over the selected time interval.
        - interval: Optional: interval in seconds (integer value,\
        e.g. 900 for a 15-minute interval). A default value of 1800 s is\
        assumed when interval is not specified as a function argument.
    
    Returns:
        - YEAR: Array of year.
        - DOY_TIME: Array of day of year (1-366) + decimal time values\
        (0-1), e.g. 153.5 for noon on day 153.
        - Y: Array of corresponding summed or averaged data values, where\
        -9999 indicates missing values when `avg` is selected and 0 when\
        `sum` is selected.

    Examples
    --------    
        >>> year=[2008,2008,2008]
        >>> daytime=[153.5,153.9,154.1]
        >>> vals=[0,0.4,2.]
        >>> event2time(year,daytime,vals,'sum',3600)
        (array([2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008,
               2008, 2008]), array([ 153.58333333,  153.625     ,  153.66666667,  153.70833333,
                153.75      ,  153.79166667,  153.83333333,  153.875     ,
                153.91666667,  153.95833333,  154.        ,  154.04166667,
                154.08333333]), array([ 0.4,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  2. ,  0. ,  0. ,
                0. ,  0. ]))
        >>> yr,day_time,sum_P = event2time(year,daytime,vals,'sum',3600)
        >>> yr
        array([2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008, 2008,
               2008, 2008])
        >>> sum_P
        array([ 0.4,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  2. ,  0. ,  0. ,
                0. ,  0. ])
        
    '''

    # Check for correct method input
    if method != 'sum':
        if method != 'avg':
            print('WARNING: method input unknown - set to default \'sum\'! \n')
            method = 'sum'
    
    # Provide default interval of 1800 seconds if not given as argument
    if interval is None:
        interval = 1800

    # Do not accept intervals larger than 84600 s (one day)
    if interval > 86400:
        print 'WARNING: event2time(): Interval > 86400 s not accepted.'
        print 'INTERVAL SET TO 86400 s (ONE DAY).\n'
        interval = 86400

    # Determine the start datetime of the new time series
    # Evaluate start time (first value in arrays)
    # First convert time of day to seconds
    startsecond = scipy.mod(doytime[0], 1) * 86400
    
    # Check what time the first interval in the regular time series would be
    starttime = scipy.floor(startsecond / interval) * interval
    # Increase to end of interval if it is not exceeding one day (86400 s)
    if interval < 86400:
        starttime = starttime + interval 
    
    # Make sure to start on the day of installation
    if starttime > 86400:
        starttime = 86400
        print 'WARNING: interval exceeds past midnight of first day'
        print 'Start set to midnight of first day'
    start = starttime / 86400 + scipy.floor(doytime[0])
    
    # Determine end time
    endsecond = scipy.mod(doytime[len(doytime) - 1], 1) * 86400
    
    # Endtime is last full interval before the end of record
    endtime = scipy.floor(endsecond / interval) * interval
    end = endtime / 86400 + scipy.floor(doytime[len(doytime) - 1])
    
    # Determine start date and time, including year
    startdate = datetime.datetime(int(yyyy[0]), 1, 1, 0, 0, 0) + \
                datetime.timedelta(days= scipy.floor(start) - 1, \
                seconds=scipy.mod(start, 1) * 86400)
    
    # Determine the end date and time of time series
    enddate = datetime.datetime(int(yyyy[len(yyyy) - 1]), 1, 1, 0, 0, 0) + \
              datetime.timedelta(days=scipy.floor(end) - 1, \
              seconds=scipy.mod(end, 1) * 86400)
    
    # Create arrays for storing the equidistant time output
    YEAR = []
    DECTIME = []
    Y = []
    
    # Set initial date/time value to first date/time interval
    intervaldate = startdate
    
    # Set counters to zero
    i = 0 # desired time-index value counter
    j = 0 # event data index counter
    counter = 0 # counts events in one time interval
    
    # Set initial data value sum to zero
    processedY = 0
    
    # Start data processing  
    while intervaldate < enddate:
        i = i + 1
        # checkdate is event based date/time
        checkdate = datetime.datetime(int(yyyy[j]), 1, 1, 0, 0, 0) + \
                    datetime.timedelta(days=scipy.floor(doytime[j]) - 1, \
                    seconds=scipy.mod(doytime[j], 1) * 86400)
        # intervaldate is the date/time at regular interval
        intervaldate = intervaldate + datetime.timedelta(seconds=interval)
        # If the statement below is true, we have event(s)
        while checkdate < intervaldate:
            counter = counter + 1
            j = j + 1
            checkdate = datetime.datetime(int(yyyy[j]), 1, 1, 0, 0, 0) + \
                        datetime.timedelta(days=scipy.floor(doytime[j]) - 1, \
                        seconds=scipy.mod(doytime[j], 1) * 86400)
            processedY = processedY + X[j]
        # Append the time spaced data to the lists
        YEAR.append(intervaldate.year)
        # Recalculate to doy.decimaltime format
        dtime = (int(intervaldate.strftime("%j")) + \
                  (int(intervaldate.strftime("%H")) * 3600 + \
                   int(intervaldate.strftime("%M")) * 60 + \
                   int(intervaldate.strftime("%S"))) / 86400.0)
        # Correct of error in day when interval is 86400 s
        # This because new day starts at midnight, but processed data
        # covers previous day ending at midnight
        if interval == 86400:
            dtime = dtime - 1
        DECTIME.append(dtime)
        if method=='sum':
            Y.append(processedY)
        if method=='avg':
            # In case there are missing data in the interval, division by zero
            # could occur while averaging. In this case we indicate missing data
            # by -9999  
            if counter==0:
                counter=1.
                processedY=-9999
            Y.append(processedY/counter) 
        # Set processedY and counter to zero for next event
        processedY = 0
        counter = 0
        
    # Convert lists to arrays and output these arrays
    YEAR = scipy.array(YEAR)
    DECTIME = scipy.array(DECTIME)
    Y = scipy.array(Y)
    
    # Return year, doy.decimaltime and datavalue as output
    return YEAR, DECTIME, Y


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print 'Ran all tests...'