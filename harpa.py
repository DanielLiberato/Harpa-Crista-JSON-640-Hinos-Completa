from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pprint
import time
from selenium.common.exceptions import TimeoutException

servico = Service(ChromeDriverManager().install())

# Configuração do Selenium WebDriver
driver = webdriver.Chrome(service=servico)

base_url = "https://www.coloqueositedaharpaaqui.com.br"
main_url = base_url + "/hino/1-chuvas-de-graca"
driver.get(main_url)

louvores = []
countLouvor = 1
data = {}

while True:    
    try:
        coro_hino = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div/div/div/main/div[3]/div/div/div[2]/blockquote'))
        )
        
        texto_coro_hino = coro_hino.text
    except TimeoutException:
        texto_coro_hino = ""

    # remover o coro se houver da pagina.
    driver.execute_script("var elementos = document.getElementsByTagName('blockquote'); for (var i = elementos.length - 1; i >= 0; i--) { elementos[i].remove(); }")

    elementos_louvor = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div/div/div/main/div[3]/div/div'))
    )
    
    texto_louvores = elementos_louvor.text
    # Dividir o texto em louvores (separados por números)
    louvores = [louvor.strip() for louvor in texto_louvores.split('\n') if louvor.strip()]

    current_title = "0"
    current_content = []
    for louvor in louvores:
        if louvor.isdigit():
            # Novo verso
            current_title = louvor
            current_content = []
        else:
            if not ("Tradutor" in louvor or "***" in louvor):
                if current_title == "0":
                    if countLouvor not in data:
                        data[countLouvor] = {}
                    data[countLouvor]['hino'] = louvor
                    data[countLouvor]['coro'] = texto_coro_hino
                else:    
                    current_content.append(louvor)
                    if 'verses' not in data[countLouvor]:
                        data[countLouvor]['verses'] = {}
                        
                    data[countLouvor]['verses'][current_title] = " <br> ".join(current_content)
            
                    
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div/div/div/main/div[4]/div/button[3]'))
        )
    except TimeoutException:
        break
    
    if not next_button.is_enabled():
        break
    
    # Clicar no botão usando JavaScript
    driver.execute_script("arguments[0].click();", next_button)
    
    # aguarde 5 segundos
    time.sleep(5)
    
    if countLouvor == 640:
        break
    
    countLouvor += 1


# Converter em JSON
#json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Imprimir o JSON
#print(json_data)

# Converter em JSON
json_filename = "harpa_crista_640_hinos.json"  # Nome do arquivo JSON
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print(f"Os dados foram salvos em '{json_filename}'.")

# Feche o navegador
driver.quit()