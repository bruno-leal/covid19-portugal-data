import utils


print("Getting the URL for the new report...")
today_report_url = utils.get_today_report_url()
print("Done. URL: " + today_report_url)

print("Downloading report...")
today_report_filepath = utils.download_report(today_report_url)
print("Done. Saved to: " + today_report_filepath)

print("Scraping municipalities data from report...")
today_municipalities_data_filepath = utils.scrap_municipalities_data_from_report(today_report_filepath)
print("Done. Saved to: " + today_municipalities_data_filepath)

print("Adding new data to database...")
utils.append_new_municipalities_data(utils.get_report_filename_from_url(today_report_url))
print("Done.")

print("Checking new data for incongruities...")
utils.check_new_municipalities_data(utils.get_report_filename_from_url(today_report_url))
print("Done.")