import requests
import pandas as pd

# enter your API key here
# you can generate an API key at this URL: https://www.rescuetime.com/anapi/manage
api_key = ""

# change this for each year you want to export
year = "2017"

# This is used as a cutoff limit for both subcategories and for individual activities
# Experiment with different cutoff times to find out what works best for your data.
# If there are too many activities it is hard to read the snakey diagram

# One hours in seconds (3600) times the number of hours you want the cutoff to be. 
min_cutoff_time = 3600 * 5

# You can export the subcategory data from this link: https://www.rescuetime.com/browse/categories/by/rank/for/the/year/of/2014-01-01
# You will need to export it for each year that you are doing. Just store the exported file in your working directory. 
# The file should be named: "RescueTime_Report_All_Categories__2014-01-01.csv"

# finally open up an ipython terminal and copy/paste this entire file

# If you want to change the colors assigned to each category you can edit them here
category_colors = {
	#green
	"Business" : "#40A940",
	'Communication & Scheduling': "#A2E295",

	#Purple
	'Software Development': "#9F76C4",
	'Design & Composition': "#CAB9DA",

	#Teal
	'Reference & Learning': "#3EC5D4",
	
	#Orange
	'Entertainment': "#FF8C35",
	'News & Opinion': "#FFC386",

	#Red
	'Shopping': "#FFA3A0",
	'Social Networking': "#DC4141",

	#Grey
	'Uncategorized': "#8C8C8C",

	#Brown
	'Utilities': "#97675C",

}




query_url = ("https://www.rescuetime.com/anapi/data?key=%s&perspective=rank&restrict_kind=activity&restrict_begin=%s-01-01&restrict_end=%s-12-31&format=json" % (api_key, year, year))

data = requests.get(query_url)

json_data = data.json()

activities_df = pd.DataFrame(json_data['rows'])

activities_df.columns = json_data['row_headers']


#['Rank', 'Time Spent (seconds)', 'Time Spent (HH:MM:SS)', 'Number of People', 'Overview', 'Category']
subcategories_df = pd.read_csv('RescueTime_Report_All_Categories__%s-01-01.csv' % year)

total_time = subcategories_df["Time Spent (seconds)"].sum()


# time for each category and subcategory
category_titles = subcategories_df.Overview.unique()

category_times = {}

for category in category_titles:
	one_category = subcategories_df[subcategories_df['Overview'] == category]
	one_time = one_category["Time Spent (seconds)"].sum()

	category_times.update({category : one_time})


# dataframe that has the subcat time and the parent category
cutoff_subcats = subcategories_df[subcategories_df["Time Spent (seconds)"] > min_cutoff_time]


#From	To (activity)	Amount (hours)	Snakey Format
master_columns = ['From', 'To', 'Time', 'Color', 'Snakey']
master_df = pd.DataFrame(columns=master_columns)


total_df = pd.DataFrame([["", ("%s Computer Time in Hours" % year), total_time, None, None]], columns=master_columns)
master_df = master_df.append(total_df, ignore_index=True)

for each in category_times:
	category_df = pd.DataFrame([[("%s Computer Time in Hours" % year), each, category_times[each], None, None]], columns=master_columns)
	master_df = master_df.append(category_df, ignore_index=True)

for index, row in cutoff_subcats.iterrows():
	sub_df = pd.DataFrame([[row["Overview"], row["Category"], row["Time Spent (seconds)"], category_colors.get(row["Overview"]), None]], columns=master_columns)
	master_df = master_df.append(sub_df, ignore_index=True)

hundred_hours_df = activities_df[activities_df["Time Spent (seconds)"] > min_cutoff_time]

for index, row in hundred_hours_df.iterrows():
	activity_df = pd.DataFrame([[row["Category"], row["Activity"], row["Time Spent (seconds)"], None, None]], columns=master_columns)
	master_df = master_df.append(activity_df, ignore_index=True)



for index, row in master_df.iterrows():
	hours = " [" + str(round(row['Time'] / 3600)) + "] " 
	snakey = row["From"] + hours + row['To']

	# rescuetime names the category level and subcategory level the same thing "Uncategorized" which causes an error in Snakey
	if row['From'] == 'Uncategorized':
		snakey = snakey + " " + "Time"

	row['Snakey'] = snakey


print("Here are the color codes for %s subcategories. Copy and paste into the SnakeyMATIC inputs." % year)
for index, row in cutoff_subcats.iterrows():
	color = category_colors.get(row["Overview"])
	print(":" + row["Category"] + " " + color)



master_df.to_csv(('%s rescuetime activites export.csv' % year), index = False)