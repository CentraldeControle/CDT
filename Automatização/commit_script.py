from git import Repo

# Define o caminho do seu repositório Git local
repo_path = 'C:/Users/PC/Documents/CDT/CDT'

# Inicializa o objeto Repo no diretório especificado
repo = Repo(repo_path)

# Verifica se o repositório tem alguma mudança
if repo.is_dirty(untracked_files=True):
    # Adiciona todos os arquivos modificados ao stage
    repo.git.add(A=True)
    
    # Commita as alterações com uma mensagem
    repo.git.commit('-m', 'Commit automático via script Python')
    
    print("Mudanças commitadas com sucesso!")
    
    # Realiza o push das mudanças para o repositório remoto
    repo.remotes.origin.push()
    
    print("Push realizado com sucesso.")
    
else:
    print("Nenhuma mudança para commitar.")
    
    
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os


from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options



# Instalando o ChromeDriver e obtendo o caminho correto
chromedriver_path = ChromeDriverManager().install()

# Configurações do ChromeOptions
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Corrigindo o caminho do ChromeDriver
# Obtendo apenas o diretório onde o ChromeDriver foi instalado
chromedriver_dir = os.path.dirname(chromedriver_path)
# Construindo o caminho completo para o executável
chromedriver_executable = os.path.join(chromedriver_dir, 'chromedriver.exe')


# Inicializando o WebDriver
service = Service(chromedriver_executable)
driver = webdriver.Chrome(service=service, options=chrome_options)


strUrl = 'https://dash-cdt.streamlit.app'






########################################################### Print dos Graficos #############################################################





# *** STEP 01: Abre o browser e carrega a URL 
driver.get(strUrl)
driver.execute_cdp_cmd('Emulation.setPageScaleFactor', {'pageScaleFactor': 0.8})
# Maximiza a janela do navegador
driver.maximize_window()

time.sleep(40)

# Espera o iframe estar disponível
WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div:nth-child(1) > div > div > iframe')))

# Muda o foco para o iframe
iframe = driver.find_element(By.CSS_SELECTOR, '#root > div:nth-child(1) > div > div > iframe')
driver.switch_to.frame(iframe)


time.sleep(10)
grafico1 = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > section.stMain.st-emotion-cache-bm2z3a.en45cdb1 > div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.en45cdb4 > div > div > div:nth-child(2) > div:nth-child(1) > div > div > div > div > div > div > div > div"))
)
grafico1.screenshot('1vendas-franquias-mes.png') 

time.sleep(2)

grafico2 = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > section.stMain.st-emotion-cache-bm2z3a.en45cdb1 > div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.en45cdb4 > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div > div > div > div"))
)
grafico2.screenshot('2media-diaria-franquias.png')   

time.sleep(2)

grafico4 = WebDriverWait(driver, 3000).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > section.stMain.st-emotion-cache-bm2z3a.en45cdb1 > div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.en45cdb4 > div > div > div:nth-child(11) > div > div > div > div > div"))
)
grafico4.screenshot('4motivo-desfiliacao.png')

grafico3 = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > section.stMain.st-emotion-cache-bm2z3a.en45cdb1 > div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.en45cdb4 > div > div > div:nth-child(4)"))
)
grafico3.screenshot('3projeção-franquias.png')

time.sleep(2)



#grafico5 = WebDriverWait(driver, 30).until(
#    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.st-emotion-cache-bm2z3a.ea3mdgi8 > div.block-container.st-emotion-cache-1jicfl2.ea3mdgi5 > div > div > div > div:nth-child(7) > div > div"))
#)
#grafico5.screenshot('5motivo-desfiliacao.png')

#time.sleep(2)

#grafico6 = WebDriverWait(driver, 30).until(
#    EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.st-emotion-cache-bm2z3a.ea3mdgi8 > div.block-container.st-emotion-cache-1jicfl2.ea3mdgi5 > div > div > div > div:nth-child(9) > div > div > div > div"))
#)
#grafico6.screenshot('6previsao_desfiliacao.png')


print("Screenshot dos elementos gráficos salvos.")


#driver.quit()

