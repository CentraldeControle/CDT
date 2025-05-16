from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import TimeoutException
import os
from cred import EMAIL, SENHA
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


strUrl = 'https://app.powerbi.com/groups/me/reports/6fbbfd34-7ecf-4a40-bdc4-55910d8bf16e/ReportSectiona45eb931ee53257081e6?ctid=d7be86d0-66c8-4589-8c27-9cf5f31d3a1d&experience=power-bi&clientSideAuth=0'


# *** STEP 01: Abre o browser e carrega a URL 
driver.get(strUrl)

# Espera para garantir que a página carregue
time.sleep(5)

# Encontra a caixa de texto pelo seu ID e digita o email
caixa_email = driver.find_element(By.ID, 'email')
caixa_email.send_keys(f"{EMAIL}")

botao_enviar = driver.find_element(By.ID, 'submitBtn')
botao_enviar.click()

time.sleep(5)

campo_senha = driver.find_element(By.ID, "i0118")
campo_senha.send_keys(f"{SENHA}")

# Encontra o botão pelo seu ID e clica nele
botao_senha = driver.find_element(By.ID, 'idSIButton9')
botao_senha.click()

time.sleep(5)

botao_sim = driver.find_element(By.ID, 'idSIButton9')
botao_sim.click()

time.sleep(10)


elemento_desejado = WebDriverWait(driver, 300).until(
    EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/root/mat-sidenav-container/mat-sidenav-content/tri-shell-panel-outlet/tri-item-renderer-panel/tri-extension-panel-outlet/mat-sidenav-container/mat-sidenav-content/div/div/div[1]/tri-shell/tri-item-renderer/tri-extension-page-outlet/div[2]/report/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[6]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div/div[2]/div/div/div[2]/div/div'))
)

# Instancia um objeto ActionChains
actions = ActionChains(driver)

# Calcula o deslocamento
offset_x = 121  # Deslocamento horizontal;
offset_y = 0    # Deslocamento vertical;

# Clique e segure o elemento, mova para a direita e solte o botão do mouse
actions.click_and_hold(elemento_desejado).move_by_offset(offset_x, offset_y).release().perform()
time.sleep(5)

botao_data = driver.find_element(By.XPATH, "/html/body/div[1]/root/mat-sidenav-container/mat-sidenav-content/tri-shell-panel-outlet/tri-item-renderer-panel/tri-extension-panel-outlet/mat-sidenav-container/mat-sidenav-content/div/div/div[1]/tri-shell/tri-item-renderer/tri-extension-page-outlet/div[2]/report/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[6]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div/div[1]/div/div[1]/div/input")
botao_data.click()
time.sleep(5)

# Supondo que 'driver' já esteja inicializado

botao_seta_xpath = "/html/body/div[2]/div[4]/div/pbi-overlay-calendar/div/pbi-calendar/div/span/span/button[1]/i"
string_Mes_xpath = "/html/body/div[2]/div[4]/div/pbi-overlay-calendar/div/pbi-calendar/div/span/button"

# Espera inicial para garantir que o elemento esteja presente antes de entrar no loop
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, botao_seta_xpath)))

while True:
    try:
        # Localiza o botão a cada iteração
        botao_seta = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, botao_seta_xpath))
        )

        # Localiza o elemento que contém a descrição do mês
        elemento_descricao_mes = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, string_Mes_xpath))
        )

        # Condição de saída do loop
        if "janeiro 2025, alterar mês" in elemento_descricao_mes.get_attribute("aria-label") or "janeiro 2025, alterar mês" in elemento_descricao_mes.get_attribute("aria-description"):
            break

        botao_seta.click()

    except TimeoutException:
        print("TimeoutException capturada. Elemento não encontrado ou condição não atendida no tempo esperado.")
        break  # Ou tente novamente, ajuste conforme necessário
    
botao_dia = WebDriverWait(driver, 100).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[4]/div/pbi-overlay-calendar/div/pbi-calendar/div/div/div/div[2]/div[4]/button"))
)

time.sleep(1)

botao_dia.click()

pesquisas = ['goiania centro norte', 'Formosa', 'caldas novas', 'sao joao da']

campo_pesquisa_xpath = "/html/body/div[1]/root/mat-sidenav-container/mat-sidenav-content/tri-shell-panel-outlet/tri-item-renderer-panel/tri-extension-panel-outlet/mat-sidenav-container/mat-sidenav-content/div/div/div[1]/tri-shell/tri-item-renderer/tri-extension-page-outlet/div[2]/report/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[8]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div"
checkbox_xpath = '/html/body/div[7]/div[1]/div/div[2]/div/div[1]/div/div/div[1]/div/div/span'




for pesquisa in pesquisas:
    # Localizar o campo de pesquisa
    campo_pesquisa = WebDriverWait(driver, 300).until(
        EC.visibility_of_element_located((By.XPATH, campo_pesquisa_xpath))
    )

    
    # Limpar, digitar o texto no campo de pesquisa e enviar
    campo_pesquisa.clear()
    
    campo_pesquisa.send_keys(pesquisa)
    time.sleep(2)  # Substitua por uma espera explícita se necessário
    
    # Localizar o checkbox (se necessário, recarregue este elemento no DOM após cada ação)
    checkbox = WebDriverWait(driver, 100).until(
        EC.visibility_of_element_located((By.XPATH, checkbox_xpath))
    )    
    # Criar uma instância de ActionChains para realizar ações complexas
    actions = ActionChains(driver)
    time.sleep(5)
    
    # Clicar no checkbox enquanto mantém a tecla Ctrl pressionada
    actions.key_down(Keys.CONTROL).click(checkbox).key_up(Keys.CONTROL).perform()
    time.sleep(2)  # Substitua por uma espera explícita se necessário

# Localizar o campo de pesquisa =========================================================================================================================
time.sleep(15)
test2 = driver.find_element(By.XPATH, '/html/body/div[1]/root/mat-sidenav-container/mat-sidenav-content/tri-shell-panel-outlet/tri-item-renderer-panel/tri-extension-panel-outlet/mat-sidenav-container/mat-sidenav-content/div/div/div[1]/tri-shell/tri-item-renderer/tri-extension-page-outlet/div[2]/report/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[19]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[4]')
test2.click()
time.sleep(2)
test = driver.find_element(By.XPATH, '/html/body/div[1]/root/mat-sidenav-container/mat-sidenav-content/tri-shell-panel-outlet/tri-item-renderer-panel/tri-extension-panel-outlet/mat-sidenav-container/mat-sidenav-content/div/div/div[1]/tri-shell/tri-item-renderer/tri-extension-page-outlet/div[2]/report/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[19]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button/i')
test.click()
time.sleep(2)
test3 = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/ng-component/pbi-menu/button[3]/div')
test3.click()
time.sleep(2)
test4 = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/mat-dialog-container/div/div/export-data-dialog/mat-dialog-actions/button[1]')
test4.click()

time.sleep(50)


driver.close()