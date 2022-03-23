# from selenium import webdriver
# import string

# PATH = 'C:\Program Files (x86)\chromedriver.exe'
# driver = webdriver.Chrome(PATH)
# template = string.Template('https://www.fantrax.com/newui/EPL/players.go?ltr=${letter}')
# attribs = []

# try:
#     for letter in string.ascii_uppercase[:2]:
#         driver.get(template.safe_substitute(letter = letter))
#         table = driver.find_element_by_class_name('sportsTable')
#         for row in table.find_elements_by_tag_name('tr')[1:]:
#             player_td = row.find_elements_by_tag_name('td')[0]
#             player_a = player_td.find_element_by_tag_name('a')
#             attribs.append(player_a.get_attribute('onclick'))
# finally:
#     driver.close()
# print(attribs)