##################################
#  DTpyWeb 1.0 Config File
# @author r00tme
# @version 1.04
# @date 27/02/2019
###################################
# Windows Drivers Reference
# {SQL Server} - released with SQL Server 2000
# {SQL Native Client} - released with SQL Server 2005 (also known as version 9.0)
# {SQL Server Native Client 10.0} - released with SQL Server 2008
# {SQL Server Native Client 11.0} - released with SQL Server 2012
# {ODBC Driver 11 for SQL Server} - supports SQL Server 2005 through 2014
# {ODBC Driver 13 for SQL Server} - supports SQL Server 2005 through 2016
# {ODBC Driver 13.1 for SQL Server} - supports SQL Server 2008 through 2016
# {ODBC Driver 17 for SQL Server} - supports SQL Server 2008 through 2017
##################################

SQL_DRIVER = "{SQL Server}"  # Drivers
SQL_SERVER = ""  # Server Version
SQL_USER = ""  # Server Username
SQL_PASS = ""  # Server Password
SQL_DBASE = "MuOnline"  # Database Name
SQL_PORT = "1433"  # Server Port

Server_Name = "DTpyWeb"  # Server Name
Secret_Key = "32G23#@F@#$@!!$:SALL"  # Web Secret Key
Web_Debug = True  # This option must be False if the web is underdevelopment
Item_Hex_Len = 20  # Item Hex Length points the Season
Web_IP = '127.0.0.1'  # Default for all IP's including external
Web_Port = 5000  # Default Web-server Port

Web_Theme = "Crystal-Mu"  # Default theme
Theme_Switcher = True  # Show all available themes or the right top corner

# Download Module Links
Dl_Links = \
    [
        # Download Link 1
        'DTpyWeb Full Client,'
        'https://mega.nz/#!ToF1FYYY!kI8l4uSeO9tBjK_X-eB0rjp-jj2Ux776y6O5LcVvfJ4,'
        'mega.co.nz,'
        '512mb, ',

        # Download Link 2
        'DTpyWeb Light Client,'
        'https://mega.nz/#!ToF1FYYY!kI8l4uSeO9tBjK_X-eB0rjp-jj2Ux776y6O5LcVvfJ4,'
        'mega.co.nz,'
        '256mb,'
    ]
