import coverage

directory = "./htmlcov"
coverage_instance = coverage.coverage(data_file="coverage_file.", auto_data=True)
coverage_instance.load()

coverage_instance.exclude("^import")
coverage_instance.exclude("from.*import")
coverage_instance.combine()

coverage_instance.html_report(morfs=None, directory=directory, ignore_errors=False)
