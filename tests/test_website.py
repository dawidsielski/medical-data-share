from selenium import webdriver
from selenium.webdriver.common.keys import Keys


WEBSITE = 'http://127.0.0.1:5000/'

driver = webdriver.Chrome(executable_path='C:\chrome_driver\chromedriver.exe')

driver.get(WEBSITE)
driver.maximize_window()
driver.save_screenshot('tests\\index.png')

runs_tab = driver.find_element_by_id('runs')
runs_tab.click()
driver.save_screenshot('tests\\runs.png')

samples_tab = driver.find_element_by_id('samples')
samples_tab.click()
driver.save_screenshot('tests\\samples.png')

samples_tab = driver.find_element_by_id('genes')
samples_tab.click()
driver.save_screenshot('tests\\genes.png')

samples_tab = driver.find_element_by_id('variants')
samples_tab.click()
driver.save_screenshot('tests\\variants.png')

driver.close()
