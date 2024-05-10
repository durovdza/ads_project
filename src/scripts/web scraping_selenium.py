from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Browser-Optionen und WebDriver initialisieren
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Für den Headless-Modus
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigiere zur spezifischen Seite
    driver.get('https://www.jobs.ch/de/lohn/kanton/?canton=zh')

    # Finde alle Karten, die die Berufe und Gehälter darstellen
    job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.Grid-sc-18fqrjd-0 > div')

    # Durchlaufe jede Karte und extrahiere die benötigten Informationen
    for card in job_cards:
        job_title = card.find_element(By.CSS_SELECTOR, 'h3').text.strip()
        salary_info = card.find_element(By.CSS_SELECTOR, 'p').text.strip().split('\n')
        num_salary_reports = salary_info[0]  # Anzahl der Lohnangaben
        average_salary = salary_info[1]  # Durchschnittsgehalt

        print(f"Beruf: {job_title}, Anzahl Lohnangaben: {num_salary_reports}, Durchschnittsgehalt: {average_salary}")

finally:
    # Stelle sicher, dass der Browser geschlossen wird
    driver.quit()
