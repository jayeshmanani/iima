# IIM Ahmedabad - Website for Data Analysis
This Repo contains the projects done at IIM Ahmedabad. 

Link to the GitHub Repo: https://github.com/jayeshmanani/iima

If you can't see this instruction properly on your local pc/laptop please follow the link for view instruction properly: https://github.com/jayeshmanani/iima/blob/main/README.md

- The main project is inside the data_website folder. It is made using Django framework. You can run it after installing the dependencies use this command to run the project.

python manage.py runserver

## Follow Instruction after here for first time Setup

### Instruction for Beginners for start the WebApp in Windows based PC (first time setup only)

First Setup Python in your Windows PC using the instructions as follows: https://realpython.com/installing-python/

Steps to Start the Project 
***
1) First download the whole folder from google drive into your Desktop or Downloads or Documents

2) Open Command Prompt/CMD

3) Move to the folder location using cd command and verify you are in the right place

Example: If you have download and moved the downloaded folder in the Desktop then use following command in cmd 

i) cd Desktop/final_web_code

After using the above command you can use the command to see other files in that directory

ii) dir

You can see other files and folder inside the final_web_code directory named 

a) data_website, 
b) requirements.txt, 
c) README.md,
d) instruction.txt

Now, You have succesfully verified that you are in the right directory.

4) After verifying the right directory. You have to install the python dependencies by using this command in cmd

pip install -r requirements.txt 

5) After successful installation move to data_website directory using command in cmd

cd data_website

6) after moving to the data_website directory, verify you are in the correct directory using command

dir

7) After using the above command you can see some of the folders and manage.py file, If you can see this file then you are in the right directory.

8) After moving to that directory, run the following command to start the website

python manage.py runserver

9) After running the above command you can see it will start the website, and you have to just go to chrome browser for viewing the website.
and type the address http://localhost:8000/ or http://127.0.0.1:8000/

and you can access the website.

### If you followed till here and can see the website and data successfully, you have managed to setup the website successfully.
***
## After successful setup you don't have to follow above instruction each and every time, You just have to follow the instruction given below for start the website.

1) Move to the directory where you have final_web_code stored.

2) then move to the data_website folder

3) use the command given below and access the website using the given address:

command: 

python manage.py runserver

address:

1) http://localhost:8000/ 
2) http://127.0.0.1:8000/

***
***
***
***
***

### About the Website, Where the data is coming from and where the data is being stored
***
1)There are various data which is being fetched from various websites of worldbank api, dbnomics api 

list of variables which is being fetched from sources like

This five variables are being fetched using dbnomics api using python library: DBnomics, for more information visit https://pypi.org/project/DBnomics/

1) General government net lending/borrowing - GGXCNL_NGDP
2) General government gross debt - GGXWDG_NGDP
3) Gross national savings	= NGSD_NGDP
4) Inflation, average consumer prices	- PCPIPCH
5) Volume of exports of goods and services - TX_RPCH

This Eleven variables are being fetched from Worldbank API. For more information visit: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation

7) External debt stocks, total (DOD, current US$) - DT.DOD.DECT.CD
8) Exports of goods and services (current US$) - NE.EXP.GNFS.CD
9) Total reserves (includes gold, current US$) - FI.RES.TOTL.CD
10) GDP per capita (constant 2010 US$) - NY.GDP.PCAP.KD
11) Imports of goods and services (current US$) - NE.IMP.GNFS.CD
12) GDP growth (annual %) - NY.GDP.MKTP.KD.ZG
13) GNI per capita (constant 2010 US$) - NY.GNP.PCAP.KD
14) GDP (current US$) - NY.GDP.MKTP.CD
15) Political Stability Estimate - PV.EST
16) Rule of Law Estimate - RL.EST
17) Govt Effectiveness Estimate - GE.EST
***
### All the data which is being fetched is stored in the database, in db.sqlite3 file.
***
## Features of the website (How to Use the Website)
### All the data you are viewing is lagging, so, if you select 2020 you will see the data of 2019 and earlier. (If some data is not available in 2019 then it will take data for 2018 - upto one year only)

0) Come back to home page just paste the main link or click on button Risk Index DashBoard

1) You can view the data in table format:

Select: year, Button: View Data

2) You can view the Bar Plot of the data and filter the barplot region wise also. 

Select: Year, Button: View Graph

3) You can view the world map for the data.

First go to view graph then use

Select: Debt Distress/Spec Grade and hit submit

4) You can update the data for particular year for latest year to last five year. (If current year is 2020, you can refresh data for the year from 2015 to 2020)

Select: Year, Button: Refresh Data

5) You can import new data if data is available for the new year, You just have to select the latest year and click on view data, if data is not available it will fetch the data and store it in the database. (If new year suppose 2021 dtaa is not there then if on first day of january if you select the year 2021 then it will fetch the data for the 2020 if it is not already there) 

Select: Year, Button: View Data/Refresh Data/View Graph

6) You can view the pie chart also for the all the country and year, as per your selection. You can check the label name by just clicking on it to hide and view other data in pie chart, if it is very small. (hide the data with big values to see clearly the small data values)

Hit Pie Chart Button

7) Update data, if you don't want to show some of the countries data then use this button, and Set it's value to true/false, True for show data and false for not showing the data

Move to update data section using update data button, 

select: year, country, and set value to true/false and hit update button for setting it's value.
 

8) You can login to admin panel using admin login button. 

Hit Admin Login button

9) You can view the data from the admin panel also, after login to the admin login using credentials given below.

### Login details for admin 
1)  Username - main, 
2) Password - mainuser123



