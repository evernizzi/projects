from iqoptionapi.stable_api import IQ_Option
import time
import json
import configparser
from datetime import datetime
from dateutil import tz
import threading

#Developed By @Euller#

arquivo = configparser.RawConfigParser()
arquivo.read('config.txt')
API = IQ_Option(arquivo.get('GERAL', 'email'), arquivo.get('GERAL', 'senha'))
API.set_max_reconnect(5)
API.change_balance('PRACTICE')  # PRACTICE / REAL

while True:
    if API.check_connect() == False:
        print('Erro ao se conectar')
        API.reconnect()
    else:
        print('Conectado com sucesso')
        break

    time.sleep(1)


def perfil():
    perfil = json.loads(json.dumps(API.get_profile()))
    return perfil['result']
x = perfil()
print(x['first_name'])
print(x['city'])
print(x['currency'],x['currency_char'],x['balance'])



def timestamp_converter(x):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))

    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]


def dia_hora(DATA, HORA):
    day = int(time.localtime().tm_mday)
    mon = int(time.localtime().tm_mon)
    hora = int(time.localtime().tm_hour)
    min = int(time.localtime().tm_min)
    seg = int(time.localtime().tm_sec)
    if day < 10:
        day = '0' + str(day)
    if mon < 10:
        mon = '0' + str(mon)
    if hora < 10:
        hora = '0' + str(hora)
    if min < 10:
        min = '0' + str(min)
    if seg < 10:
        seg = '0' + str(seg)   
         
    d = str(day) + '/' + str(mon) + '/' + str(time.localtime().tm_year) + '|' + str(hora) + ':' + str(min) + ':' + str(seg)
    f = str(DATA) + '|' + str(HORA) + ':00'
    if d == f :
        return True
    else:
        return False



def payout(par, tipo, timeframe = 1):
  if tipo == 'turbo':
    a = API.get_all_profit()
    return int(100 * a[par]['turbo'])

  elif tipo == 'digital':

    API.subscribe_strike_list(par, timeframe)
    while True:
      d = API.get_digital_current_profit(par, timeframe)
      if d != False:
        d = int(d)
        break
      time.sleep(1)
    API.unsubscribe_strike_list(par, timeframe)
    return d

par = API.get_all_open_time()

for paridade in par['turbo']:
  if par['turbo'][paridade]['open'] == True:
    print('[ TURBO ]: '+paridade+' | Payout: '+str(payout(paridade, 'turbo')))

print('\n')

for paridade in par['digital']:
  if par['digital'][paridade]['open'] == True:
    print('[ DIGITAL ]: '+paridade+' | Payout: '+str( payout(paridade, 'digital') ))

print('\n')



def configuracao():
    arquivo = configparser.RawConfigParser()
    arquivo.read('config.txt')

    return {'valor_entrada': arquivo.get('GERAL', 'entrada'),'qnt_gale':arquivo.get('GERAL', 'qnt_gale'),'fator_gale': arquivo.get('GERAL', 'fator_gale'), 'timeframe': arquivo.get('GERAL', 'timeframe')}


conf = configuracao()


def carregar_sinais():
    arquivo = open('sinais.txt', encoding='UTF-8')
    lista = arquivo.read()
    arquivo.close

    lista = lista.split('\n')

    for index, a in enumerate(lista):
        if a == '':
            del lista[index]

    return lista


def entrada_martingale(API, par, entrada, direcao, timeframe):
    id = API.buy_digital_spot(par, entrada, direcao, timeframe)
    if id == None:
        print('Não foi possível fazer a entrada...')
        return id
    return id


qnt_gale = int(conf['qnt_gale'])

cont = 1 #controle de gale

def status_entrada(id, API, par, entrada, direcao, timeframe, fator_gale, loop=True):
    global cont, qnt_gale
    while loop:
            if id != None:
                status, lucro = API.check_win_digital_v2(id)
                print('Cont',cont,'Status',status,'ID',id)
                if status:
                    if lucro > 0:
                        print('RESULTADO: WIN / LUCRO:  ' + str(round(lucro, 2)))
                        id = None
                        loop = False
                    elif lucro < 0 and cont > qnt_gale:
                        print('RESULTADO: HIT / LUCRO:  ' + str(entrada))
                        loop = False
                    elif lucro < 0 and cont <= qnt_gale:
                        print('RESULTADO: LOSS / LUCRO:  ' + str(entrada))
                        
                        entrada = entrada * fator_gale
                        print('Entrada.',entrada,'Fator gale',fator_gale)
                        print('Mart', par, entrada, direcao, timeframe)
                        id = entrada_martingale(API, par, entrada, direcao.lower(), timeframe)
                        cont = cont + 1  # Conta Loss, serve de controle do gale
                        
            time.sleep(1)        
    


print('\n\n')


#         # Entradas na digital

while True:
    lista = carregar_sinais() # assim quando atualizar lista pega as atualizações
    print('Procurando Oportunidade...',datetime.now().second)
    c = 0
    for sinal in lista:
        dados = sinal.split(',')
        d1 = dados[0]
        d2 = dados[1]
        d3 = dados[2]
        d4 = dados[3]
        #rint(d1, d2, d3, d4)
        dia = dados[0]
        hora = dados[1]
        par = dados[2]
        direcao = dados[3]
        entrada = float(conf['valor_entrada'])
        fator_gale = float(conf['fator_gale'])
        timeframe = 1
        # Entradas na digital

        #print('Esperando Entrada')
        if dia_hora(dia, hora):
            print('ENTRADA', sinal)
            lista.remove(lista[c])
            id = API.buy_digital_spot(par, entrada, direcao.lower(), timeframe) # direção caixa baixa
            if id == 'error':
                c += 1
                continue

            if isinstance(id, int):
                threading.Thread(target=status_entrada, args=(id, API, par, entrada, direcao, timeframe,fator_gale)).start()
        c += 1
    time.sleep(1)
