from bs4 import BeautifulSoup
import requests
from datetime import date

import tabula
import pandas as pd


## TODO: config file
REPORTS_URL = "https://covid19.min-saude.pt/relatorio-de-situacao"
LOCAL_REPORTS_PATH = "E:/Estudos/COVID-19/DGS"
LOCAL_DATA_PATH = "E:/Estudos/COVID-19/covid19-portugal-data"
MUNICIPALITIES_DATA_FILENAME = "time_series_covid19_portugal_confirmados_concelhos"


# GET DGS'S REPORT URL BY DATE
def get_report_url_by_date(day: date):
	page = requests.get(REPORTS_URL)
	if (page.status_code != 200):
		raise Exception("URL not found")

	soup = BeautifulSoup(page.content, 'html.parser')
	links = soup.find_all('a', href=True)

	# date_fmt = day.strftime("%d/%m/%Y")
	date_fmt = day.strftime("%Y%m%d")
	# print(date_fmt)

	for l in links:
		# print(l.contents)
		# print(type(l.contents[0]))

		# if isinstance(content, NavigableString)
		title = str(l.contents[0])

		# if "Relatório de Situação" in title and date_fmt in title:
		# return l['href']
		if date_fmt in l['href']:
			return l['href']

	raise Exception("Report not found")


# GET TODAY'S REPORT URL
def get_today_report_url():
    return get_report_url_by_date(date.today())


# GET FILENAME FROM URL
def get_report_filename_from_url(url):
    return url.split('/')[-1].split('.')[0]


# AUXILIAR FUNCTION TO BUILD PATH GIVEN FOLDER PATH, FILENAME AND EXTENSION
def build_file_path(folder, filename, extension):
    return "{}/{}.{}".format(folder, filename, extension)


# DOWNLOAD DGS'S REPORT, GIVEN THE URL
def download_report(url):
	report_filename = get_report_filename_from_url(url)

	report = requests.get(url)

	path = build_file_path(
		LOCAL_REPORTS_PATH,
		report_filename,
		'pdf'
	)

	with open(path,'wb') as f:
		f.write(report.content)

	return path


# SCRAP MUNICIPALITIES DATA FROM A GIVEN DGS'S REPORT AND SAVE IT TO A CSV
def scrap_municipalities_data_from_report(file_path):
	tables = tabula.read_pdf(
		file_path,
		lattice=True,
		pages='3',
		# encoding='utf-8',
		area = [
			[121.59490909881424, 22.6084762957762, 712.0927309066756, 131.18868030578597],
			[121.59490909881424, 133.41978038818343, 712.0927309066756, 239.76888431579573],
			[121.59490909881424, 241.9999843981932, 712.0927309066756, 349.0927883532713],
			[121.59490909881424, 352.8112884906004, 712.0927309066756, 457.6729923632811],
			[121.59490909881424, 460.64779247314436, 712.0927309066756, 571.4590965655516]
		],
		pandas_options={'header': None}
	)

	full_table = pd.concat(
		[
			tables[0],
			tables[1],
			tables[2],
			tables[3],
			tables[4]
		]
	).reset_index()

	full_table = full_table.rename(
		columns={
			0: "concelho",
			1: "confirmados"
		}
	)

	full_table = full_table.assign(concelho = full_table.concelho.replace(r'\r',  ' ', regex=True))

	full_table = full_table.filter(["concelho", "confirmados"])

	path = build_file_path(
		LOCAL_REPORTS_PATH,
		get_report_filename_from_url(file_path),
		'csv'
	)

	full_table.to_csv(path, encoding='utf-16', index=False)

	return path


def append_new_municipalities_data(new_municipalities_data_path):
	municipalities_data_path = build_file_path(LOCAL_DATA_PATH, MUNICIPALITIES_DATA_FILENAME, "xlsx")

	municipalities_data = pd.read_excel(
		municipalities_data_path,
		dtype={"distrito_ilha": str, "codigo": str}
	)

	municipalities_new_data = pd.read_csv(
		build_file_path(LOCAL_REPORTS_PATH, new_municipalities_data_path, "csv"),
		encoding="utf-16"
	)

	municipalities_data_merged = pd.merge(
		left=municipalities_data,
		right=municipalities_new_data,
		how="left",
		left_on="concelho",
		right_on="concelho",
	).rename(
		columns={
			"confirmados": date.today().strftime("%Y/%m/%d")
		}
	)

	municipalities_data_merged.to_excel(municipalities_data_path, index=False)


def check_new_municipalities_data(new_municipalities_data_path):
	municipalities_data_path = build_file_path(LOCAL_DATA_PATH, MUNICIPALITIES_DATA_FILENAME, "xlsx")

	municipalities_data = pd.read_excel(
		municipalities_data_path,
		dtype={"distrito_ilha": str, "codigo": str}
	)

	last_columns = municipalities_data.T.tail(2).index.values

	recent_municipalities_data = municipalities_data.filter(
		[
			"concelho",
			last_columns[0],
			last_columns[1]
		]
	)
	incongruous_data = recent_municipalities_data.loc[recent_municipalities_data[last_columns[1]].isna()].loc[recent_municipalities_data[last_columns[0]].gt(0)]

	print("Incongruous new data detected for:")
	print(incongruous_data)